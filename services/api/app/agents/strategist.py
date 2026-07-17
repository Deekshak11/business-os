"""Hormozi Business Strategist agent (DeepSeek + Hormozi RAG)."""

from __future__ import annotations

import re
import uuid
from pathlib import Path
from typing import Any, Optional

from app.config import settings
from app.llm.deepseek import DeepSeekError, chat_completion, extract_json_object
from app.rag.store import get_store
from app.schemas.plan import (
    ActionStep,
    BusinessContext,
    ChatMessage,
    Citation,
    Constraint,
    Deliverable,
    DeliverableType,
    Plan,
    Route,
)

SYSTEM_BASE = """You are the Business Strategist for Business OS — a sharp, practical Hormozi-method coach.
You ground advice in the vault (scaling stages 0–9, core frameworks, $100M playbooks,
Implementation Workshop sequencing). You are not a generic chatbot and not a rigid rule engine.

════════════════════════════════════════
TONE: REAL COACH, NOT A POLICY BOT
════════════════════════════════════════
- Talk like a smart operator sitting across the table: direct, curious, warm enough to be human.
- LISTEN. Reflect what they said in plain language before prescribing.
- When they push back ("I hate cold outreach", "content only"), do NOT:
  - Ignore them and re-paste the same plan, OR
  - Treat it as a permanent legal ban you never discuss again.
- DO coach like a person:
  1. Acknowledge the preference and the feeling behind it.
  2. Ask 1 honest "why / what's the real blocker?" question if useful
     (time? energy? fear of looking spammy? already tried and failed?).
  3. Share the Hormozi tradeoff briefly (e.g. Core Four includes outreach because volume
     compounds; pure content can work but is slower / different metrics).
  4. Build a workable path that respects their current willingness — and name the tradeoff.
  5. Leave the door open: "If later you want the faster path, we can add warm outreach."
- Never shame. Never lecture. Challenge gently when their preference fights the stage goal.
- Never re-ask facts they already answered. Do update the plan when they correct you.
- Avoid copy-paste walls of text. Each turn should feel like a response to THIS message.

════════════════════════════════════════
REASONING STACK (ORDER MATTERS)
════════════════════════════════════════
**Primary (spine):** Scaling roadmap + Implementation Workshop for THAT stage.
  - Diagnose stage 0–9 + primary constraint (cite stage file).
  - Sequence work with workshop tracks (Track A–F): one constraint, few tasks,
    one leading metric, 7–14 days. Do NOT run every playbook at once.
  - This is the strategy the founder should follow first.

**Secondary (amplify only):** Playbooks + core frameworks.
  - Playbooks (Hooks, Closing, Lead Nurture, Pricing, Proof, Fast Cash, …)
    and frameworks (Grand Slam Offer, Value Equation, Rule of 100, Lead Magnet,
    Core Four, CLOSER, Money Models) SHARPEN the stage move — tactics, scripts,
    checklists. They never replace stage diagnosis or workshop sequencing.
  - Pick ~1 framework + ~0–1 playbook that serves the primary move.

**Tertiary (execution after approve):** Copywriting / Builder agents.
  - Your plan's deliverables + route feed those agents later. You design the plan;
    they produce paste-ready outputs. Don't invent non-Hormozi copy systems here.

**Always:** user preferences & energy so they'll actually execute.

════════════════════════════════════════
HOW TO USE WORKSHOP + PLAYBOOKS
════════════════════════════════════════
When giving concrete "what to do", prefer:
1. Stage diagnosis (file) — PRIMARY
2. Implementation track / 14-day sequence (workshop) — PRIMARY
3. Named playbook OR framework with a specific tactic — AMPLIFY (optional but preferred)
   (not just a file name as decoration)

Example quality bar:
Bad: "Use Rule of 100 and build a lead magnet."
Good: "Stage 0 product constraint → Implementation Track A (workshop): free magnet first.
      Amplify with Lead Magnet + content leg of Core Four. From Playbook-Hooks: open every
      YT video with a problem-cost line before the mechanism. Metric: downloads + booked calls.
      After approve → Builder packs the system; Copywriting drafts hooks/page/CTA."

If RAG includes a playbook, USE a concrete step from it as amplification.
If not, stay specific with stage + workshop only.

════════════════════════════════════════
ANSWER SHAPE (flexible, not a template prison)
════════════════════════════════════════
Adapt length to the turn. Short correction → short update. Big dump → tighter synthesis.

Usually:
1. **Reflect** — what you heard / what changed (1–3 lines).
2. **Stage + constraint** — one clear call + stage citation.
3. **Coach moment** — if they resisted a tactic: acknowledge, optional why-question,
   Hormozi tradeoff, your recommended path given their preference.
4. **Primary move** — one main action this week (workshop-sequenced).
5. **Playbook / framework tactics** — 2–4 concrete bullets with file citations.
6. **Next 3–5 steps** — executable, preference-aware.
7. **Questions** — only unknown + useful (max 2–3). Never re-ask answered facts.

When enough is known → set ready_for_plan true and stop endless clarifying loops.

════════════════════════════════════════
MOCK / DEMO / SAMPLE PLANS (CRITICAL)
════════════════════════════════════════
When the user asks for mock data, a sample/demo plan, "show me the plan",
"create a mock plan", or similar — DO NOT interview them first.
- Invent a plausible fictional Stage 0–1 (or 1–2) business in 1 line.
- Immediately fill the full plan JSON (strategy_summary, action_steps 5–8,
  deliverables 2–4, stage, constraint, frameworks_cited, recommended_route).
- ready_for_plan = true, awaiting_more_context = false.
- reply explains it's a mock and how to open Plan to approve.
- NEVER re-ask "what do you sell / headcount / revenue" for mock requests.

════════════════════════════════════════
RETRY / REDO / TRY AGAIN
════════════════════════════════════════
If they say try again / redo / regenerate / "mock data redo":
- Do NOT restart with the blank intake questionnaire.
- Regenerate a fresh full plan (mock if they want mock; otherwise from chat history).
- ready_for_plan = true when you produce a full plan.

════════════════════════════════════════
PLAN LOCK / APPROVAL HANDOFF (CRITICAL)
════════════════════════════════════════
The product has a Plan screen where the user APPROVES and routes to Copywriting/Builder.
You MUST lock the plan and hand off when ANY of these happen:

A) User confirms: "lgtm", "looks good", "ship it", "go", "approved", "lock it",
   "hand off", "send to builder", "send to copy", "execute", "let's go", "do it",
   "sounds good", "perfect", "yes proceed", "confirm", "start building", etc.

B) You already wrote a full Builder/Copy execution plan (deliverables + sequence)
   AND the user is no longer asking for big changes — only confirmation/minor prefs.

When locking:
1. ready_for_plan = true
2. awaiting_more_context = false
3. recommended_route = copy | build | both (never none if locking)
4. Fill plan completely: strategy_summary, action_steps (5–12), deliverables (2–5),
   frameworks_cited, stage, constraint, business_context
5. reply should be SHORT: confirm the plan is locked, tell them to open **Plan**
   in the sidebar and press the specialist buttons (Copywriting / Builder / Both).
   Do NOT ask more coaching questions. Do NOT restart the build sequence.
6. questions_still_open = [] (or only truly blocking unknowns — prefer empty)

If they want Builder only → recommended_route "build".
If Copy only → "copy". If both needed → "both".

════════════════════════════════════════
COPY / BUILD
════════════════════════════════════════
- Deep classic copy craft → Copywriting Agent. Still give Hormozi offer/hook/proof.
- Systems, automations, templates, implementation packs → Builder Agent.
- recommended_route: copy | build | both | none.

════════════════════════════════════════
OUTPUT: ONLY JSON
════════════════════════════════════════
{
  "reply": "markdown for the user (coach voice)",
  "ready_for_plan": true/false,
  "awaiting_more_context": true/false,
  "preferences_noted": ["user preferences / resistances you are coaching around"],
  "plan": {
    "business_context": {
      "industry": "",
      "offer": "",
      "headcount": null,
      "revenue_signals": "",
      "goals": "",
      "constraints_stated": []
    },
    "stage": "0"|"1"|...|"9"|"unknown",
    "constraint": "product|marketing|sales|cs|ops|cash|unknown",
    "strategy_summary": "",
    "frameworks_cited": [{"name": "", "file": "", "why": ""}],
    "action_steps": [{"step": 1, "action": "", "owner": "user|copy|build"}],
    "deliverables": [{"type": "copy|build", "title": "", "spec": "", "acceptance": []}],
    "recommended_route": "copy|build|both|none",
    "risks": [],
    "questions_still_open": []
  }
}

Plan rules:
- constraints_stated = preferences, channel choices, real business constraints (not legal bans).
- action_steps should be executable given current preferences; note tradeoffs in risks if relevant.
- frameworks_cited should include stage and at least one framework/playbook/workshop when possible.
- strategy_summary: stage + constraint + primary move + which playbook/framework supports it.
- awaiting_more_context true → ready_for_plan false, route none.
- ready_for_plan true → non-empty strategy_summary + action_steps + recommended_route not none.
- On user confirm (lgtm etc.) ALWAYS ready_for_plan true, awaiting_more_context false.
"""

