# GitHub public checklist (no secrets)

Use before any `git push` of Business OS or automation repos.

## 1. Never commit

- `.env`, `.env.local`, `.env.*.local`
- API keys, tokens, webhook secrets
- Client PII, CRM dumps, calendar exports
- `data/chroma/` or other vector stores with private corpus if licensed
- Private Hormozi/knowledge raw dumps if not licensed for public redistribute

## 2. `.gitignore` must include

```
.env
.env.*
**/.env
**/.env.local
**/__pycache__/
.venv/
**/node_modules/
.vercel/
dist/
data/chroma/
*.pyc
```

## 3. Pre-push scan (PowerShell)

From repo root:

```powershell
# Fail if common secret patterns appear outside .env.example
rg -n --hidden -g '!.git' -g '!.env*' -g '!**/node_modules/**' `
  -e 'sk-[a-zA-Z0-9]{10,}' `
  -e 'api[_-]?key\s*=\s*[''"][^''"]+[''"]' `
  -e 'BEGIN (RSA |OPENSSH )?PRIVATE KEY' `
  -e 'xai-[a-zA-Z0-9]{20,}' `
  -e 'AKIA[0-9A-Z]{16}'
```

If anything hits: remove, rotate the key, re-scan.

## 4. README template (every public repo)

1. One-line outcome (business)
2. Problem
3. Architecture (diagram or bullets)
4. Stack
5. Live demo URL
6. Loom walkthrough URL (same as portfolio `links.ts`)
7. How to run locally with `.env.example` only
8. License / contact → deekshak.site

## 5. Pin order (profile)

1. business-os  
2. show-rate / automation  
3. lead-gen  
4. (optional) portfolio site  

## 6. Portfolio link sync

After public URLs exist, set in `H:\portfolio\site\src\lib\links.ts`:

- `github`
- `repos.businessOs` / `showRate` / `leadGen`
- `demos.*` Loom URLs  

Redeploy portfolio.
