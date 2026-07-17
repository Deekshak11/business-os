from pathlib import Path

from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


def _default_root() -> Path:
    """
    Local layout:  services/api/app/config.py → parents[3] = business-os/
    Modal layout:  /root/app/config.py → no monorepo root; fall back to /data
    """
    p = Path(__file__).resolve()
    try:
        # Prefer monorepo root when it exists (local dev)
        cand = p.parents[3]
        if (cand / "services" / "api").is_dir() or (cand / "knowledge").is_dir():
            return cand
    except IndexError:
        pass
    # Modal / flat package
    if Path("/data").exists():
        return Path("/data")
    return p.parents[1]  # .../app → parent package root


_ENV_FILE = Path(__file__).resolve().parents[1] / ".env"  # services/api/.env


def _env_path(name: str, default: Path) -> Path:
    raw = __import__("os").environ.get(name, "").strip()
    return Path(raw) if raw else default


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=str(_ENV_FILE) if _ENV_FILE.exists() else None,
        env_file_encoding="utf-8",
        extra="ignore",
    )

    project_root: Path = _default_root()
    data_dir: Path = _env_path("BIZOS_DATA_DIR", _default_root() / "data")
    chroma_dir: Path = _env_path("BIZOS_CHROMA_DIR", _default_root() / "data" / "chroma")
    hormozi_path: Path = _env_path(
        "BIZOS_HORMOZI_PATH", _default_root() / "knowledge" / "hormozi"
    )
    copyos_path: Path = _env_path(
        "BIZOS_COPYOS_PATH", _default_root() / "knowledge" / "copyos"
    )

    # Primary LLM (OpenRouter or any OpenAI-compatible endpoint)
    openrouter_api_key: str = ""
    llm_base_url: str = "https://openrouter.ai/api/v1"
    llm_model: str = "deepseek/deepseek-v4-flash"

    # Legacy DeepSeek env names — still accepted; filled from OpenRouter when empty
    deepseek_api_key: str = ""
    deepseek_base_url: str = ""
    deepseek_model: str = ""

    xai_api_key: str = ""
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"

    # OpenRouter app attribution (optional, recommended for rankings)
    openrouter_http_referer: str = "http://127.0.0.1:5173"
    openrouter_app_title: str = "Business OS"

    # Host
    api_host: str = "127.0.0.1"
    api_port: int = 8000

    @model_validator(mode="after")
    def _resolve_llm(self) -> "Settings":
        # Prefer OpenRouter key when present
        key = (self.openrouter_api_key or self.deepseek_api_key or "").strip()
        base = (self.deepseek_base_url or self.llm_base_url or "").strip()
        model = (self.deepseek_model or self.llm_model or "").strip()

        if self.openrouter_api_key and not self.deepseek_base_url:
            base = self.llm_base_url or "https://openrouter.ai/api/v1"
        if self.openrouter_api_key and not self.deepseek_model:
            model = self.llm_model or "deepseek/deepseek-v4-flash"
        if not base:
            base = "https://openrouter.ai/api/v1" if self.openrouter_api_key else "https://api.deepseek.com"
        if not model:
            model = "deepseek/deepseek-v4-flash" if "openrouter" in base else "deepseek-chat"

        # Normalize into deepseek_* fields used by the chat client
        object.__setattr__(self, "deepseek_api_key", key)
        object.__setattr__(self, "deepseek_base_url", base.rstrip("/"))
        object.__setattr__(self, "deepseek_model", model)
        object.__setattr__(self, "llm_base_url", base.rstrip("/"))
        object.__setattr__(self, "llm_model", model)
        return self

    @property
    def llm_configured(self) -> bool:
        return bool(self.deepseek_api_key)

    @property
    def llm_provider(self) -> str:
        b = self.deepseek_base_url.lower()
        if "openrouter" in b:
            return "openrouter"
        if "deepseek" in b:
            return "deepseek"
        return "openai_compatible"


settings = Settings()
try:
    settings.data_dir.mkdir(parents=True, exist_ok=True)
    settings.chroma_dir.mkdir(parents=True, exist_ok=True)
except OSError:
    # Read-only images / first Modal volume mount edge cases
    pass