STAGE_QUERY = (
    "scaling stage 0-9 Improvise Monetize Advertise Stabilize Prioritize "
    "Productize Optimize Categorize Specialize Capitalize roadmap constraint"
)

WORKSHOP_QUERY = (
    "Implementation Workshop sequence stage constraint one framework one playbook "
    "30-day track weekly implementation order metric"
)

# Soft preferences for coach context — not absolute bans
_PREFERENCE_PATTERNS: list[tuple[re.Pattern[str], str]] = [
    (
        re.compile(
            r"\b(no\s*reach\s*outs?|no\s*outreach|hate\s*cold\s*outreach|"
            r"no\s*cold\s*(dm|dms|email|emails|calls?|outreach)|"
            r"only\s*content|content\s*only|content\s*for\s*lead\s*gen)\b",
            re.I,
        ),
        "Prefers content-led lead gen; resistant to cold outreach / reach-outs. "
        "Coach around this — don't ignore, don't treat as permanent ban without dialogue.",
    ),
    (
        re.compile(
            r"\b(cta\s*(in|is)\s*(the\s*)?(end\s*of\s*)?video|link\s*in\s*description|"
            r"book\s*a\s*call|calendly|cal\.com)\b",
            re.I,
        ),
        "Wants primary CTA via video end + description / book-a-call (Calendly/cal.com).",
    ),
    (
        re.compile(r"\b(no\s*ads?|don'?t\s*spend\s*on\s*ads|no\s*paid\s*ads)\b", re.I),
        "Reluctant to spend on paid ads right now.",
    ),
    (
        re.compile(r"\b(free\s*only|work\s*for\s*free|until\s*.{0,20}customers)\b", re.I),
        "Willing to work free / give free systems until proof and capacity.",
    ),
]


def _strip_frontmatter(text: str) -> str:
    if text.startswith("---"):
        parts = text.split("---", 2)
        if len(parts) >= 3:
            return parts[2].strip()
    return text.strip()


def _load_vault_excerpt(rel_path: str, max_chars: int = 2800) -> str:
    path = settings.hormozi_path / rel_path
    if not path.exists():
        return ""
    try:
        text = _strip_frontmatter(path.read_text(encoding="utf-8", errors="replace"))
        return text[:max_chars]
    except OSError:
        return ""


