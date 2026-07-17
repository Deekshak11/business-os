"""Copywriting Agent — CopyOS RAG + LLM → paste-ready copy artifacts."""

from __future__ import annotations

import json
from typing import Any

from app.llm.deepseek import DeepSeekError, chat_completion
from app.llm.parse_artifacts import parse_specialist_output
from app.rag.store import get_store
from app.schemas.plan import Artifact, Plan

# Delimiter format is far more reliable than nested JSON for Flash models
# (no escape hell, truncation still yields readable bodies).
SYSTEM = """You are the Copywriting Agent for Business OS.
You write paste-ready marketing copy grounded in classic direct-response craft
from the CopyOS vault (Schwartz, Halbert, Hormozi offer math, Ogilvy, Brunson, etc.).

CRITICAL OUTPUT RULES:
1. Respond with ONLY the delimiter format below. No JSON. No markdown fences around the whole reply.
2. Produce exactly 2 COMPLETE artifacts. Finish every draft — no cut-off mid-sentence.
3. Body text uses real line breaks (press enter). Never write the two characters \\n.
4. Do NOT put Sources inside the body — omit sources entirely.
5. Do NOT repeat the title as the first line of the body.
6. Use markdown in bodies: ## headings, **bold**, numbered lists, blank lines between sections.

Exact format:

<<<SUMMARY>>>
one sentence about what you produced
<<<ARTIFACT>>>
title: short human title
kind: script
---
## Section

paste-ready markdown body with real line breaks

<<<ARTIFACT>>>
title: another short title
kind: email
---
paste-ready markdown body

Kinds: hook | script | email | sequence | page | other

Default pack if plan is vague:
1) YouTube / VSL script (hook → cost → mechanism → CTA)
2) Short nurture email or 3 testimonial prep scripts
"""


def _format_hits(hits: list[dict[str, Any]]) -> str:
    blocks = []
    for i, h in enumerate(hits, 1):
        meta = h.get("metadata") or {}
        title = meta.get("title") or meta.get("filename") or "untitled"
        path = meta.get("source_path") or meta.get("filename") or ""
        body = (h.get("text") or "")[:700]
        blocks.append(f"[{i}] {title}\nfile: {path}\n{body}")
    return "\n\n---\n\n".join(blocks) if blocks else "(no CopyOS hits)"


def _plan_query(plan: Plan) -> str:
    titles = [d.title for d in plan.deliverables if d.type.value == "copy"]
    offer = plan.business_context.offer if plan.business_context else ""
    goals = plan.business_context.goals if plan.business_context else ""
    bits = [
        plan.strategy_summary or "",
        offer,
        goals,
        " ".join(titles),
        "headline youtube script email nurture gumroad CTA",
    ]
    return " ".join(b for b in bits if b)[:700]


def run_copywriter(plan: Plan) -> dict[str, Any]:
    """Returns { summary, artifacts, log, error? } — artifacts always human-readable."""
    store = get_store()
    q = _plan_query(plan)
    hits = store.query("copyos", q, n_results=6)
    for d in plan.deliverables:
        if d.type.value != "copy":
            continue
        for h in store.query("copyos", f"{d.title} {d.spec}", n_results=2):
            hits.append(h)
    seen: set[tuple] = set()
    uniq: list[dict[str, Any]] = []
    for h in hits:
        key = ((h.get("metadata") or {}).get("source_path"), (h.get("text") or "")[:60])
        if key in seen:
            continue
        seen.add(key)
        uniq.append(h)
    hits = uniq[:8]

    handoff = plan.to_handoff_dict()
    copy_deliv = [
        d for d in (handoff.get("deliverables") or []) if d.get("type") == "copy"
    ]
    compact = {
        "stage": handoff.get("stage"),
        "constraint": handoff.get("constraint"),
        "strategy_summary": (handoff.get("strategy_summary") or "")[:900],
        "offer": (handoff.get("business_context") or {}).get("offer", ""),
        "goals": (handoff.get("business_context") or {}).get("goals", ""),
        "copy_deliverables": copy_deliv[:4] or handoff.get("deliverables") or [],
        "action_steps": (handoff.get("action_steps") or [])[:6],
    }
    user = (
        f"## Plan (compact)\n{json.dumps(compact, ensure_ascii=False)}\n\n"
        f"## CopyOS craft\n{_format_hits(hits)}\n\n"
        f"Write exactly 2 complete artifacts using <<<SUMMARY>>> / <<<ARTIFACT>>> format.\n"
        f"Real line breaks in bodies. No JSON. No literal \\\\n characters."
    )

    try:
        raw = chat_completion(
            [
                {"role": "system", "content": SYSTEM},
                {"role": "user", "content": user},
            ],
            temperature=0.35,
            max_tokens=3200,
            timeout=180.0,
        )
    except DeepSeekError as e:
        return {
            "summary": f"Copywriting Agent failed: {e}",
            "artifacts": [],
            "log": f"copy:error:{e}",
            "error": str(e),
        }

    summary, arts = parse_specialist_output(
        raw,
        agent="copy",
        fallback_title="Copy draft",
    )
    arts = arts[:3]
    if not arts:
        arts = [
            Artifact(
                agent="copy",
                title="Copy note",
                kind="note",
                content="No usable copy returned. Re-run Copywriting Agent from Plan.",
                sources=[],
            )
        ]

    return {
        "summary": summary,
        "artifacts": arts,
        "log": f"copy:ok:{len(arts)}",
    }
