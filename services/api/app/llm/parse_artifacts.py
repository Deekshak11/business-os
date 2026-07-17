"""Parse specialist (copy/build) model output into clean artifacts.

Never surface raw JSON dumps, literal \\n sequences, or quote-glue to the UI.
Accepts:
  - valid / truncated JSON with artifacts[]
  - delimiter format (<<<ARTIFACT>>> ...)
  - plain markdown prose
"""

from __future__ import annotations

import json
import re
from typing import Any

from app.llm.deepseek import extract_json_object
from app.schemas.plan import Artifact


# ---------------------------------------------------------------------------
# Low-level string cleanup
# ---------------------------------------------------------------------------

def unescape_content(text: str) -> str:
    """Turn literal \\n / \\t / \\\" into real characters (idempotent-ish)."""
    if not text:
        return ""
    s = str(text)
    # Repeated passes for double-escaped blobs ("\\\\n" → "\\n" → "\n")
    for _ in range(3):
        if "\\n" not in s and "\\t" not in s and '\\"' not in s and "\\u" not in s:
            break
        try:
            # Prefer real JSON string decode when the whole value is one string
            if s.startswith('"') and s.endswith('"') and s.count('"') >= 2:
                decoded = json.loads(s)
                if isinstance(decoded, str):
                    s = decoded
                    continue
        except Exception:
            pass
        try:
            decoded = json.loads(f'"{s}"')
            if isinstance(decoded, str):
                s = decoded
                continue
        except Exception:
            pass
        s = (
            s.replace("\\r\\n", "\n")
            .replace("\\n", "\n")
            .replace("\\r", "\n")
            .replace("\\t", "\t")
            .replace('\\"', '"')
            .replace("\\'", "'")
            .replace("\\\\", "\\")
        )
        # unicode escapes like \u2014
        def _u(m: re.Match[str]) -> str:
            try:
                return chr(int(m.group(1), 16))
            except Exception:
                return m.group(0)

        s = re.sub(r"\\u([0-9a-fA-F]{4})", _u, s)
    return s if isinstance(s, str) else str(s)


def scrub_body(text: str) -> str:
    """Remove JSON chrome / quote-glue that models leave in content bodies.

    Handles patterns seen in production:
      "\\n\\n"Testimonial Scripts
      "Script 1: ...
      trailing "
      half-stripped { "title": ... } wrappers
    """
    if not text:
        return ""
    s = unescape_content(text).strip()

    # Whole body is still a JSON object → peel content fields first
    if _looks_like_json_blob(s):
        peeled = _peel_content_fields(s)
        if peeled:
            s = peeled

    # Unwrap if the entire body is still one big quoted string
    if len(s) >= 2 and s[0] in "\"'" and s[-1] == s[0]:
        inner = s[1:-1]
        # only unwrap if it looks like escaped content, not a title with quotes
        if "\\n" in s or "\n" in inner or len(inner) > 40:
            s = unescape_content(inner).strip()

    # Quote-glue between sections:  "\n\n"  or  "\n"  or  ", "
    s = re.sub(r'"\s*\\n\s*"', "\n\n", s)
    s = re.sub(r'"\s*\n+\s*"', "\n\n", s)
    s = re.sub(r'"\s*,\s*"', "\n\n", s)

    # Lines that are only quotes / commas / braces
    cleaned_lines: list[str] = []
    for line in s.split("\n"):
        t = line.strip()
        if t in {'"', "'", '""', "''", ",", ",,", "{", "}", "{},", "[]", "],", "},"}:
            cleaned_lines.append("")
            continue
        # Leading/trailing orphan quotes on a line
        line2 = re.sub(r'^["\']+\s*', "", line)
        line2 = re.sub(r'\s*["\']+$', "", line2)
        # Strip leftover JSON keys at line start
        line2 = re.sub(
            r'^\s*"(?:title|kind|content|summary|sources|agent|artifacts)"\s*:\s*"?',
            "",
            line2,
            flags=re.I,
        )
        cleaned_lines.append(line2)
    s = "\n".join(cleaned_lines)

    # Drop residual key:value chrome if any slipped through (not inside code fences)
    s = _strip_json_keys_outside_fences(s)

    # Final unescape in case keys held escapes
    s = unescape_content(s)
    s = re.sub(r"\n{3,}", "\n\n", s).strip()
    # One more pass on leading/trailing quotes
    s = s.strip().strip('"').strip("'").strip()
    return s