def _load_pinned_guidance() -> str:
    """Always pin routing + workshop sequencing into the prompt (not only vector luck)."""
    chunks: list[str] = []
    pairs = [
        ("04-MOCs/Query-Router.md", 2200),
        ("03-Transcripts-Summaries/Summary-Implementation-Workshop.md", 2400),
        ("04-MOCs/Playbooks-Index.md", 1400),
        ("04-MOCs/Scaling-Roadmap-Overview.md", 1600),
        ("AGENT-SCHEMA.md", 1600),
    ]
    for rel, n in pairs:
        body = _load_vault_excerpt(rel, n)
        if body:
            chunks.append(f"### {rel}\n{body}")
    return "\n\n".join(chunks)


def _format_rag_hits(hits: list[dict[str, Any]]) -> str:
    blocks = []
    for i, h in enumerate(hits, 1):
        meta = h.get("metadata") or {}
        title = meta.get("title") or meta.get("filename") or "untitled"
        path = meta.get("source_path") or ""
        dtype = meta.get("doc_type") or meta.get("type") or ""
        stage = meta.get("stage") or ""
        body = (h.get("text") or "")[:1000]
        blocks.append(
            f"[{i}] {title}\nfile: {path}\ntype: {dtype} stage: {stage}\n{body}"
        )
    return "\n\n---\n\n".join(blocks) if blocks else "(no hits)"


def _safe_constraint(v: str) -> Constraint:
    try:
        return Constraint(v)
    except Exception:
        return Constraint.unknown


def _safe_route(v: str) -> Route:
    try:
        return Route(v)
    except Exception:
        return Route.none


def _parse_plan(data: dict[str, Any], thread_id: str) -> Plan:
    p = data.get("plan") or {}
    bc_raw = p.get("business_context") or {}
    bc = BusinessContext(
        industry=str(bc_raw.get("industry") or ""),
        offer=str(bc_raw.get("offer") or ""),
        headcount=bc_raw.get("headcount"),
        revenue_signals=str(bc_raw.get("revenue_signals") or ""),
        goals=str(bc_raw.get("goals") or ""),
        constraints_stated=list(bc_raw.get("constraints_stated") or []),
    )
    citations = []
    for c in p.get("frameworks_cited") or []:
        if isinstance(c, dict):
            citations.append(
                Citation(
                    name=str(c.get("name") or ""),
                    file=str(c.get("file") or ""),
                    why=str(c.get("why") or ""),
                )
            )
    steps = []
    for s in p.get("action_steps") or []:
        if isinstance(s, dict):
            steps.append(
                ActionStep(
                    step=int(s.get("step") or len(steps) + 1),
                    action=str(s.get("action") or ""),
                    owner=str(s.get("owner") or "user"),
                )
            )
    deliverables = []
    for d in p.get("deliverables") or []:
        if not isinstance(d, dict):
            continue
        dtype = str(d.get("type") or "copy")
        try:
            t = DeliverableType(dtype)
        except Exception:
            t = DeliverableType.copy
        deliverables.append(
            Deliverable(
                type=t,
                title=str(d.get("title") or "Deliverable"),
                spec=str(d.get("spec") or ""),
                acceptance=list(d.get("acceptance") or []),
            )
        )

    return Plan(
        thread_id=thread_id,
        business_context=bc,
        stage=str(p.get("stage") or "unknown"),
        constraint=_safe_constraint(str(p.get("constraint") or "unknown")),
        strategy_summary=str(p.get("strategy_summary") or ""),
        frameworks_cited=citations,
        action_steps=steps,
        deliverables=deliverables,
        recommended_route=_safe_route(str(p.get("recommended_route") or "none")),
        risks=list(p.get("risks") or []),
        questions_still_open=list(p.get("questions_still_open") or []),
    )


def extract_preferences(
    message: str,
    history: Optional[list[ChatMessage]] = None,
) -> list[str]:
    """Soft preferences for coach awareness (not hard bans)."""
    texts: list[str] = []
    for m in history or []:
        if m.role == "user":
            texts.append(m.content)
    texts.append(message)
    blob = "\n".join(texts)
    found: list[str] = []
    seen: set[str] = set()
    for pat, label in _PREFERENCE_PATTERNS:
        if pat.search(blob) and label not in seen:
            seen.add(label)
            found.append(label)
    return found


# Back-compat alias for tests
def extract_hard_constraints(
    message: str,
    history: Optional[list[ChatMessage]] = None,
) -> list[str]:
    return extract_preferences(message, history)


# Positive intent phrases (matched anywhere — not full-string exact only)
_CONFIRM_PHRASES = re.compile(
    r"(?:"
    r"\blgtm\b"
    r"|\blooks?\s+good\b"
    r"|\bsounds?\s+good\b"
    r"|\bgood\s+to\s+(go|me)\b"
    r"|\bworks?\s+for\s+me\b"
    r"|\bi'?m\s+(good|in|happy|fine)\b"
    r"|\bhappy\s+with\s+(this|it|the\s+plan)\b"
    r"|\bship\s*it\b"
    r"|\block(\s+it|\s+the\s+plan)?\b"
    r"|\bgo\s*ahead\b"
    r"|\blet'?s\s+go\b"
    r"|\bdo\s*it\b"
    r"|\bapproved?\b"
    r"|\bconfirm(ed)?\b"
    r"|\bproceed\b"
    r"|\bexecute\b"
    r"|\bhand\s*off\b"
    r"|\bsend\s+(it\s+)?to\s+(the\s+)?(builder|copy|both)\b"
    r"|\bstart\s+build(ing)?\b"
    r"|\broute\s+(it|to)\b"
    r"|\breach\s+out\s+to\s+(the\s+)?(builder|copy)\b"
    r"|\bi\s+like\s+(this|the)\s+plan\b"
    r"|\bthis\s+(plan\s+)?(is\s+)?(good|great|solid|fine|perfect)\b"
    r"|\bperfect\b"
    r"|\bgo\s+for\s+it\b"
    r"|\byes\s+please\b"
    r"|\bok(ay)?\s*,?\s*(go|ship|lock|proceed|looks)\b"
    r")",
    re.I,
)

