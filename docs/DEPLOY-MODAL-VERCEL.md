# Deploy: Modal (API) + Vercel (UI) → app.deekshak.site

No signups / no user DB for v1. OpenRouter key stays **only** on Modal.

## Live status

| Layer | URL | Status |
|-------|-----|--------|
| **API (Modal)** | https://deekshakdk11--bizos-api.modal.run | Deployed · health OK · OpenRouter Flash |
| **RAG index** | Modal volume `business-os-chroma` | Hormozi + CopyOS ingested |
| **UI (Vercel)** | https://app.deekshak.site | Needs `vercel login` + domain DNS (one-time) |

## Architecture

```
Browser  →  https://app.deekshak.site     (Vercel · React)
         →  https://deekshakdk11--bizos-api.modal.run
         →  OpenRouter (server-side only — never in the browser)
```

- `deekshak.site` — portfolio (later)
- `app.deekshak.site` — Business OS

## Commands cheat-sheet

```powershell
# API redeploy after backend changes
cd H:\business-os\services\api
modal deploy modal_app.py

# Re-ingest vaults into Modal Chroma
modal run modal_app.py::bootstrap_index

# Frontend (after vercel login once)
cd H:\business-os\apps\web
$env:VITE_API_URL="https://deekshakdk11--bizos-api.modal.run"
vercel --prod --yes
```

### Domain `app.deekshak.site`

1. Vercel project → **Domains** → add `app.deekshak.site`
2. DNS:

| Type | Name | Value |
|------|------|--------|
| CNAME | `app` | `cname.vercel-dns.com` (or Vercel’s value) |

## Local development

```powershell
# API
cd H:\business-os\services\api
.\.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000

# Web — do NOT set VITE_API_URL (uses /api proxy)
cd H:\business-os\apps\web
npm run dev
```

## Security (v1 free public demo)

| Control | Detail |
|---------|--------|
| Rate limits | 30 chat / 8 execute / 40 rag / 120 global per IP per hour |
| Input bounds | Max message 6k chars, history 24 turns |
| Prompt injection | Multi-signal jailbreak filter; fake `system` roles stripped |
| CORS | Only app.deekshak.site, deekshak.site, localhost |
| Secrets | OpenRouter only in Modal Secret `business-os-secrets` |
| Headers | nosniff, DENY frame, referrer policy |
| Docs | `/docs` off unless `BIZOS_ENABLE_DOCS=true` |

## Making changes after deploy

Edit files under `H:\business-os` (same as now). Then:

| Change | Redeploy |
|--------|----------|
| React / CSS | `cd apps\web; vercel --prod` |
| API / agents / security | `cd services\api; modal deploy modal_app.py` |
| Vault markdown | `modal run modal_app.py::bootstrap_index` + redeploy API if image embeds vaults |

I still work on your local project; cloud updates only after deploy commands.
