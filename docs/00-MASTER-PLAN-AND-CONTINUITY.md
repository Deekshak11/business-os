# Business OS — Master Plan & Continuity Document

**Purpose:** Single source of truth if a chat hits context limits. Start a new chat with:  
> “Continue Business OS from `H:\business-os\docs\00-MASTER-PLAN-AND-CONTINUITY.md`”

**Last updated:** 2026-07-16  
**Project root:** `H:\business-os\`

---

## 1. Product vision

A **Business Operating System** showcase:

1. **Strategist agent** (Hormozi methodology) — multi-turn context questions → structured strategy plan  
2. **Human approval gate** — user edits/approves and chooses route  
3. **Execution agents:**
   - **Copy agent** — Copy-OS RAG → copy assets  
   - **Build agent** — Grok / Grok Build → implementation tasks/code  

**Frontend:** Dashboard (Lovable → export GitHub → edit in OpenDesign)  
**Backend:** Custom (not AnythingLLM product runtime)  
**Knowledge:** Structured MD vaults already built on disk  

---

## 2. What already exists (do not rebuild)

| Asset | Path | Status |
|-------|------|--------|
| Hormozi RAG vault | `H:\Hormozi-Business-Strategist\` | Done — stages 0–9, frameworks, playbooks, MOCs, AGENT-SCHEMA |
| Copy-OS RAG vault | `H:\Copywriting-OS\` (also was `H:\Copy-OS`) | Done — ~433 section files + MOCs + AGENT-SCHEMA |
| Old unstructured Copy OS | `H:\Copy OS\` | **Deleted** |
| Project scaffold | `H:\business-os\` | In progress |
| Knowledge junctions | `H:\business-os\knowledge\hormozi` → Hormozi vault | Linked |
| Knowledge junctions | `H:\business-os\knowledge\copyos` → `H:\Copywriting-OS` | Linked |

---

## 3. Architecture (approved)

```
Frontend (chat, plan card, approve, artifacts)
        │
        ▼
FastAPI + LangGraph orchestrator
  thread_id + checkpointer + interrupt(approval)
        │
   ┌────┴────┬────────────┐
   ▼         ▼            ▼
Strategist  Copy         Build
DeepSeek    DeepSeek     Grok
+ hormozi   + copyos     + plan JSON only
  Chroma      Chroma
