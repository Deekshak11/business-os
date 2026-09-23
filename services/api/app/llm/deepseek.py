"""OpenAI-compatible chat client (OpenRouter, DeepSeek, etc.)."""

from __future__ import annotations

import json
from typing import Any, Optional

import httpx

from app.config import settings


class DeepSeekError(RuntimeError):
    """Raised on LLM HTTP / config failures (name kept for import stability)."""

    pass


# Alias for newer call sites
LLMError = DeepSeekError

# Muse Spark reasoning is mandatory and shares the output token budget.
# Default is medium. "max" is not used; that label maps to xhigh.
_REASONING_EFFORTS = {"minimal", "low", "medium", "high", "xhigh"}
_REASONING_RESERVE = {
    "minimal": 512,
    "low": 1024,
    "medium": 4096,
    "high": 8192,
    "xhigh": 16384,
}


def normalize_reasoning_effort(effort: str | None) -> str:
    raw = (effort or "medium").strip().lower()
    if raw == "max":
        return "xhigh"
    if raw in _REASONING_EFFORTS:
        return raw
    return "medium"


def _completions_url(base: str) -> str:
    """
    OpenRouter:  https://openrouter.ai/api/v1  + /chat/completions
    DeepSeek:    https://api.deepseek.com      + /v1/chat/completions
    """
    b = base.rstrip("/")
    if b.endswith("/v1"):
        return f"{b}/chat/completions"
    return f"{b}/v1/chat/completions"


def chat_completion(
    messages: list[dict[str, str]],
    *,
    temperature: float = 0.3,
    max_tokens: int = 2500,
    response_format: Optional[dict[str, Any]] = None,
    timeout: float = 180.0,
    reasoning_effort: str | None = None,
) -> str:
    if not settings.deepseek_api_key:
        raise DeepSeekError(
            "LLM API key not set. Put OPENROUTER_API_KEY (or DEEPSEEK_API_KEY) in services/api/.env"
        )

    url = _completions_url(settings.deepseek_base_url)
    effort = normalize_reasoning_effort(
        reasoning_effort if reasoning_effort is not None else settings.llm_reasoning_effort
    )
    muse = "muse-spark" in settings.deepseek_model
    # Reasoning tokens come out of max_tokens. Keep the caller's answer budget.
    output_budget = max_tokens + (_REASONING_RESERVE[effort] if muse else 0)
    payload: dict[str, Any] = {
        "model": settings.deepseek_model,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": output_budget,
    }
    if muse:
        payload["reasoning"] = {"effort": effort}
    if response_format:
        payload["response_format"] = response_format

    headers = {
        "Authorization": f"Bearer {settings.deepseek_api_key}",
        "Content-Type": "application/json",
    }
    # OpenRouter optional ranking headers
    if "openrouter.ai" in settings.deepseek_base_url:
        headers["HTTP-Referer"] = settings.openrouter_http_referer
        headers["X-Title"] = settings.openrouter_app_title

    with httpx.Client(timeout=timeout) as client:
        r = client.post(url, headers=headers, json=payload)
        if r.status_code >= 400:
            raise DeepSeekError(
                f"LLM HTTP {r.status_code} ({settings.llm_provider}): {r.text[:500]}"
            )
        data = r.json()

    try:
        content = data["choices"][0]["message"]["content"]
        # Some models return content as a list of parts
        if isinstance(content, list):
            parts = []
            for p in content:
                if isinstance(p, dict):
                    parts.append(str(p.get("text") or p.get("content") or ""))
                else:
                    parts.append(str(p))
            content = "".join(parts)
        if content is None:
            raise KeyError("empty content")
        return str(content)
    except (KeyError, IndexError, TypeError) as e:
        raise DeepSeekError(f"Unexpected LLM response: {data!r}") from e


def extract_json_object(text: str) -> dict[str, Any]:
    """Parse JSON from model output, tolerating markdown fences."""
    t = text.strip()
    if t.startswith("```"):
        lines = t.split("\n")
        if lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].strip().startswith("```"):
            lines = lines[:-1]
        t = "\n".join(lines).strip()
    start = t.find("{")
    end = t.rfind("}")
    if start == -1 or end == -1 or end <= start:
        raise ValueError("No JSON object found in model output")
    return json.loads(t[start : end + 1])
