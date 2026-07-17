# Business OS

**Multi-agent business operating system** — turn a vague constraint into a locked plan and specialist-generated artifacts.

| | |
|---|---|
| **Live demo** | [app.deekshak.site](https://app.deekshak.site) |
| **Portfolio** | [deekshak.site](https://deekshak.site) |
| **Author** | [Deekshak SS](https://deekshak.site) · AI implementation / orchestration |

---

## What it does

```
User chat  →  Strategist (RAG)  →  Plan lock + human approval
                                      ↓
                         Copywriting + Builder specialists
                                      ↓
                         Paste-ready outputs (not token dumps)
```

Built for roles and teams that care about **production loops**, not notebook demos.

## Stack

| Layer | Tech |
|-------|------|
| Web UI | React + Vite · Vercel |
| API | FastAPI · Modal |
| Strategist | LLM + RAG over your knowledge vaults |
| Agents | Strategist · Copywriter · Builder · Executor |
| Data | Chroma (local / Modal volume) |

## Repo layout

```
apps/web/          # Product UI (chat, pipeline, plan, agents, outputs)
services/api/      # FastAPI app, agents, RAG, Modal deploy
docs/              # Design notes & continuity
evals/             # Evaluation helpers
scripts/           # Utility scripts
knowledge/         # Place your own RAG sources (not shipped)
```

## Quick start (local API)

```powershell
cd services/api
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env   # add OPENROUTER_API_KEY or DEEPSEEK_API_KEY
# Optionally put markdown/docs under knowledge/ and run ingest
python -m app.rag.ingest
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

API docs: http://127.0.0.1:8000/docs

## Quick start (web)

```powershell
cd apps/web
npm install
# set VITE_API_URL to your API base
npm run dev
```

Production web: configure `VITE_API_URL` for the deployed Modal/API URL, then:

```powershell
npm run build
# deploy dist/ (Vercel project already used for app.deekshak.site)
```

## Environment

See `services/api/.env.example`. **Never commit real keys.**

| Variable | Purpose |
|----------|---------|
| `OPENROUTER_API_KEY` / `DEEPSEEK_API_KEY` | LLM access |
| `LLM_BASE_URL` / `LLM_MODEL` | Provider routing |
| `XAI_API_KEY` | Optional Grok-related tooling |

## Modal deploy

```powershell
cd services/api
modal secret create business-os-secrets OPENROUTER_API_KEY=<your-key>
modal deploy modal_app.py
```

## Security

- `.env` and local vector DBs are gitignored  
- Knowledge vaults with third-party copyrighted material are **not** included  
- Rotate any key that ever appeared in a local-only file  

## License

MIT for original code in this repository.  
Live product branding © Deekshak SS. Third-party models and APIs subject to their terms.