def _strip_json_keys_outside_fences(text: str) -> str:
    parts = re.split(r"(```[\s\S]*?```)", text)
    out: list[str] = []
    for i, part in enumerate(parts):
        if i % 2 == 1:  # fenced code — leave alone
            out.append(part)
            continue
        p = part
        p = re.sub(r'"sources"\s*:\s*\[[^\]]*\]\s*,?', "", p, flags=re.I)
        p = re.sub(r'"(?:title|kind|summary|agent)"\s*:\s*"[^"]*"\s*,?', "", p, flags=re.I)
        p = re.sub(r'"content"\s*:\s*"', "", p, flags=re.I)
        p = re.sub(r'"artifacts"\s*:\s*\[', "\n", p, flags=re.I)
        # only strip bare braces when the chunk still looks like JSON chrome
        if re.search(r'"\w+"\s*:', p) or p.strip().startswith("{"):
            p = re.sub(r"^\s*[\{\[]\s*", "", p)
            p = re.sub(r"\s*[\}\]]\s*$", "", p)
        out.append(p)
    return "".join(out)


def _peel_content_fields(raw: str) -> str:
    """Join all content string values found in a JSON-ish blob."""
    chunks = _extract_string_fields(raw, "content")
    if not chunks:
        return ""
    return "\n\n---\n\n".join(c for c in chunks if c.strip())


def _looks_like_json_blob(text: str) -> bool:
    t = text.strip()
    return t.startswith("{") and (
        "artifacts" in t or '"summary"' in t or '"content"' in t
    )


# ---------------------------------------------------------------------------
# JSON repair / field extraction
# ---------------------------------------------------------------------------

def _repair_json(text: str) -> str:
    """Best-effort close truncated JSON so json.loads can succeed."""
    t = text.strip()
    if t.startswith("```"):
        lines = t.split("\n")
        if lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].strip().startswith("```"):
            lines = lines[:-1]
        t = "\n".join(lines).strip()
    start = t.find("{")
    if start == -1:
        return t
    t = t[start:]
    if t.count('"') % 2 == 1:
        t += '"'
    t = re.sub(r",\s*$", "", t)
    open_a = t.count("[") - t.count("]")
    open_b = t.count("{") - t.count("}")
    t += "]" * max(0, open_a) + "}" * max(0, open_b)
    return t


def _read_json_string(s: str, start: int) -> tuple[str, int] | None:
    """Read a JSON string starting at s[start] == '"'. Returns (value, end_idx)."""
    if start >= len(s) or s[start] != '"':
        return None
    i = start + 1
    out: list[str] = []
    while i < len(s):
        ch = s[i]
        if ch == "\\":
            if i + 1 >= len(s):
                break
            nxt = s[i + 1]
            escapes = {"n": "\n", "t": "\t", "r": "\r", '"': '"', "\\": "\\", "/": "/"}
            if nxt in escapes:
                out.append(escapes[nxt])
                i += 2
                continue
            if nxt == "u" and i + 5 < len(s):
                try:
                    out.append(chr(int(s[i + 2 : i + 6], 16)))
                    i += 6
                    continue
                except Exception:
                    pass
            out.append(nxt)
            i += 2
            continue
        if ch == '"':
            return ("".join(out), i + 1)
        out.append(ch)
        i += 1
    # Unclosed string — return what we have
    return ("".join(out), i)


