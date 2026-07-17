"""Builder Agent — demo-scoped implementation packs for DeepSeek V4 Flash.

Complexity gate
---------------
DeepSeek V4 Flash (OpenRouter: deepseek/deepseek-v4-flash) is an efficiency model
(~284B MoE / ~13B active): fast and cheap, solid on short docs and simple agent
tasks, not a production engineering crew. Long multi-service systems routinely
truncate or invent half-finished blueprints.

We therefore classify each plan:

* SIMPLE  — short checklists, one-pagers, copy templates → full demo artifacts
* COMPLEX — multi-service automations, agentic systems, production n8n/CRM stacks
            → DEMO MODE only: complete mini-artifacts + honest upgrade notice

Never claim a full production system was built in this demo path.
"""

from __future__ import annotations

import json
import re
from typing import Any, Literal

from app.llm.deepseek import DeepSeekError, chat_completion
from app.llm.parse_artifacts import parse_specialist_output, scrub_body, unescape_content
from app.rag.store import get_store
from app.schemas.plan import Artifact, Plan

Complexity = Literal["simple", "complex"]

# Signals that the requested work exceeds reliable Flash demo scope
_COMPLEX_PATTERNS: list[re.Pattern[str]] = [
    re.compile(r"\bn8n\b", re.I),
    re.compile(r"\bmake\.com\b|\bintegromat\b", re.I),
    re.compile(r"\b(twilio|supabase|airtable|crm|calendly|cal\.com)\b", re.I),
    re.compile(r"\b(automation|workflow|agent|multi[- ]?agent)\b", re.I),
    re.compile(r"\b(sms|webhook|self[- ]?host|docker|kubernetes)\b", re.I),
    re.compile(r"\b(production|full[- ]?stack|end[- ]?to[- ]?end)\b", re.I),
    re.compile(r"\b(dashboard|integration|pipeline)\b", re.I),
    re.compile(r"\b(system|platform|infrastructure)\b", re.I),
]

DEMO_BANNER = """
---

### Demo mode (truth)

This pack was produced by **Business OS Builder Agent** on **DeepSeek V4 Flash**
(via OpenRouter) — an efficient model tuned for speed/cost, not production engineering.

| In scope for this demo | Out of scope here |
|------------------------|-------------------|
| Complete short checklists & one-pagers | Fully tested multi-service systems |
| Sample/skeleton n8n JSON (few nodes) | Production n8n + Twilio + CRM stacks |
| Setup outlines & ship order | Agentic multi-day build + monitoring |
| Architecture notes (markdown/mermaid) | Live infra, secrets, paid APIs |

**Production-grade systems** (hardened workflows, real credentials, QA, monitoring)
need a **Business OS Pro / human builder loop** — not this free demo path.

What you got below is a **complete demo piece** you can read, copy, and extend —
not a claim that the full system was implemented and verified.
""".strip()

SYSTEM_SIMPLE = """You are the Builder Agent (demo tier) for Business OS.
Produce a COMPLETE, short implementation pack the founder can use immediately.

Rules:
1. Prefer 2 COMPLETE markdown artifacts (not 3 half-finished ones).
2. Each artifact body MUST be finished — no cut-off mid-sentence, no "…", no open tables.
3. Keep each artifact under ~600 words so output fits the model budget.
4. Be concrete: owners, acceptance checks, tool names.
5. Use REAL line breaks in bodies. Never write the two characters \\n.
6. Respond with ONLY this delimiter format (no JSON wrapper):

<<<SUMMARY>>>
1-2 sentences
<<<ARTIFACT>>>
title: short title
kind: checklist
---
full markdown body with real line breaks
<<<ARTIFACT>>>
title: short title
kind: runbook
---
full markdown body

Kinds: checklist | spec | runbook | other
"""