```

**Patterns (evidence-based):**
- LangChain multi-agent: Subagents / Handoffs / Custom LangGraph workflow  
- LangGraph `interrupt()` for human-in-the-loop approval  
- Chroma metadata filters for RAG precision  
- OpenAI Agents SDK documents handoffs independently  

See `docs/01-RESEARCH-HOSTING-AND-STACK.md` for claim–evidence.

---

## 4. Shared Plan JSON schema

Every handoff uses this contract (not free-form chat):

```json
{
  "version": "1.0",
  "thread_id": "uuid",
  "business_context": {
    "industry": "",
    "offer": "",
    "headcount": null,
    "revenue_signals": "",
    "goals": "",
    "constraints_stated": []
  },
  "stage": "0-9 or unknown",
  "constraint": "product|marketing|sales|cs|ops|cash|unknown",
  "strategy_summary": "",
  "frameworks_cited": [{"name": "", "file": "", "why": ""}],
  "action_steps": [{"step": 1, "action": "", "owner": "user|copy|build"}],
  "deliverables": [
    {
      "id": "d1",
      "type": "copy|build",
      "title": "",
      "spec": "",
      "acceptance": []
    }
  ],
  "recommended_route": "copy|build|both|none",
  "risks": [],
  "questions_still_open": []
}
```

---

## 5. Implementation phases

| Phase | Work | Status |
|-------|------|--------|
| 0 | Plan schema + continuity docs + repo scaffold | **Active** |
| 1 | RAG ingest + query API (Chroma, two collections) | Next |
| 2 | Strategist agent (DeepSeek + hormozi RAG) | Pending |
| 3 | LangGraph approval interrupt + routing | Pending |
| 4 | Copy executor (DeepSeek + copyos RAG) | Pending |
| 5 | Build executor (Grok handoff package) | Pending |
| 6 | Minimal web UI (local) + pipeline status | Pending |
| 7 | Optional cloud demo deploy | Pending |
| 8 | Portfolio videos + landing page copy | Pending |

---

## 6. Hosting decision (this machine + free cloud)

### PC specs (measured 2026-07-16)

| Component | Value |
|-----------|--------|
| CPU | Intel Core i5-4590T @ 2.00 GHz, 4 cores / 4 threads |
| RAM | 15.9 GB total |
| GPU | Intel HD Graphics 4600 (integrated only) |
| Disk | H: ~90 GB free; vaults on H: |
| Tooling | Python 3.10, Node 22, Docker 29, Windows 10 Enterprise |

### Can we host locally?

| Workload | Fit on this PC? |
|----------|-----------------|
| FastAPI + LangGraph + SQLite checkpointer | **Yes — preferred** |
| Chroma + MiniLM embeddings (CPU) for ~500–2k MD chunks | **Yes** (embed once; query is light) |
| Calling DeepSeek / Grok **APIs** for LLM | **Yes** (network-bound, not GPU) |
| Local 7B+ LLM interactive chat | **No** (CPU too old/slow; no discrete GPU) |
| Concurrent heavy Docker + browser + embed rebuild | Tight; avoid simultaneous heavy jobs |

**Decision:** **Primary = local API + local Chroma**. LLM intelligence via **remote APIs** (DeepSeek + Grok). This is the fastest path for demos (localhost latency, vaults on disk).

### Free / generous cloud (credible sources only)

| Platform | Free / credit (official) | Fit for us |
|----------|---------------------------|------------|
| **Modal Starter** | **$30/month free compute credit**; pay-per-use serverless | Best if we need cloud burst/GPU later; not required for v1 CPU RAG |
| **Google Cloud Run** | Always-free tier: **2M requests/mo** + free vCPU/GiB-seconds (see GCP free tier docs) | Strong for public FastAPI container demo |
| **Hugging Face Spaces** | **CPU Basic free**: 2 vCPU, 16 GB RAM, 50 GB ephemeral disk | Easy portfolio demo UI; free Spaces sleep when idle |
| **Railway** | Free trial **$5 one-time** (docs); Hobby has limited included usage | OK trial, not “always free forever” |
| **Fly.io** | Free trial limited (2 VM hours / 7 days per free trial docs); free allowances historically small | Secondary option |

**Cloud recommendation order:**
1. **Develop local**  
2. **Public demo:** Hugging Face Spaces (free CPU) *or* Cloud Run free tier  
3. **Optional heavy jobs:** Modal ($30 credit)  

Do **not** rely on Railway/Fly as primary free forever hosts.

---

## 7. Model routing (cost)

| Agent | Model | Key |
|-------|--------|-----|
| Strategist | DeepSeek API | `DEEPSEEK_API_KEY` |
| Copy | DeepSeek API | same |
| Build | Grok / xAI or SuperGrok workflow | `XAI_API_KEY` or export pack |
| Embeddings | `sentence-transformers/all-MiniLM-L6-v2` local | free |

---

## 8. Agent system prompts (source files)

- Strategist: `knowledge/hormozi/AGENT-SCHEMA.md`  
- Copy: `knowledge/copyos/AGENT-SCHEMA.md`  
- Router MOCs: respective `04-MOCs` / `05-MOCs` Query-Router files  

---

## 9. Explicit non-goals (v1)

- AnythingLLM as production backend  
- Local large model inference  
- Auto-deploy without approval  
- Merging Hormozi + Copy into one vector collection  
- 6+ agent company simulation  

---

## 10. How to resume in a new chat

Paste:

```
Continue Business OS build from H:\business-os\docs\00-MASTER-PLAN-AND-CONTINUITY.md
Read docs/STATUS.md for current phase and next tasks.
Host: local primary. Vaults linked under knowledge/.
```

---

## 11. Environment secrets (local `.env`, never commit)

```
DEEPSEEK_API_KEY=
XAI_API_KEY=          # optional for build agent
BUSINESS_OS_DATA_DIR=H:\business-os\data
```

---

## 12. Success criteria for portfolio demo

1. Chat with Strategist → clarifying Qs → plan JSON with stage + citations  
2. Approve → route Copy → get headline/email/offer draft grounded in Copy-OS  
3. Approve → route Build → get task list / scaffold package  
4. Screen recording of full pipeline under 5 minutes  
5. Optional public URL on free tier without paying for infra  
