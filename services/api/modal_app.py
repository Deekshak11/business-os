"""
Modal deployment for Business OS API.

Deploy:
  modal secret create business-os-secrets OPENROUTER_API_KEY=<your-key>
  modal deploy modal_app.py

Local serve (ephemeral URL):
  modal serve modal_app.py
"""

from __future__ import annotations

import modal

APP_NAME = "business-os-api"

app = modal.App(APP_NAME)

# Persistent Chroma store across cold starts
chroma_vol = modal.Volume.from_name("business-os-chroma", create_if_missing=True)
hf_vol = modal.Volume.from_name("business-os-hf-cache", create_if_missing=True)

# Vaults: resolved junction targets on the Windows host
_HORMOZI = r"H:\Hormozi-Business-Strategist"
_COPYOS = r"H:\Copywriting-OS"

image = (
    modal.Image.debian_slim(python_version="3.11")
    .pip_install(
        "fastapi>=0.115.0",
        "uvicorn[standard]>=0.32.0",
        "pydantic>=2.9.0",
        "pydantic-settings>=2.6.0",
        "python-dotenv>=1.0.0",
        "chromadb>=0.5.0",
        "sentence-transformers>=3.0.0",
        "httpx>=0.27.0",
        "pyyaml>=6.0.0",
        "python-multipart>=0.0.12",
        "numpy<2",
    )
    .env(
        {
            "BIZOS_HOST": "modal",
            "BIZOS_DATA_DIR": "/data",
            "BIZOS_CHROMA_DIR": "/data/chroma",
            "BIZOS_HORMOZI_PATH": "/knowledge/hormozi",
            "BIZOS_COPYOS_PATH": "/knowledge/copyos",
            "HF_HOME": "/cache/hf",
            "TRANSFORMERS_CACHE": "/cache/hf",
            "SENTENCE_TRANSFORMERS_HOME": "/cache/hf",
            "OPENROUTER_HTTP_REFERER": "https://app.deekshak.site",
            "OPENROUTER_APP_TITLE": "Business OS",
            "BIZOS_CORS_ORIGINS": (
                "https://app.deekshak.site,https://deekshak.site,https://www.deekshak.site,"
                "https://business-os-ten-chi.vercel.app"
            ),
        }
    )
    .add_local_python_source("app")
    .add_local_dir(_HORMOZI, remote_path="/knowledge/hormozi")
    .add_local_dir(_COPYOS, remote_path="/knowledge/copyos")
)


def _ensure_index() -> None:
    """Ingest vaults into Chroma if collections look empty."""
    import os
    from pathlib import Path

    os.environ.setdefault("BIZOS_CHROMA_DIR", "/data/chroma")
    os.environ.setdefault("BIZOS_HORMOZI_PATH", "/knowledge/hormozi")
    os.environ.setdefault("BIZOS_COPYOS_PATH", "/knowledge/copyos")

    # Clear cached settings if any
    from app import config as config_mod
    from app.config import Settings

    config_mod.settings = Settings()
    from app.rag.ingest import ingest_collection
    from app.rag.store import get_store

    store = get_store()
    for name, path in (
        ("hormozi", Path("/knowledge/hormozi")),
        ("copyos", Path("/knowledge/copyos")),
    ):
        col = store.get_or_create(name)
        try:
            count = col.count()
        except Exception:
            count = 0
        if count and count > 5:
            print(f"[bizos] collection {name} already has {count} chunks")
            continue
        if not path.exists():
            print(f"[bizos] missing vault path {path}")
            continue
        print(f"[bizos] ingesting {name} from {path} …")
        n = ingest_collection(store, name, path, reset=True)
        print(f"[bizos] ingested {name}: {n}")
    chroma_vol.commit()


@app.function(
    image=image,
    secrets=[modal.Secret.from_name("business-os-secrets")],
    volumes={
        "/data/chroma": chroma_vol,
        "/cache/hf": hf_vol,
    },
    timeout=60 * 15,
    memory=4096,
    cpu=2.0,
)
def bootstrap_index():
    """One-shot: build Chroma index on the Modal volume."""
    _ensure_index()
    return {"ok": True}


@app.function(
    image=image,
    secrets=[modal.Secret.from_name("business-os-secrets")],
    volumes={
        "/data/chroma": chroma_vol,
        "/cache/hf": hf_vol,
    },
    timeout=60 * 6,  # chat + execute can be long
    memory=4096,
    cpu=2.0,
    # Keep one warm container so demos stay responsive 24/7 (uses Modal credits)
    min_containers=1,
    scaledown_window=600,
)
@modal.concurrent(max_inputs=8)
@modal.asgi_app(label="bizos-api")
def fastapi_app():
    import os

    # Force production paths before importing settings
    os.environ.setdefault("BIZOS_HOST", "modal")
    os.environ.setdefault("BIZOS_CHROMA_DIR", "/data/chroma")
    os.environ.setdefault("BIZOS_HORMOZI_PATH", "/knowledge/hormozi")
    os.environ.setdefault("BIZOS_COPYOS_PATH", "/knowledge/copyos")
    os.environ.setdefault("BIZOS_DATA_DIR", "/data")
    os.environ.setdefault(
        "BIZOS_CORS_ORIGINS",
        "https://app.deekshak.site,https://deekshak.site,https://www.deekshak.site,"
        "https://business-os-ten-chi.vercel.app",
    )
    os.environ.setdefault("OPENROUTER_HTTP_REFERER", "https://app.deekshak.site")

    # Map Modal secret env if only DEEPSEEK / OPENROUTER set
    if os.getenv("OPENROUTER_API_KEY") and not os.getenv("DEEPSEEK_API_KEY"):
        os.environ["DEEPSEEK_API_KEY"] = os.environ["OPENROUTER_API_KEY"]
        os.environ.setdefault("DEEPSEEK_BASE_URL", "https://openrouter.ai/api/v1")
        os.environ.setdefault("DEEPSEEK_MODEL", "deepseek/deepseek-v4-flash")
        os.environ.setdefault("LLM_BASE_URL", "https://openrouter.ai/api/v1")
        os.environ.setdefault("LLM_MODEL", "deepseek/deepseek-v4-flash")

    # Reload settings after env is set
    from app import config as config_mod
    from app.config import Settings

    config_mod.settings = Settings()

    # Lazy first-request index if volume empty
    try:
        store = __import__("app.rag.store", fromlist=["get_store"]).get_store()
        n = store.get_or_create("hormozi").count()
        if not n:
            print("[bizos] empty chroma — running ingest")
            _ensure_index()
    except Exception as e:
        print(f"[bizos] index check: {e}")

    from app.main import app as web_app

    return web_app