SYSTEM_COMPLEX = """You are the Builder Agent in DEMO MODE for Business OS.
The request is COMPLEX (multi-service automation / agentic / production-ish).
You are running on DeepSeek V4 Flash — good at short specs, weak at shipping full systems.

YOU MUST NOT claim to build a production system.
Instead produce exactly 2 COMPLETE demo artifacts:

1) **Demo blueprint** — a FINISHED short artifact:
   - Either a sample n8n workflow JSON (max 4–6 nodes, valid JSON in a fenced block)
     OR a step-by-step mini setup guide for ONE slice (e.g. "24h email reminder only")
   - Must be complete and usable as a demo, not a stub ending mid-word.

2) **Ship roadmap + honesty** — markdown that:
   - Lists what a production version would include
   - States clearly this is DEMO MODE on DeepSeek V4 Flash
   - Says production-grade delivery needs Business OS Pro / human builder

Rules:
- Exactly 2 artifacts, each COMPLETE (no truncation, no mid-sentence cuts).
- Prefer depth over breadth: one narrow demo slice, not five unfinished systems.
- Use REAL line breaks. Never write literal \\n characters.
- Kind values: blueprint | checklist | spec | demo | note
- Respond with ONLY this delimiter format (no JSON wrapper):

<<<SUMMARY>>>
Demo-mode pack: [what demo piece] — not production. Full system needs Pro.
<<<ARTIFACT>>>
title: Demo blueprint title
kind: blueprint
---
full finished markdown
<<<ARTIFACT>>>
title: Production path & demo limits
kind: note
---
full finished markdown
"""


def classify_build_complexity(plan: Plan) -> Complexity:
    """
    Heuristic threshold for DeepSeek V4 Flash demo scope.

    SIMPLE: short docs, one channel, few deliverables without multi-tool systems.
    COMPLEX: automations, multi-tool stacks, agentic workflows, production language.
    """
    parts: list[str] = [
        plan.strategy_summary or "",
        plan.business_context.offer if plan.business_context else "",
        plan.business_context.goals if plan.business_context else "",
    ]
    for d in plan.deliverables or []:
        parts.append(f"{d.type.value} {d.title} {d.spec}")
    for s in plan.action_steps or []:
        parts.append(s.action)
    blob = " ".join(parts)

    score = 0
    for pat in _COMPLEX_PATTERNS:
        if pat.search(blob):
            score += 1

    build_n = sum(1 for d in (plan.deliverables or []) if d.type.value == "build")
    if build_n >= 2:
        score += 1
    if len(plan.action_steps or []) >= 6:
        score += 1
    if len(blob) > 1800:
        score += 1

    # 2+ signals → complex (demo mode)
    return "complex" if score >= 2 else "simple"


def _format_hits(hits: list[dict[str, Any]]) -> str:
    blocks = []
    for i, h in enumerate(hits, 1):
        meta = h.get("metadata") or {}
        title = meta.get("title") or meta.get("filename") or "untitled"
        path = meta.get("source_path") or ""
        body = (h.get("text") or "")[:600]
        blocks.append(f"[{i}] {title}\nfile: {path}\n{body}")
    return "\n\n---\n\n".join(blocks) if blocks else "(no hits)"


def _looks_truncated(text: str) -> bool:
    t = (text or "").strip()
    if not t:
        return True
    if len(t) < 40:
        return True
    # mid-word cut at end (common with max_tokens)
    if re.search(r"[a-zA-Z0-9]{3,}$", t) and not t.endswith(
        (".", "!", "?", "`", "*", ")", "]", "}", '"', "'", "\n")
    ):
        # allow ending on list markers
        if not t.rstrip().endswith(("-", ":", "|")):
            # if last line is clearly incomplete markdown heading/table
            last = t.splitlines()[-1].strip()
            if len(last) > 12 and not last.endswith((".", "!", "?", "`", "*", ")")):
                if re.search(r"\bn8\s*$", last) or re.search(r"\bwith\s+\w{1,8}$", last):
                    return True
                if last.count("|") == 1 or last.endswith((" the", " a", " an", " to", " for", " and")):
                    return True
    if t.count("```") % 2 == 1:
        return True
    return False


def _repair_truncated(content: str) -> str:
    c = content.rstrip()
    if c.count("```") % 2 == 1:
        c += "\n```"
    if not c.endswith(("\n", ".", "!", "?", "`")):
        c += "\n\n*(Demo artifact closed here — content was length-limited by the model.)*\n"
    return c