# Bare short tokens that only count as confirm if the message is tiny
_CONFIRM_SHORT = re.compile(
    r"^\s*(go|yes|yep|yeah|yup|ok|okay|k|lgtm|ship|lock|proceed|confirm|"
    r"approved?|perfect|do\s*it|ship\s*it)\s*[.!]?\s*$",
    re.I,
)

# Negations / still-editing — never treat as lock
_CONFIRM_NEG = re.compile(
    r"(?:"
    r"\b(not|don'?t|do\s+not|never|nope|nah)\b.{0,40}\b(good|go|lock|ship|approve|confirm|looks)\b"
    r"|\b(change|revise|tweak|edit|update|wrong|hate|wait)\b"
    r"|\bnot\s+yet\b"
    r"|\bhold\s+on\b"
    r"|\bone\s+more\b"
    r"|\bbut\s+also\b"
    r"|\bexcept\b"
    r"|\bwhat\s+about\b"
    r"|\?\s*$"  # questions usually not locks
    r")",
    re.I,
)


def is_plan_confirmation(message: str) -> bool:
    """
    Detect plan-lock intent from natural language.

    Not pure LLM judgment (fast + deterministic server-side), but **phrase-based
    and flexible** — full sentences like "ok looks good to me, go ahead" count.
    Exact single words only when the whole message is short.
    """
    m = (message or "").strip()
    if not m:
        return False
    # Long essays are almost never pure "lock it"
    if len(m) > 280:
        return False
    # "try again" / redo is NOT a plan lock — it's retry intent
    if re.search(r"\b(try\s*again|retry|redo|regenerate|re-?run)\b", m, re.I):
        return False
    if _CONFIRM_NEG.search(m):
        # Allow "looks good" even if somewhere else has soft words unless clear reject
        if re.search(r"\b(not|don'?t|nope|nah|wrong|change|revise)\b", m, re.I):
            return False
    if _CONFIRM_SHORT.match(m):
        return True
    if _CONFIRM_PHRASES.search(m):
        return True
    return False


def is_mock_or_demo_request(message: str) -> bool:
    """User wants a fictional/sample plan without providing their business facts."""
    m = message or ""
    if re.search(
        r"\b(mock|sample|demo|fictional|example)\b.{0,40}\b(plan|data|business|scenario)\b",
        m,
        re.I,
    ):
        return True
    if re.search(
        r"\b(create|generate|show|give|make|write)\b.{0,30}\b(mock|sample|demo)\b",
        m,
        re.I,
    ):
        return True
    if re.search(r"\bmock\s+data\b", m, re.I):
        return True
    return False


def is_regenerate_request(message: str) -> bool:
    """User wants a fresh plan generation (not intake restart)."""
    m = message or ""
    return bool(
        re.search(
            r"\b(try\s*again|retry|redo|regenerate|re-?do|start\s+over|again)\b",
            m,
            re.I,
        )
    )
    return False


def _infer_stage_hint(message: str, history: Optional[list[ChatMessage]]) -> str:
    blob = " ".join(
        [m.content for m in (history or []) if m.role == "user"] + [message]
    ).lower()
    m = re.search(r"\bstage\s*([0-9])\b", blob)
    if m:
        return m.group(1)
    if re.search(r"\b(improvise|nothing to sell|work for free|starting out)\b", blob):
        return "0"
    if re.search(r"\b(first\s*customers?|monetize|first\s*paid)\b", blob):
        return "1"
    if re.search(r"\b(rule of 100|youtube every day|content machine)\b", blob):
        return "2"
    return ""


def _playbook_queries_for(message: str, stage_hint: str) -> list[str]:
    """Route problem language → playbook retrieval (mirrors Playbooks-Index / Query-Router)."""
    m = message.lower()
    qs: list[str] = []
    mapping = [
        (r"\b(hook|scroll|thumbnail|first line|youtube open)\b", "Playbook-Hooks hooks first line stop scroll"),
        (r"\b(ad|ads|creative|paid)\b", "Playbook-Goated-Ads ad assembly creative"),
        (r"\b(proof|testimonial|case study|credibility)\b", "Playbook-Proof testimonials proof stack"),
        (r"\b(clos|sales call|book a call|appointment|cal\.com|calendly)\b", "Playbook-Closing CLOSER sales call"),
        (r"\b(nurture|follow[- ]?up|email sequence)\b", "Playbook-Lead-Nurture follow up"),
        (r"\b(price|pricing|charge)\b", "Playbook-Pricing price value"),
        (r"\b(cash|broke|runway)\b", "Playbook-Fast-Cash quick cash"),
        (r"\b(ltv|lifetime|upsell)\b", "Playbook-Lifetime-Value LTV"),
        (r"\b(churn|retention|cancel)\b", "Playbook-Retention churn"),
        (r"\b(brand|positioning|associate with)\b", "Playbook-Branding brand positioning"),
        (r"\b(no[- ]?show|reminder|automation|agent)\b", "Lead Magnet Playbook-Lead-Nurture reminders systems"),
        (r"\b(content|youtube|organic)\b", "Core Four content Rule of 100 Playbook-Hooks"),
    ]
    for pat, q in mapping:
        if re.search(pat, m):
            qs.append(q)
    if stage_hint in ("0", "1"):
        qs.append("Lead Magnet free Grand Slam Offer Stage 0 1 implementation track")
    if stage_hint == "2":
        qs.append("Core Four Rule of 100 Playbook-Hooks Stage 2 Advertise")
    if not qs:
        qs.append("Playbooks Index when to use hooks closing lead nurture pricing")
    return qs[:4]


