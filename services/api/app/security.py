"""Production-lite security: rate limits, input bounds, prompt-injection guards."""

from __future__ import annotations

import re
import time
from collections import defaultdict, deque
from threading import Lock
from typing import Deque

from fastapi import HTTPException, Request

# —— Limits (demo free tier — raise later with auth/credits) ——
MAX_MESSAGE_CHARS = 6_000
MAX_HISTORY_MESSAGES = 24
MAX_HISTORY_CHARS_EACH = 4_000
MAX_THREAD_ID_CHARS = 80
MAX_RAG_QUERY_CHARS = 1_500
MAX_PLAN_JSON_CHARS = 120_000  # execute body upper bound (approx)

# Per-IP sliding windows
CHAT_LIMIT = 30          # /chat per hour
EXECUTE_LIMIT = 8        # /execute per hour
RAG_LIMIT = 40           # /rag/query per hour
GLOBAL_LIMIT = 120       # any API hit per hour

_WINDOW = 3600.0  # seconds

_lock = Lock()
_buckets: dict[str, Deque[float]] = defaultdict(deque)

# Injection / jailbreak heuristics (defense-in-depth; model still gets delimited content)
_INJECTION_PATTERNS: list[re.Pattern[str]] = [
    re.compile(r"ignore\s+(all\s+)?(previous|prior|above)\s+(instructions?|rules?|prompts?)", re.I),
    re.compile(r"disregard\s+(all\s+)?(previous|prior|system)\s+", re.I),
    re.compile(r"you\s+are\s+now\s+(dan|jailbreak|unrestricted|developer\s+mode)", re.I),
    re.compile(r"\bDAN\b.*\bjailbreak\b", re.I),
    re.compile(r"reveal\s+(your\s+)?(system\s+prompt|hidden\s+instructions?|api\s*keys?)", re.I),
    re.compile(r"print\s+(your\s+)?system\s+prompt", re.I),
    re.compile(r"<\s*/?\s*system\s*>", re.I),
    re.compile(r"```\s*system", re.I),
    re.compile(r"\[?\s*INST\s*\]?", re.I),
    re.compile(r"exfiltrate|exfiltration|steal\s+(the\s+)?(keys?|secrets?)", re.I),
    re.compile(r"override\s+safety|disable\s+safety|no\s+restrictions", re.I),
]


def client_ip(request: Request) -> str:
    """Best-effort client IP (Modal / proxies set X-Forwarded-For)."""
    xff = request.headers.get("x-forwarded-for") or request.headers.get("x-real-ip")
    if xff:
        return xff.split(",")[0].strip()[:64]
    if request.client:
        return (request.client.host or "unknown")[:64]
    return "unknown"


def _prune(q: Deque[float], now: float) -> None:
    while q and now - q[0] > _WINDOW:
        q.popleft()


def rate_limit(request: Request, *, bucket: str, limit: int) -> None:
    """Raise 429 if IP exceeded `limit` hits in the last hour for this bucket."""
    ip = client_ip(request)
    key = f"{bucket}:{ip}"
    now = time.time()
    with _lock:
        q = _buckets[key]
        _prune(q, now)
        if len(q) >= limit:
            raise HTTPException(
                status_code=429,
                detail=(
                    f"Rate limit exceeded ({limit}/hour for {bucket}). "
                    "Try again later. Free public demo is shared."
                ),
                headers={"Retry-After": "300"},
            )
        # global bucket
        gkey = f"global:{ip}"
        gq = _buckets[gkey]
        _prune(gq, now)
        if len(gq) >= GLOBAL_LIMIT:
            raise HTTPException(
                status_code=429,
                detail="Global rate limit exceeded. Try again later.",
                headers={"Retry-After": "300"},
            )
        q.append(now)
        gq.append(now)


def injection_score(text: str) -> int:
    if not text:
        return 0
    return sum(1 for p in _INJECTION_PATTERNS if p.search(text))


def assert_safe_user_text(text: str, *, field: str = "message") -> None:
    if text is None:
        raise HTTPException(400, f"{field} is required")
    if not isinstance(text, str):
        raise HTTPException(400, f"{field} must be a string")
    if len(text) > MAX_MESSAGE_CHARS:
        raise HTTPException(
            400,
            f"{field} too long (max {MAX_MESSAGE_CHARS} characters).",
        )
    # Null bytes / control chars (except whitespace)
    if "\x00" in text:
        raise HTTPException(400, f"{field} contains invalid characters")
    score = injection_score(text)
    if score >= 2:
        raise HTTPException(
            400,
            "Message rejected by safety filter (looks like a prompt-injection attempt). "
            "Describe your business problem in plain language.",
        )


def sanitize_for_model(text: str) -> str:
    """
    Neutralize common instruction-smuggling while keeping business content.
    Content is also wrapped in delimiters by the strategist user payload.
    """
    t = text.replace("\x00", " ")
    # Flatten fake role tags
    t = re.sub(r"(?i)<\s*/?\s*system\s*>", " ", t)
    t = re.sub(r"(?i)<\s*/?\s*assistant\s*>", " ", t)
    t = re.sub(r"(?i)^\s*system\s*:", "user-note:", t, flags=re.M)
    t = re.sub(r"(?i)^\s*assistant\s*:", "user-note:", t, flags=re.M)
    # Cap extreme whitespace
    t = re.sub(r"\n{4,}", "\n\n\n", t)
    return t.strip()


def validate_chat_request(message: str, history: list, thread_id: str | None) -> tuple[str, list]:
    from app.schemas.plan import ChatMessage

    assert_safe_user_text(message, field="message")
    if thread_id is not None and len(str(thread_id)) > MAX_THREAD_ID_CHARS:
        raise HTTPException(400, "thread_id too long")
    if history is None:
        history = []
    if len(history) > MAX_HISTORY_MESSAGES:
        history = history[-MAX_HISTORY_MESSAGES:]

    out: list[ChatMessage] = []
    for m in history:
        role = getattr(m, "role", None) if not isinstance(m, dict) else m.get("role")
        content = getattr(m, "content", None) if not isinstance(m, dict) else m.get("content")
        if role not in ("user", "assistant"):
            # Never accept client-supplied system messages
            continue
        c = str(content or "")[:MAX_HISTORY_CHARS_EACH]
        if injection_score(c) >= 3:
            continue  # drop toxic history turns rather than 400 the whole chat
        out.append(ChatMessage(role=role, content=sanitize_for_model(c)))
    return sanitize_for_model(message), out


def validate_rag_query(query: str) -> str:
    if not query or not str(query).strip():
        raise HTTPException(400, "query is required")
    q = str(query).strip()
    if len(q) > MAX_RAG_QUERY_CHARS:
        raise HTTPException(400, f"query too long (max {MAX_RAG_QUERY_CHARS})")
    if injection_score(q) >= 2:
        raise HTTPException(400, "query rejected by safety filter")
    return sanitize_for_model(q)


SECURITY_HEADERS = {
    "X-Content-Type-Options": "nosniff",
    "X-Frame-Options": "DENY",
    "Referrer-Policy": "strict-origin-when-cross-origin",
    "Permissions-Policy": "camera=(), microphone=(), geolocation=()",
    "Cross-Origin-Opener-Policy": "same-origin",
    "Cross-Origin-Resource-Policy": "cross-origin",
}