def _demo_fallback_artifacts(plan: Plan) -> list[Artifact]:
    """Deterministic complete demo pack when the model fails or truncates badly."""
    title = "No-show freebie"
    for d in plan.deliverables or []:
        if d.type.value == "build" and d.title:
            title = d.title
            break
    blueprint = f"""# Demo blueprint — {title}

> **Demo mode** on DeepSeek V4 Flash. This is a complete *sample* slice, not a production system.

## Narrow demo slice (ship this first)
**One job only:** send a single **email reminder 24 hours before** an appointment.

### Mini data model (Google Sheet / free Airtable)
| Column | Example |
|--------|---------|
| client_name | Alex Agency |
| email | client@example.com |
| appointment_at | 2026-08-01T15:00:00Z |
| status | scheduled |

### Sample n8n skeleton (import and wire credentials yourself)

```json
{{
  "name": "Demo — 24h Appointment Email Reminder",
  "nodes": [
    {{
      "parameters": {{ "rule": {{ "interval": [{{ "field": "hours", "hoursInterval": 1 }}] }} }},
      "name": "Every hour",
      "type": "n8n-nodes-base.scheduleTrigger",
      "typeVersion": 1.1,
      "position": [0, 0]
    }},
    {{
      "parameters": {{
        "operation": "read",
        "documentId": "YOUR_SHEET_ID",
        "sheetName": "appointments"
      }},
      "name": "Read appointments",
      "type": "n8n-nodes-base.googleSheets",
      "typeVersion": 4,
      "position": [220, 0]
    }},
    {{
      "parameters": {{
        "conditions": {{
          "string": [{{ "value1": "={{{{$json.status}}}}", "value2": "scheduled" }}]
        }}
      }},
      "name": "Only scheduled",
      "type": "n8n-nodes-base.if",
      "typeVersion": 1,
      "position": [440, 0]
    }},
    {{
      "parameters": {{
        "fromEmail": "you@example.com",
        "toEmail": "={{{{$json.email}}}}",
        "subject": "Reminder: appointment tomorrow",
        "text": "Hi {{{{$json.client_name}}}}, this is a demo reminder for your appointment at {{{{$json.appointment_at}}}}. Reply to reschedule."
      }},
      "name": "Send reminder email",
      "type": "n8n-nodes-base.emailSend",
      "typeVersion": 2,
      "position": [660, 0]
    }}
  ],
  "connections": {{
    "Every hour": {{ "main": [[{{ "node": "Read appointments", "type": "main", "index": 0 }}]] }},
    "Read appointments": {{ "main": [[{{ "node": "Only scheduled", "type": "main", "index": 0 }}]] }},
    "Only scheduled": {{ "main": [[{{ "node": "Send reminder email", "type": "main", "index": 0 }}]] }}
  }}
}}
```

### Demo acceptance (this slice only)
- [ ] Sheet has 1 test row
- [ ] n8n imports without error
- [ ] Manual run sends one test email

SMS, multi-channel, dashboards, CRM sync = **production path** (see next artifact).
"""

    honesty = f"""# Production path & demo limits

## What you asked for
{(plan.strategy_summary or 'Open-source no-show automation freebie + ship pack.')[:800]}

## What this demo delivered
A **complete, importable sample** for one reminder channel (email + sheet).  
Enough to film a YouTube demo and put a real downloadable starter on Gumroad.

## What production still needs
1. SMS (Twilio or free alternative) + 1h reminder path  
2. Reschedule link + status writes back to the sheet  
3. No-show rate dashboard  
4. Hardened credentials, retries, logging  
5. Setup guide with screenshots + support for non-technical agencies  

## Why the cut
**DeepSeek V4 Flash** is strong on short, finished specs. Multi-service agentic builds
exceed reliable free-demo scope and often **truncate mid-output**.

## Upgrade
For production-grade systems: **Business OS Pro** (or a human builder sprint) with a
stronger model tier, longer runs, and verification — not this free demo path.

## Stage note (Hormozi)
Stage 0 · product constraint: a **narrow free magnet that works** beats a half-finished
mega-system. Ship the demo slice → get downloads → then expand.
"""

    return [
        Artifact(
            agent="build",
            title=f"Demo blueprint — {title}",
            kind="blueprint",
            content=blueprint,
            sources=["Summary-Implementation-Workshop.md", "Stage-0-Improvise.md"],
        ),
        Artifact(
            agent="build",
            title="Production path & demo limits",
            kind="note",
            content=honesty,
            sources=[],
        ),
    ]


