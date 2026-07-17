# Business OS — Live Status

**Date:** 2026-07-16

| Field | Value |
|-------|--------|
| Phase | **Product shell UI** (sidebar + multi-view) |
| Frontend | http://127.0.0.1:5173/ |
| API | http://127.0.0.1:8000/ |
| Status chrome | “All systems live” / “Systems offline” |

## Product UI

- Left sidebar: Chat · Pipeline · Plan · Agents
- Chat: full-height message stream + sticky composer (ChatGPT-like)
- Pipeline: step track strategy→execution with live “Now” panel
- Plan: full plan + approve routes; auto-opens on plan_ready
- Markdown: `**bold**`, lists, headings rendered (not raw stars)
- Brand: portfolio tokens preserved

## Verify

```powershell
cd H:\business-os\apps\web
npm test
npm run dev
```

Evidence: `{SCRATCH}/ui-structure.txt`, `unit-tests.log`, `launch-chat.log`