def _dedupe_hits(hits: list[dict[str, Any]], limit: int = 12) -> list[dict[str, Any]]:
    seen: set[tuple] = set()
    out: list[dict[str, Any]] = []
    for h in hits:
        key = (
            (h.get("metadata") or {}).get("source_path"),
            (h.get("text") or "")[:80],
        )
        if key in seen:
            continue
        seen.add(key)
        out.append(h)
        if len(out) >= limit:
            break
    return out


def _path_rank(path: str) -> int:
    """Lower = more preferred in the mixed retrieval pack."""
    p = path.replace("\\", "/")
    if "01-Scaling-Stages" in p or re.search(r"Stage-\d", p):
        return 0
    if "Implementation-Workshop" in p or "Summary-Scaling-Roadmap" in p:
        return 1
    if "04-MOCs" in p or "Query-Router" in p or "Playbooks-Index" in p:
        return 2
    if "02-Playbooks" in p or "Playbook-" in p:
        return 3
    if "00-Core-Frameworks" in p:
        return 4
    return 5


def _retrieve_context(
    message: str,
    history: Optional[list[ChatMessage]],
    preferences: list[str],
    stage_hint: str,
) -> list[dict[str, Any]]:
    """
    Balanced retrieval:
    stages + implementation workshop + playbooks + frameworks.
    """
    store = get_store()
    hits: list[dict[str, Any]] = []

    # Stage spine
    stage_queries = [STAGE_QUERY, "Scaling-Roadmap-Overview which frameworks by stage"]
    if stage_hint:
        stage_queries.append(
            f"Stage {stage_hint} primary constraint what to do Stage-{stage_hint}"
        )
    else:
        stage_queries.append("Stage 0 Improvise Stage 1 Monetize free proof product")

    for q in stage_queries:
        hits.extend(store.query("hormozi", q, n_results=3))

    # Implementation workshop (explicit)
    hits.extend(store.query("hormozi", WORKSHOP_QUERY, n_results=4))
    hits.extend(
        store.query(
            "hormozi",
            "Summary-Implementation-Workshop Track A Stage 0 1 free lead magnet",
            n_results=3,
        )
    )

    # Playbooks routed by problem language
    for q in _playbook_queries_for(message, stage_hint):
        hits.extend(store.query("hormozi", q, n_results=3))

    # User message + recent context
    queries = [message[:600]]
    if history:
        last_users = [m.content for m in history if m.role == "user"][-3:]
        if last_users:
            queries.append(" ".join(last_users + [message])[:700])
    if any("content" in p.lower() or "outreach" in p.lower() for p in preferences):
        queries.append(
            "Core Four content Rule of 100 Lead Magnet free content inbound "
            "Playbook-Hooks YouTube CTA"
        )
    for q in queries:
        hits.extend(store.query("hormozi", q, n_results=4))

    # Core amplifiers
    hits.extend(
        store.query(
            "hormozi",
            "Grand Slam Offer Value Equation Lead Magnet Rule of 100 Core Four",
            n_results=3,
        )
    )

    def sort_key(h: dict[str, Any]) -> tuple:
        path = str((h.get("metadata") or {}).get("source_path") or "")
        dist = h.get("distance") if h.get("distance") is not None else 1.0
        return (_path_rank(path), float(dist))

    hits = sorted(hits, key=sort_key)
    return _dedupe_hits(hits, limit=12)


