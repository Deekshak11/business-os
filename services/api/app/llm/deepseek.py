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
    timeout: float = 120.0,
) -> str:
    if not settings.deepseek_api_key:
        raise DeepSeekError(
            "LLM API key not set. Put OPENROUTER_API_KEY (or DEEPSEEK_API_KEY) in services/api/.env"
        )

    url = _completions_url(settings.deepseek_base_url)
    payload: dict[str, Any] = {
        "model": settings.deepseek_model,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
    }
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
