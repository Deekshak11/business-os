"""Minimal YAML frontmatter parser (no heavy deps required beyond PyYAML)."""

from __future__ import annotations

import re
from typing import Any

import yaml

FM_RE = re.compile(r"\A---\s*\n(.*?)\n---\s*\n?(.*)\Z", re.DOTALL)


def parse_markdown_with_frontmatter(text: str) -> tuple[dict[str, Any], str]:
    m = FM_RE.match(text)
    if not m:
        return {}, text
    raw_yaml, body = m.group(1), m.group(2)
    try:
        meta = yaml.safe_load(raw_yaml) or {}
        if not isinstance(meta, dict):
            meta = {}
    except yaml.YAMLError:
        meta = {}
    return meta, body


def flatten_metadata(meta: dict[str, Any], source_path: str) -> dict[str, Any]:
    """Chroma metadata values must be str|int|float|bool."""
    out: dict[str, Any] = {"source_path": source_path}
    for k, v in meta.items():
        if v is None:
            continue
        if isinstance(v, (str, int, float, bool)):
            out[str(k)] = v
        elif isinstance(v, list):
            out[str(k)] = ",".join(str(x) for x in v)
        else:
            out[str(k)] = str(v)
    # Normalize common keys
    if "type" in out:
        out["doc_type"] = str(out["type"])
    return out