def _extract_string_fields(text: str, field: str) -> list[str]:
    """Extract all JSON string values for a given field name, even in broken JSON."""
    results: list[str] = []
    pattern = re.compile(rf'"{re.escape(field)}"\s*:\s*"', re.I)
    for m in pattern.finditer(text):
        start = m.end() - 1  # points at opening "
        read = _read_json_string(text, start)
        if read:
            val, _ = read
            results.append(val)
    return results


def _extract_artifacts_regex(text: str) -> list[dict[str, Any]]:
    """Pull artifact objects even from broken multi-artifact JSON."""
    arts: list[dict[str, Any]] = []
    # Find each "title": "..." then nearby kind/content
    for m in re.finditer(r'"title"\s*:\s*"', text):
        title_read = _read_json_string(text, m.end() - 1)
        if not title_read:
            continue
        title, pos = title_read
        window = text[pos : pos + 8000]
        kind = "draft"
        content = ""
        sources: list[str] = []

        km = re.search(r'"kind"\s*:\s*"', window)
        if km:
            kr = _read_json_string(window, km.end() - 1)
            if kr:
                kind = kr[0] or kind

        cm = re.search(r'"content"\s*:\s*"', window)
        if cm:
            cr = _read_json_string(window, cm.end() - 1)
            if cr:
                content = cr[0]

        sm = re.search(r'"sources"\s*:\s*(\[[^\]]*\])', window)
        if sm:
            try:
                sources = [str(x) for x in json.loads(sm.group(1))]
            except Exception:
                sources = re.findall(r'"([^"]+\.md)"', sm.group(1))

        if content.strip() or title.strip():
            arts.append(
                {
                    "title": unescape_content(title).strip() or "Draft",
                    "kind": kind,
                    "content": content,
                    "sources": sources,
                }
            )
    return arts


# ---------------------------------------------------------------------------
# Delimiter format (preferred — models break JSON less often this way)
# ---------------------------------------------------------------------------

_DELIM_SUMMARY = re.compile(
    r"<<<SUMMARY>>>\s*(.*?)\s*(?=<<<ARTIFACT>>>|$)", re.S | re.I
)
_DELIM_ARTIFACT = re.compile(
    r"<<<ARTIFACT>>>\s*(.*?)\s*(?=<<<ARTIFACT>>>|$)", re.S | re.I
)


def _parse_delimiter_format(raw: str) -> tuple[str, list[dict[str, Any]]]:
    if "<<<ARTIFACT>>>" not in raw.upper() and "<<<SUMMARY>>>" not in raw.upper():
        return "", []
    summary = ""
    sm = _DELIM_SUMMARY.search(raw)
    if sm:
        summary = sm.group(1).strip()
    arts: list[dict[str, Any]] = []
    for block in _DELIM_ARTIFACT.findall(raw):
        title, kind, body = "Draft", "draft", block
        # Optional header lines before ---
        if "---" in block:
            head, body = block.split("---", 1)
        else:
            head = ""
            # try first lines as meta
            lines = block.split("\n")
            meta_lines = []
            rest_start = 0
            for i, line in enumerate(lines):
                if re.match(r"^(title|kind)\s*:", line, re.I):
                    meta_lines.append(line)
                    rest_start = i + 1
                elif line.strip() == "":
                    rest_start = i + 1
                    if meta_lines:
                        break
                else:
                    break
            if meta_lines:
                head = "\n".join(meta_lines)
                body = "\n".join(lines[rest_start:])
        tm = re.search(r"title\s*:\s*(.+)", head, re.I)
        km = re.search(r"kind\s*:\s*(\S+)", head, re.I)
        if tm:
            title = tm.group(1).strip().strip("\"'")
        if km:
            kind = km.group(1).strip().strip("\"'")
        arts.append({"title": title, "kind": kind, "content": body.strip(), "sources": []})
    return summary, arts


# ---------------------------------------------------------------------------
# Artifact construction
# ---------------------------------------------------------------------------

