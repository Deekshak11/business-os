# Business OS

**Multi-agent business operating system** — messy request → dense RAG strategist → **human plan lock** → specialist agents → paste-ready artifacts.

[![Live](https://img.shields.io/badge/Live-app.deekshak.site-14b8a6?style=for-the-badge)](https://app.deekshak.site)
[![Portfolio](https://img.shields.io/badge/Portfolio-deekshak.site-0ea5e9?style=for-the-badge)](https://deekshak.site/#flagship)
[![Author](https://img.shields.io/badge/Author-Deekshak%20SS-1e293b?style=for-the-badge)](https://github.com/Deekshak11)

> Hire-facing flagship. Proves **orchestration**, **approval gates**, **multi-corpus RAG**, and a real product UI — not a notebook demo.

---

## Why this exists

Most business AI chat dumps ideas and stops. Operators still need:

1. A **diagnosed constraint** (not vibes)
2. A **structured plan** a human can approve
3. **Specialists** that produce usable drafts (copy / build), grounded in real methodology

Business OS is that loop, end to end, in production.

| Surface | URL |
|---------|-----|
| **Live product** | https://app.deekshak.site |
| **Portfolio case + walkthrough** | https://deekshak.site/#flagship |
| **This repo** | architecture, API, web shell, deploy |

---

## System architecture

```text
┌──────────────────────────────────────────────────────────────────┐
│  React product shell (Vercel)                                      │
│  Chat · Pipeline · Plan · Agents · Outputs                           │
└────────────────────────────┬─────────────────────────────────────┘
                             │ HTTPS / JSON
┌────────────────────────────▼─────────────────────────────────────┐
│  FastAPI orchestration layer (Modal)                               │
│  · Thread + plan state                                             │
│  · Approval / route (copy | build | both)                          │
│  · Specialist handoff + artifact collection                        │
└───────┬────────────────────┬─────────────────────┬───────────────┘
        │                    │                     │
        ▼                    ▼                     ▼
┌───────────────┐   ┌────────────────┐   ┌─────────────────┐
│  STRATEGIST   │   │  COPYWRITING   │   │    BUILDER      │
│  LLM + RAG    │   │  LLM + RAG     │   │  LLM + plan     │
│  Hormozi vault│   │  Copy OS vault │   │  implementation │
│  diagnose →   │   │  drafts, hooks │   │  blueprints     │
│  plan schema  │   │  after lock    │   │  after lock     │
└───────┬───────┘   └────────┬───────┘   └────────┬────────┘
        │                    │                     │
        ▼                    ▼                     │
┌───────────────────────────────────────┐          │
│  Chroma vector store                   │◄─────────┘
│  embeddings · retrieval · citations    │
└───────────────────────────────────────┘
```

### Control flow (happy path)

```text
User message
    → Strategist (multi-turn, vault-grounded)
    → Plan object (strategy_summary, action_steps, deliverables, route)
    → Awaiting approval (human gate)
    → User chooses Copy / Builder / Both
    → Specialist executors run
    → Artifacts land in Outputs (paste-ready)
    → Pipeline UI reflects stage
```

**Design invariant:** specialists do **not** auto-ship without plan approval. Silent agent chaos is a bug.

---

## Knowledge density (what makes RAG real)

Third-party corpus **content is not shipped** in this public repo (copyright / license hygiene). The **pipeline and architecture** are. On the running product, retrieval is backed by high-density vaults:

### Strategist — Hormozi growth systems

| Dimension | What is loaded |
|-----------|----------------|
| Core | Offers, leads, money models, growth systems |
| Containers | **3** core books + **12** advanced implementation playbooks |
| Shape | Stages, frameworks, diagnostic systems for lead / sales / retention / profit |

### Copy specialist — Copy OS persuasion systems

| Dimension | Scale |
|-----------|------:|
| Vault documents | **14** in-depth docs |
| Named frameworks | **112** |
| Structures / templates | **32** |
| Checklists & QA | **58** (incl. universal laws, stress tests) |
| Swipe / examples | **600+** files |
| Author / source base | **40+** classic and modern (Hopkins, Schwartz, Cialdini, Ogilvy, Kennedy, Brunson, Hormozi, …) |

Portfolio deep-dive: [deekshak.site/#flagship](https://deekshak.site/#flagship) → **Behind the scenes**.

Local operators place their own vault material under paths described in `knowledge/README.md` (never commit secrets or copyrighted dumps to git).

---

## Stack

| Layer | Choice | Role |
|-------|--------|------|
| Web | React + Vite + TypeScript | ChatGPT-like shell, pipeline, plan approval UI |
| API | FastAPI | Threads, plan schema, execute routes |
| Hosting | Modal (API) · Vercel (web) | Production split |
| RAG | Chroma + embeddings | Multi-corpus retrieval |
| LLM | Configurable (OpenRouter / DeepSeek / peers) | Strategist + specialists |
| Contracts | Shared plan JSON schema | Strategist → UI → executors |

---

## Repository map

```text
apps/web/                 Product UI (views: chat, pipeline, plan, agents, outputs)
services/api/
  app/
    agents/               Strategist, copy, build executors, parsing
    rag/                  Ingest + retrieve
    schemas/              Plan contract
    llm/                  Model clients
  modal_app.py            Modal deploy entry
  tests/                  Unit tests (constraints, artifact parse)
docs/                     Continuity, design system, deploy, status
knowledge/                Local vault instructions (no proprietary dump)
evals/                    Evaluation hooks
```

---

## Quick start (local)

```powershell
# API
cd services/api
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env   # set LLM keys
uvicorn app.main:app --reload --port 8000

# Web
cd apps/web
npm install
# VITE_API_URL=http://127.0.0.1:8000
npm run dev
```

Tests:

```powershell
cd services/api
pytest
```

---

## Deploy

| Target | How |
|--------|-----|
| API | `modal deploy services/api/modal_app.py` (secrets in Modal) |
| Web | Vercel · `VITE_API_URL` → public API |

See `docs/DEPLOY-MODAL-VERCEL.md`.

---

## Security model

- No `.env` / keys / tokens in git  
- No client PII  
- **No third-party copyrighted vault dumps** in the public tree  
- `.env.example` documents variables only  

---

## Related systems (same author)

| Repo | Role |
|------|------|
| [agency-os](https://github.com/Deekshak11/agency-os) | Outbound factory · Modal + Workspace |
| [show-rate-guardian](https://github.com/Deekshak11/show-rate-guardian) | No-show risk agent skills |
| [signal-os](https://github.com/Deekshak11/signal-os) | Agentic infra architecture |
| [automation-systems](https://github.com/Deekshak11/automation-systems) | Production n8n graphs (BDR, email RAG, CRM, research) |
| [deekshak-portfolio](https://github.com/Deekshak11/deekshak-portfolio) | Hire site source |

---

## License

MIT for original code in this repository. Methodology corpora remain under their respective rights holders; use your own licensed material for local RAG.