def run_strategist(
    message: str,
    *,
    thread_id: Optional[str] = None,
    history: Optional[list[ChatMessage]] = None,
) -> dict[str, Any]:
    """
    Returns dict with keys: thread_id, reply, plan, awaiting_approval, status, error?
    """
    tid = thread_id or str(uuid.uuid4())
    history = history or []

    prefs = extract_preferences(message, history)
    stage_hint = _infer_stage_hint(message, history)
    hits = _retrieve_context(message, history, prefs, stage_hint)
    pinned = _load_pinned_guidance()
    rag_block = _format_rag_hits(hits)

    system = SYSTEM_BASE
    if pinned:
        system += (
            "\n\n## PINNED VAULT GUIDANCE (Query Router + Implementation Workshop + indexes)\n"
            "Use this for when-to-use playbooks and sequencing. Cite real file names.\n\n"
            + pinned
        )

    messages: list[dict[str, str]] = [{"role": "system", "content": system}]

    for m in history[-16:]:
        if m.role in ("user", "assistant"):
            cap = 5000 if m.role == "user" else 2200
            messages.append({"role": m.role, "content": m.content[:cap]})

    prefs_block = (
        "\n".join(f"- {p}" for p in prefs)
        if prefs
        else "- (none detected — still listen carefully to this turn)"
    )
    stage_block = (
        f"Likely stage from conversation: **Stage {stage_hint}**. Confirm with stage files."
        if stage_hint
        else "Infer stage from symptoms (01-Scaling-Stages + Scaling-Roadmap-Overview)."
    )

    confirm = is_plan_confirmation(message)
    wants_mock = is_mock_or_demo_request(message)
    wants_regen = is_regenerate_request(message)
    confirm_block = ""
    if confirm:
        confirm_block = (
            "## USER CONFIRMED THE PLAN (LOCK NOW) — CRITICAL\n"
            "User said a short go-ahead (go / lgtm / yes / ship it / etc.).\n"
            "DO NOT restate the full strategy. DO NOT repeat the 14-day list.\n"
            "DO NOT ask 'does this look right' again.\n"
            "You MUST:\n"
            "1. ready_for_plan=true, awaiting_more_context=false\n"
            "2. recommended_route=both (or build if only systems; copy if only copy)\n"
            "3. Fill plan JSON completely FROM PRIOR TURNS (stage, constraint, "
            "strategy_summary, action_steps, deliverables, frameworks_cited)\n"
            "4. reply = 2–4 short lines ONLY, e.g.:\n"
            "   **Plan locked.** Open **Plan** in the sidebar → hit "
            "**Builder Agent** and/or **Copywriting Agent**.\n"
            "No more coaching paragraphs.\n\n"
        )
    elif wants_mock or (wants_regen and wants_mock):
        confirm_block = (
            "## MOCK / DEMO PLAN REQUEST — CRITICAL\n"
            "User wants a MOCK plan with invented data. DO NOT ask intake questions "
            "(what do you sell, headcount, revenue, frustration).\n"
            "Immediately invent one fictional Stage 0–1 business and fill the FULL plan JSON.\n"
            "ready_for_plan=true, awaiting_more_context=false, recommended_route=both.\n"
            "reply: short intro that it's mock + key diagnosis + point them to Plan sidebar.\n"
            "Vary the fictional business each time (don't always use the same niche).\n\n"
        )
    elif wants_regen:
        confirm_block = (
            "## REGENERATE / TRY AGAIN\n"
            "User wants a fresh plan. DO NOT restart with blank intake questions if prior "
            "turns or a mock request already gave signals. Rebuild a complete plan now.\n"
            "If they also want mock data, invent a new fictional business.\n"
            "ready_for_plan=true when the plan body is complete.\n\n"
        )

    user_payload = (
        f"{confirm_block}"
        f"## COACH NOTES — user preferences / resistances (not hard bans)\n"
        f"{prefs_block}\n"
        f"Acknowledge, explore why if needed, recommend a path they'll run. "
        f"Name Hormozi tradeoffs. Do not ignore and do not robotic-ban.\n\n"
        f"## STAGE + IMPLEMENTATION PRIORITY\n{stage_block}\n"
        f"1) Stage + constraint  2) Implementation Workshop sequence  "
        f"3) One framework + one playbook tactic  4) Respect energy/preferences.\n\n"
        f"## Retrieved vault chunks (stages / workshop / playbooks / frameworks)\n"
        f"{rag_block}\n\n"
        f"## Latest user message\n{message}\n\n"
        f"## This turn\n"
        f"- Respond to THIS message like a live coach — not a recycled template.\n"
        f"- Never re-paste the same intake questionnaire if they asked for mock/demo/redo.\n"
        f"- If they corrected you, update the plan and say what changed.\n"
        f"- Cite stage + workshop and/or a playbook when giving steps.\n"
        f"- Put preferences into plan.business_context.constraints_stated as short notes.\n"
        f"- If they confirmed (lgtm etc.), LOCK the plan — do not keep coaching.\n"
    )
    messages.append({"role": "user", "content": user_payload})

    try:
        # Slightly warmer for coach feel; higher for mock variety
        temp = 0.42 if wants_mock else 0.32
        raw = chat_completion(messages, temperature=temp, max_tokens=3200)
    except DeepSeekError as e:
        cites = []
        for h in hits[:4]:
            meta = h.get("metadata") or {}
            cites.append(
                Citation(
                    name=str(meta.get("title") or meta.get("filename") or "source"),
                    file=str(meta.get("source_path") or ""),
                    why="Retrieved while DeepSeek unavailable",
                )
            )
        plan = Plan(
            thread_id=tid,
            strategy_summary="LLM call failed; showing retrieved context only.",
            frameworks_cited=cites,
            questions_still_open=["Retry after verifying DEEPSEEK_API_KEY / network."],
            recommended_route=Route.none,
            business_context=BusinessContext(
                constraints_stated=[p.split(".")[0][:120] for p in prefs]
            ),
        )
        return {
            "thread_id": tid,
            "reply": f"**Strategist error talking to DeepSeek:** {e}\n\nRetrieved files:\n"
            + "\n".join(f"- {c.file or c.name}" for c in cites),
            "plan": plan,
            "awaiting_approval": False,
            "status": "error",
            "error": str(e),
        }

    try:
        data = extract_json_object(raw)
    except Exception:
        plan = Plan(
            thread_id=tid,
            strategy_summary=raw[:500],
            frameworks_cited=[
                Citation(
                    name=str((h.get("metadata") or {}).get("title") or ""),
                    file=str((h.get("metadata") or {}).get("source_path") or ""),
                    why="RAG context provided to model",
                )
                for h in hits[:4]
            ],
            recommended_route=Route.none,
            questions_still_open=[],
            raw_assistant_notes="Model did not return valid JSON; reply is raw text.",
            business_context=BusinessContext(
                constraints_stated=[p.split(".")[0][:120] for p in prefs]
            ),
        )
        return {
            "thread_id": tid,
            "reply": raw,
            "plan": plan,
            "awaiting_approval": False,
            "status": "chatting",
        }

    reply = str(data.get("reply") or raw)
    plan = _parse_plan(data, tid)

    # Merge preferences into plan notes if model omitted them
    existing = list(plan.business_context.constraints_stated or [])
    for p in prefs:
        short = p.split(".")[0][:120]
        if not any(short[:32].lower() in x.lower() for x in existing):
            existing.append(short)
    # Also honor model-declared preferences_noted
    for p in data.get("preferences_noted") or []:
        s = str(p)[:120]
        if s and not any(s[:32].lower() in x.lower() for x in existing):
            existing.append(s)
    plan.business_context.constraints_stated = existing

    ready = bool(data.get("ready_for_plan"))
    awaiting = bool(data.get("awaiting_more_context"))

    def _infer_route_from_text(*texts: str) -> Route:
        blob = " ".join(texts).lower()
        wants_build = bool(
            re.search(
                r"\b(builder|n8n|automation|open[- ]?source|workflow|system|implement)\b",
                blob,
            )
        )
        wants_copy = bool(
            re.search(
                r"\b(copywriting|headline|hooks?|landing page|video description|gumroad copy)\b",
                blob,
            )
        )
        if wants_build and wants_copy:
            return Route.both
        if wants_build:
            return Route.build
        if wants_copy:
            return Route.copy
        return Route.both

    def _reply_looks_like_execution_plan(text: str) -> bool:
        t = (text or "").lower()
        hits = 0
        for needle in (
            "deliverable",
            "acceptance criteria",
            "implementation sequence",
            "build order",
            "recommended_route",
            "action steps",
            "execution plan",
            "owner:",
            "builder agent",
        ):
            if needle in t:
                hits += 1
        return hits >= 2

    # Server-side lock: user said go / lgtm / yes / etc.
    user_confirmed = is_plan_confirmation(message)
    reply_is_plan_early = _reply_looks_like_execution_plan(reply)
    has_meat_early = bool(
        (plan.strategy_summary and len(plan.strategy_summary.strip()) > 40)
        and (bool(plan.action_steps) or bool(plan.deliverables))
    )
    # Mock / regen: force plan-ready path (LLM fills body; we force flags)
    if wants_mock or (wants_regen and (wants_mock or has_meat_early or reply_is_plan_early)):
        ready = True
        awaiting = False
        if plan.recommended_route == Route.none and (
            has_meat_early or reply_is_plan_early or wants_mock
        ):
            plan.recommended_route = Route.both
        # If mock response fell into intake form, replace with a clear instruction for next model...
        # (we still prefer real LLM plan body when present)
        if wants_mock and re.search(
            r"what do you sell|how many people|monthly revenue|biggest frustration",
            reply or "",
            re.I,
        ):
            # Soft fallback: keep coaching tone but tell UI we need a real plan body —
            # force another generation path via summary from any prior mock content
            last_a = ""
            for m in reversed(history or []):
                if m.role == "assistant" and m.content:
                    last_a = m.content.strip()
                    break
            if last_a and len(last_a) > 200 and not re.search(
                r"what do you sell|how many people are on the team", last_a, re.I
            ):
                plan.strategy_summary = plan.strategy_summary or last_a[:1600]
                reply = (
                    "Regenerating from the prior mock plan. Open **Plan** to review, "
                    "or ask me to invent a **different** mock business."
                )

    if user_confirmed:
        ready = True
        awaiting = False
        hist = " ".join(
            m.content for m in (history or []) if m.role in ("user", "assistant")
        )
        # Prefer last assistant plan content as strategy_summary if model re-dumped empty/thin
        last_assistant = ""
        for m in reversed(history or []):
            if m.role == "assistant" and (m.content or "").strip():
                last_assistant = m.content.strip()
                break
        if plan.recommended_route == Route.none:
            plan.recommended_route = _infer_route_from_text(hist, message, reply, last_assistant)
        # Ensure minimum plan body from PRIOR turns only — never inject a fixed business niche
        if not plan.strategy_summary or len(plan.strategy_summary.strip()) < 40:
            seed = last_assistant[:1800] if last_assistant else ""
            plan.strategy_summary = seed or (
                (reply or "")[:1200]
                or "Plan confirmed from prior conversation — review steps in Plan view."
            )
        if not plan.action_steps:
            # Generic routing steps only (LLM should have filled real ones)
            plan.action_steps = [
                ActionStep(
                    step=1,
                    action="Review strategy_summary and refine the primary constraint move this week",
                    owner="user",
                ),
                ActionStep(
                    step=2,
                    action="Route specialists from Plan view (Copywriting / Builder / Both)",
                    owner="user",
                ),
            ]
        if not plan.deliverables:
            plan.deliverables = [
                Deliverable(
                    type=DeliverableType.copy,
                    title="Copy pack from approved strategy",
                    spec="Hooks, page/email, or script drafts matching the plan",
                    acceptance=["Paste-ready drafts"],
                ),
                Deliverable(
                    type=DeliverableType.build,
                    title="Implementation pack from approved strategy",
                    spec="Checklist / blueprint matching the plan's primary move",
                    acceptance=["Actionable steps"],
                ),
            ]
        if plan.stage in ("", "unknown"):
            plan.stage = "0"
        if plan.constraint == Constraint.unknown:
            plan.constraint = Constraint.product
        # Prefer short model handoff; only override if the reply is still a long re-plan dump
        if len(reply or "") > 600 or re.search(
            r"what do you sell|how many people|monthly revenue|biggest frustration",
            reply or "",
            re.I,
        ):
            reply = (
                "**Plan locked.** Open **Plan** in the sidebar → review → route to "
                "**Copywriting**, **Builder**, or **Both**."
            )

    has_meat = bool(
        (plan.strategy_summary and len(plan.strategy_summary.strip()) > 40)
        and (bool(plan.action_steps) or bool(plan.deliverables))
    )
    # Model wrote a full execution plan in the reply but forgot flags
    reply_is_plan = _reply_looks_like_execution_plan(reply)

    # Explicit "generate/mock/show plan" requests — treat as handoff intent
    user_asked_for_plan = bool(
        wants_mock
        or re.search(
            r"\b("
            r"(mock|sample|demo)\s+(plan|data)"
            r"|generate\s+(a\s+)?(mock\s+|sample\s+|demo\s+)?plan"
            r"|(show|create|write|draft|give|make)\s+(me\s+)?(a\s+)?(the\s+)?"
            r"(full\s+|execution\s+|mock\s+|sample\s+)?plan"
            r"|show\s+me\s+the\s+plan"
            r"|lock\s+(the\s+)?plan"
            r")\b",
            message or "",
            re.I,
        )
    )

    # Force plan-ready when we clearly have something to approve
    if not ready and (has_meat or reply_is_plan) and (not awaiting or user_asked_for_plan):
        ready = True
        if user_asked_for_plan:
            awaiting = False
    if not ready and has_meat and not plan.questions_still_open:
        # Enough structure, no open questions → stop chatting loops
        ready = True
        awaiting = False
    # CRITICAL: ready_for_plan must win over awaiting_more_context.
    # Model often sets both true for mock/full plans → used to fall through to
    # status=chatting and the UI never auto-opened Plan (PC/phone flake).
    if ready and has_meat:
        awaiting = False
    if ready and plan.recommended_route == Route.none and (has_meat or reply_is_plan):
        hist = " ".join(
            m.content for m in (history or []) if m.role in ("user", "assistant")
        )
        plan.recommended_route = _infer_route_from_text(hist, message, reply)

    # If reply is a full plan but JSON plan is thin, seed minimum fields
    if reply_is_plan and not has_meat:
        if not plan.strategy_summary:
            plan.strategy_summary = reply[:1200]
        if not plan.action_steps:
            plan.action_steps = [
                ActionStep(
                    step=1,
                    action="Execute the approved plan in the Plan view (route specialists)",
                    owner="build",
                )
            ]
        if plan.recommended_route == Route.none:
            plan.recommended_route = _infer_route_from_text(reply, message)
        has_meat = True
        ready = True
        awaiting = False

    if user_asked_for_plan and (has_meat or reply_is_plan):
        ready = True
        awaiting = False
        if plan.recommended_route == Route.none:
            plan.recommended_route = Route.both

    # Mock request with any plan summary → force plan_ready even if steps lag
    if wants_mock and plan.strategy_summary and len(plan.strategy_summary.strip()) > 40:
        ready = True
        awaiting = False
        has_meat = has_meat or bool(plan.action_steps or plan.deliverables)
        if not plan.action_steps:
            plan.action_steps = [
                ActionStep(
                    step=1,
                    action="Execute the mock plan via Plan → Copywriting / Builder",
                    owner="user",
                )
            ]
        if not plan.deliverables:
            plan.deliverables = [
                Deliverable(
                    type=DeliverableType.copy,
                    title="Mock copy pack",
                    spec="Drafts matching the mock strategy",
                    acceptance=["Paste-ready"],
                ),
                Deliverable(
                    type=DeliverableType.build,
                    title="Mock implementation pack",
                    spec="Checklist matching the mock strategy",
                    acceptance=["Actionable"],
                ),
            ]
        has_meat = True
        if plan.recommended_route == Route.none:
            plan.recommended_route = Route.both

    # Status decision — ready + meat always opens Plan (no ready∧awaiting limbo)
    if ready and (has_meat or reply_is_plan or plan.recommended_route != Route.none):
        if plan.recommended_route == Route.none:
            plan.recommended_route = Route.both if (has_meat or reply_is_plan) else Route.build
        status = "plan_ready"
        awaiting_approval = True
    elif has_meat and plan.recommended_route != Route.none:
        # Belt-and-suspenders: meaty plan always opens approval
        status = "plan_ready"
        awaiting_approval = True
        ready = True
    elif wants_mock and (has_meat or reply_is_plan or (plan.strategy_summary or "").strip()):
        status = "plan_ready"
        awaiting_approval = True
        if plan.recommended_route == Route.none:
            plan.recommended_route = Route.both
    elif awaiting and not ready:
        status = "chatting"
        awaiting_approval = False
    else:
        status = "chatting"
        awaiting_approval = False

    # Model claimed lock without flags — still open approval
    if re.search(
        r"plan\s*locked|open\s+\*?\*?plan\*?\*?|hit\s+(the\s+)?(builder|copywriting)",
        reply or "",
        re.I,
    ):
        awaiting_approval = True
        status = "plan_ready"
        if plan.recommended_route == Route.none:
            plan.recommended_route = Route.both
        if not plan.strategy_summary or len(plan.strategy_summary.strip()) < 20:
            last_a = ""
            for m in reversed(history or []):
                if m.role == "assistant" and m.content:
                    last_a = m.content.strip()
                    break
            plan.strategy_summary = (last_a or reply)[:1800]
        if not plan.action_steps:
            plan.action_steps = [
                ActionStep(
                    step=1,
                    action="Review plan in Plan view and route to Builder and/or Copywriting",
                    owner="user",
                )
            ]

    # Hard guarantee: user confirm always yields approvable plan
    if user_confirmed:
        awaiting_approval = True
        status = "plan_ready"
        if plan.recommended_route == Route.none:
            plan.recommended_route = Route.both

    # Always tip the user when approval is open
    if awaiting_approval:
        tip = (
            "\n\n---\n"
            "**Next:** Open **Plan** in the sidebar to review and approve — "
            "then route to **Copywriting Agent**, **Builder Agent**, or **Both**."
        )
        if "open **plan**" not in reply.lower() and "sidebar" not in reply.lower():
            reply = reply.rstrip() + tip

    return {
        "thread_id": tid,
        "reply": reply,
        "plan": plan,
        "awaiting_approval": bool(awaiting_approval),
        "status": status,
    }
