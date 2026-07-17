# Business OS

**Multi-agent Business Operating System** — vague constraint → Hormozi-grounded strategist → plan lock → specialist agents → paste-ready artifacts.

| | |
|---|---|
| **Live** | [app.deekshak.site](https://app.deekshak.site) |
| **Portfolio** | [deekshak.site](https://deekshak.site) |
| **Author** | [Deekshak SS](https://deekshak.site) |

---

## Product vision

1. **Strategist** — multi-turn diagnosis with RAG over a methodology vault  
2. **Human approval** — structured plan the user can edit / lock  
3. **Execution specialists**  
   - **Copy** — copy assets from Copy-OS style knowledge  
   - **Build** — implementation tasks / blueprints  

Built as a **hire-ready proof** of orchestration, approval gates, and real UI — not a notebook.

## Architecture

```
React UI (chat · pipeline · plan · agents · outputs)
        ↓
FastAPI API (thread state, plan schema, handoffs)
        ↓
┌─────────────┬──────────────┬─────────────┐
│ Strategist  │  Copywriter  │   Builder   │
│ LLM + RAG   │  LLM + RAG   │  LLM plan   │
└─────────────┴──────────────┴─────────────┘
```

| Layer | Tech |
|-------|------|
| Web | React + Vite · Vercel |
| API | FastAPI · Modal |
| RAG | Chroma + sentence-transformers |
| Orchestration | Plan schema + approval + specialist executors |

Continuity docs: `docs/00-MASTER-PLAN-AND-CONTINUITY.md`, `docs/STATUS.md`, `docs/DESIGN-SYSTEM.md`.

## Repo layout

```
apps/web/           # Product shell
services/api/       # FastAPI, agents, RAG, Modal
docs/               # Plans, design system, deploy notes
evals/              # Evaluation helpers
knowledge/README.md # Place your own vaults (not shipped)
```

## Quick start

```powershell
# API
cd services/api
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env   # OPENROUTER_API_KEY or DEEPSEEK_API_KEY
uvicorn app.main:app --reload --port 8000

# Web
cd apps/web
npm install
# set VITE_API_URL
npm run dev
```

## Deploy

- API: `modal deploy services/api/modal_app.py` (secrets via Modal)  
- Web: Vercel with `VITE_API_URL` pointing at API  

## Security

- Never commit `.env`  
- Knowledge vaults with third-party copyrighted material are **not** in this repo  
- `.env.example` documents required variables only  

## Related projects

| Repo | Role |
|------|------|
| [agency-os](https://github.com/Deekshak11/agency-os) | Outbound factory (Antigravity) |
| [show-rate-guardian](https://github.com/Deekshak11/show-rate-guardian) | No-show agent skills |
| [signal-os](https://github.com/Deekshak11/signal-os) | Agentic infrastructure docs |
| [deekshak-portfolio](https://github.com/Deekshak11/deekshak-portfolio) | Portfolio site |

## License

MIT for original code in this repository.
