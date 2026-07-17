"""Business OS API — local + Modal orchestrator entrypoint."""

from __future__ import annotations

import os
from typing import Callable

from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware

from app.agents.executor import run_execution
from app.agents.strategist import run_strategist
from app.config import settings
from app.rag.store import get_store
from app.schemas.plan import (
    ChatRequest,
    ChatResponse,
    ExecuteRequest,
    ExecuteResponse,
    RagHit,
    RagQueryRequest,
    RagQueryResponse,
    Route,
)
from app.security import (
    SECURITY_HEADERS,
    rate_limit,
    validate_chat_request,
    validate_rag_query,
)

app = FastAPI(
    title="Business OS API",
    version="0.4.0",
    description="Hormozi Strategist + Copy + Build orchestration",
    docs_url="/docs" if os.getenv("BIZOS_ENABLE_DOCS", "").lower() in ("1", "true") else None,
    redoc_url=None,
    openapi_url="/openapi.json" if os.getenv("BIZOS_ENABLE_DOCS", "").lower() in ("1", "true") else None,
)

# CORS: explicit allow-list + Vercel preview/prod hostnames for this project
_DEFAULT_ORIGINS = [
    "http://127.0.0.1:5173",
    "http://localhost:5173",
    "https://app.deekshak.site",
    "https://deekshak.site",
    "https://www.deekshak.site",
    "https://business-os-ten-chi.vercel.app",
]
_extra = [o.strip() for o in os.getenv("BIZOS_CORS_ORIGINS", "").split(",") if o.strip()]
ALLOW_ORIGINS = list(dict.fromkeys(_DEFAULT_ORIGINS + _extra))


def _cors_origin_ok(origin: str | None) -> bool:
    if not origin:
        return False
    if origin in ALLOW_ORIGINS:
        return True
    # Any Vercel deployment under this team's project naming
    if origin.endswith(".vercel.app") and "business-os" in origin:
        return True
    return False


app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOW_ORIGINS,
    allow_origin_regex=r"https://business-os[a-z0-9-]*\.vercel\.app",
    allow_credentials=False,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization", "X-Requested-With"],
    max_age=600,
)


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        origin = request.headers.get("origin")
        # Explicit OPTIONS so browsers always get a valid preflight (Modal/ASGI edge cases)
        if request.method == "OPTIONS":
            headers = dict(SECURITY_HEADERS)
            if _cors_origin_ok(origin):
                headers["Access-Control-Allow-Origin"] = origin  # type: ignore[assignment]
                headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
                headers["Access-Control-Allow-Headers"] = (
                    "Content-Type, Authorization, X-Requested-With"
                )
                headers["Access-Control-Max-Age"] = "600"
                headers["Vary"] = "Origin"
            return Response(status_code=204, headers=headers)

        cl = request.headers.get("content-length")
        if cl and cl.isdigit() and int(cl) > 2_000_000:
            return Response("Request body too large", status_code=413)
        response = await call_next(request)
        for k, v in SECURITY_HEADERS.items():
            response.headers.setdefault(k, v)
        if origin and _cors_origin_ok(origin):
            response.headers["Access-Control-Allow-Origin"] = origin
            response.headers["Vary"] = "Origin"
        return response


# SecurityHeaders outer-most after CORS (Starlette: last add = first run)
app.add_middleware(SecurityHeadersMiddleware)


@app.get("/health")
def health():
    llm_on = bool(settings.llm_configured)
    return {
        "ok": True,
        "host": os.getenv("BIZOS_HOST", "local"),
        "version": "0.4.0",
        "llm_configured": llm_on,
        # Alias kept so older frontends don't show "Systems offline"
        "deepseek_configured": llm_on,
        "llm_provider": settings.llm_provider,
        "llm_model": settings.llm_model,
        "deepseek_model": settings.llm_model,
        "endpoints": ["/health", "/rag/query", "/chat", "/execute"],
    }


@app.post("/rag/query", response_model=RagQueryResponse)
def rag_query(req: RagQueryRequest, request: Request):
    rate_limit(request, bucket="rag", limit=40)
    if req.collection not in ("hormozi", "copyos"):
        raise HTTPException(400, "collection must be hormozi or copyos")
    q = validate_rag_query(req.query)
    n = max(1, min(int(req.n_results or 6), 12))
    store = get_store()
    try:
        hits_raw = store.query(
            collection=req.collection,
            query=q,
            n_results=n,
            where=req.where,
        )
    except Exception as e:
        raise HTTPException(500, f"RAG query failed: {e}") from e
    hits = [RagHit(**h) for h in hits_raw]
    return RagQueryResponse(collection=req.collection, hits=hits)


@app.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest, request: Request):
    """Hormozi Strategist: RAG + LLM → reply + Plan JSON."""
    rate_limit(request, bucket="chat", limit=30)
    if not settings.llm_configured:
        raise HTTPException(
            503,
            "LLM API key not configured on the server.",
        )
    message, history = validate_chat_request(req.message, req.history, req.thread_id)
    try:
        result = run_strategist(
            message,
            thread_id=req.thread_id,
            history=history,
        )
    except Exception as e:
        raise HTTPException(500, f"Strategist failed: {e}") from e

    return ChatResponse(
        thread_id=result["thread_id"],
        reply=result["reply"],
        plan=result.get("plan"),
        awaiting_approval=bool(result.get("awaiting_approval")),
        status=str(result.get("status") or "chatting"),
    )


@app.post("/execute", response_model=ExecuteResponse)
def execute(req: ExecuteRequest, request: Request):
    """After plan approval: run Copywriting and/or Builder agents."""
    rate_limit(request, bucket="execute", limit=8)
    if not settings.llm_configured:
        raise HTTPException(503, "LLM API key not configured on the server.")
    if req.route not in (Route.copy, Route.build, Route.both):
        raise HTTPException(400, "route must be copy, build, or both")
    if not req.thread_id or len(req.thread_id) > 80:
        raise HTTPException(400, "invalid thread_id")
    # Bound plan payload size
    try:
        dumped = req.plan.model_dump_json()
    except Exception as e:
        raise HTTPException(400, f"invalid plan: {e}") from e
    if len(dumped) > 120_000:
        raise HTTPException(400, "plan payload too large")
    try:
        return run_execution(
            thread_id=req.thread_id,
            route=req.route,
            plan=req.plan,
        )
    except Exception as e:
        raise HTTPException(500, f"Execution failed: {e}") from e


@app.get("/")
def root():
    return {
        "service": "Business OS API",
        "version": "0.4.0",
        "health": "/health",
        "endpoints": ["/rag/query", "/chat", "/execute"],
    }