def run_builder(plan: Plan) -> dict[str, Any]:
    complexity = classify_build_complexity(plan)
    demo_mode = complexity == "complex"

    store = get_store()
    q = " ".join(
        filter(
            None,
            [
                plan.strategy_summary,
                plan.business_context.offer if plan.business_context else "",
                "implementation checklist stage 0 free lead magnet",
            ],
        )
    )[:500]
    hits = store.query("hormozi", q, n_results=4)

    handoff = plan.to_handoff_dict()
    # Compact handoff — huge JSON burns tokens and causes truncation
    compact = {
        "stage": handoff.get("stage"),
        "constraint": handoff.get("constraint"),
        "strategy_summary": (handoff.get("strategy_summary") or "")[:900],
        "business_context": {
            "offer": (handoff.get("business_context") or {}).get("offer", ""),
            "goals": (handoff.get("business_context") or {}).get("goals", ""),
            "constraints_stated": (handoff.get("business_context") or {}).get(
                "constraints_stated", []
            )[:8],
        },
        "action_steps": (handoff.get("action_steps") or [])[:8],
        "deliverables": [
            d
            for d in (handoff.get("deliverables") or [])
            if d.get("type") == "build"
        ][:5]
        or (handoff.get("deliverables") or [])[:5],
        "recommended_route": handoff.get("recommended_route"),
    }

    system = SYSTEM_COMPLEX if demo_mode else SYSTEM_SIMPLE
    user = (
        f"## Complexity classification: {complexity.upper()}"
        f"{' — DEMO MODE (do not claim production)' if demo_mode else ''}\n\n"
        f"## Approved plan (compact)\n{json.dumps(compact, ensure_ascii=False)}\n\n"
        f"## Vault context\n{_format_hits(hits)}\n\n"
        f"{'Produce the 2 COMPLETE demo artifacts now.' if demo_mode else 'Produce 2 COMPLETE short artifacts now.'}\n"
        f"Use <<<SUMMARY>>> / <<<ARTIFACT>>> format. Real line breaks. No JSON. No literal \\\\n. Finish every artifact."
    )

    try:
        raw = chat_completion(
            [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            temperature=0.25,
            # Budget for 2 finished short artifacts; still room for JSON wrappers
            max_tokens=3500 if demo_mode else 3000,
            timeout=180.0,
        )
    except DeepSeekError as e:
        arts = _demo_fallback_artifacts(plan)
        for a in arts:
            a.content = a.content + "\n\n" + DEMO_BANNER
        return {
            "summary": (
                f"Builder LLM error ({e}). Served deterministic demo pack instead. "
                "Production systems need Business OS Pro / human builder."
            ),
            "artifacts": arts,
            "log": f"build:fallback_error:{e}",
            "error": None,
        }

    summary, arts = parse_specialist_output(
        raw, agent="build", fallback_title="Build draft"
    )
    for a in arts:
        a.content = scrub_body(unescape_content(a.content))
        if _looks_truncated(a.content):
            a.content = _repair_truncated(a.content)

    # If model returned nothing usable or still truncated heavily, replace
    if (
        not arts
        or sum(1 for a in arts if _looks_truncated(a.content)) >= max(1, len(arts))
        or any(
            a.content.strip().startswith("{") and '"artifacts"' in a.content
            for a in arts
        )
    ):
        arts = _demo_fallback_artifacts(plan)
        demo_mode = True
        summary = (
            summary
            or "Builder switched to deterministic demo pack (model output incomplete)."
        )

    # Cap artifact count in demo mode
    if demo_mode and len(arts) > 3:
        arts = arts[:2]

    # Always stamp honesty on complex/demo runs
    if demo_mode:
        for a in arts:
            if "Demo mode (truth)" not in a.content:
                a.content = a.content.rstrip() + "\n\n" + DEMO_BANNER
        if not summary.lower().startswith("demo"):
            summary = (
                "Demo-mode Builder pack (DeepSeek V4 Flash): complete starter artifacts — "
                "not a production-grade system. "
                + (summary or "")
            ).strip()

    return {
        "summary": summary or f"Produced {len(arts)} build artifact(s).",
        "artifacts": arts,
        "log": f"build:ok:{len(arts)}:complexity={complexity}:demo={demo_mode}",
    }