def _artifact_from_dict(a: dict[str, Any], *, agent: str) -> Artifact:
    content = scrub_body(str(a.get("content") or ""))
    # If content itself is still a JSON wrapper, unwrap once more
    if _looks_like_json_blob(content) and len(content) > 80:
        try:
            inner = extract_json_object(content)
            if isinstance(inner, dict) and inner.get("content"):
                content = scrub_body(str(inner.get("content")))
            elif isinstance(inner, dict) and inner.get("artifacts"):
                first = (inner.get("artifacts") or [None])[0]
                if isinstance(first, dict):
                    content = scrub_body(str(first.get("content") or content))
        except Exception:
            peeled = _peel_content_fields(content)
            if peeled:
                content = scrub_body(peeled)
    sources = a.get("sources") or []
    if not isinstance(sources, list):
        sources = []
    title = scrub_body(str(a.get("title") or "Draft")).split("\n")[0].strip() or "Draft"
    # Title should never be a whole essay
    if len(title) > 120:
        title = title[:117] + "…"
    return Artifact(
        agent=agent,
        title=title,
        kind=str(a.get("kind") or "other").strip() or "other",
        content=content.strip(),
        sources=[str(s) for s in sources if s],
    )


def parse_specialist_output(
    raw: str,
    *,
    agent: str,
    fallback_title: str = "Draft",
) -> tuple[str, list[Artifact]]:
    """
    Returns (summary, artifacts). Always returns readable markdown artifacts —
    never a raw JSON blob as the primary content.
    """
    raw = (raw or "").strip()
    if not raw:
        return "No content returned.", []

    arts: list[Artifact] = []
    summary = ""

    # 1) Delimiter format (preferred path for new prompts)
    d_summary, d_arts = _parse_delimiter_format(raw)
    if d_arts:
        summary = d_summary
        for a in d_arts:
            arts.append(_artifact_from_dict(a, agent=agent))

    # 2) JSON object
    if not arts:
        data: dict[str, Any] | None = None
        try:
            data = extract_json_object(raw)
        except Exception:
            try:
                data = json.loads(_repair_json(raw))
            except Exception:
                data = None

        if isinstance(data, dict):
            summary = str(data.get("summary") or "").strip()
            for a in data.get("artifacts") or []:
                if isinstance(a, dict) and (a.get("content") or a.get("title")):
                    arts.append(_artifact_from_dict(a, agent=agent))

    # 3) Regex salvage of title/kind/content fields
    if not arts:
        for a in _extract_artifacts_regex(raw):
            arts.append(_artifact_from_dict(a, agent=agent))

    # 4) Pull bare content fields
    if not arts and (_looks_like_json_blob(raw) or '"content"' in raw):
        contents = _extract_string_fields(raw, "content")
        titles = _extract_string_fields(raw, "title")
        if contents:
            for i, c in enumerate(contents):
                title = titles[i] if i < len(titles) else (
                    f"{fallback_title} {i + 1}" if len(contents) > 1 else fallback_title
                )
                arts.append(
                    _artifact_from_dict(
                        {"title": title, "kind": "draft", "content": c, "sources": []},
                        agent=agent,
                    )
                )
            summary = summary or "Recovered draft from incomplete model JSON."

    # 5) Last resort: scrub whole raw into one prose card
    if not arts:
        body = scrub_body(raw)
        # If scrub left nothing useful, use light unescape
        if not body or len(body) < 20:
            body = unescape_content(raw).strip()
        arts.append(
            Artifact(
                agent=agent,
                title=fallback_title,
                kind="draft",
                content=body[:12000],
                sources=[],
            )
        )
        summary = summary or "Draft saved as formatted text."

    # Final scrub pass on every card (defense in depth)
    cleaned: list[Artifact] = []
    for a in arts:
        body = scrub_body(a.content)
        if not body.strip():
            continue
        cleaned.append(
            Artifact(
                agent=a.agent,
                title=a.title,
                kind=a.kind,
                content=body[:12000],
                sources=a.sources,
            )
        )
    arts = cleaned

    if not summary:
        summary = f"Produced {len(arts)} draft(s)."
    return summary, arts
