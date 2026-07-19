# Hormozi Business Strategist

Distilled, RAG-optimized knowledge vault for a **Business Strategist agent** in AnythingLLM. Built from Alex Hormozi’s core books, playbooks, and the $100M Scaling Roadmap (Stages 0–9).

**Not raw books.** Stories and filler are stripped. Files keep formulas, processes, constraints, checklists, and “when to use” guidance.

---

## Folder map

| Folder | Purpose |
|--------|---------|
| `00-Core-Frameworks/` | Universal tools (Value Equation, Grand Slam Offer, Core Four, Money Models, etc.) |
| `01-Scaling-Stages/` | Stages 0–9: theme, headcount, constraints, graduation criteria |
| `02-Playbooks/` | Actionable implementation guides (hooks, ads, closing, pricing, etc.) |
| `03-Transcripts-Summaries/` | Distilled workshop / course summaries |
| `04-MOCs/` | Maps of Content — indexes and query router (start here mentally) |
| `05-Examples-Case-Studies/` | Short formula applications only (if needed) |

Root files:

- `AGENT-SCHEMA.md` — paste into AnythingLLM **system prompt** (or keep embedded)
- `README.md` — this file

---

## How to load into AnythingLLM

1. Create a new workspace: **Hormozi Business Strategist**
2. Upload **this entire folder** (distilled MD only — do **not** also upload the Desktop raw dump)
3. Workspace settings (recommended start):
   - Vector search preference: **Accuracy Optimized** (reranking) if using LanceDB
   - **Max Context Snippets:** 6–8
   - If answers miss relevant docs: lower **Document similarity threshold** or try **No Restriction**
4. Paste the system prompt from `AGENT-SCHEMA.md` into the workspace system prompt
5. Optional: **Pin** only small navigation hubs if needed:
   - `04-MOCs/Query-Router.md`
   - `04-MOCs/Scaling-Roadmap-Overview.md`  
   Do **not** pin full books or large playbooks.

---

## How the agent should think

1. Identify **stage** (0–9) and **constraint** (product / marketing / sales / CS / etc.)
2. Select **framework(s)** and **playbook(s)** that match
3. Answer with formulas + steps + constraints
4. **Cite** source file names and framework names
5. Never invent generic startup advice outside this vault

See `04-MOCs/Query-Router.md` for “if user says X → open Y.”

---

## Source inventory (v1)

| Included | Source location |
|----------|-----------------|
| $100M Offers (cleaned) | Desktop `Alex and Leila/Books` |
| $100M Leads (cleaned) | same |
| $100M Money Models (cleaned) | same |
| Offer checklists / related books PDFs (distilled) | same |
| Playbooks (12+) | Desktop `Alex and Leila/Playbooks` |
| Scaling Roadmap Stages 0–9 (full) | Desktop `Alex and Leila/Other Files` complete transcript |
| Implementation Workshop (distilled) | same |

| Excluded (by design) |
|----------------------|
| Hormozi’s Mind (mindset podcasts) |
| Content masterclass 3hrs |
| Apify channel scrapes / Leila video dumps |
| Full raw book/transcript dumps in this vault |

---

## File conventions

Every content file has YAML frontmatter:

- `type`: framework | stage | playbook | summary | moc | example  
- `source`, `stage`, `tags`, `keywords`, `summary`, `when_to_use`

Naming: `Value-Equation.md`, `Stage-3-Stabilize.md`, `Playbook-Hooks.md`, etc.

---

## Related project

**CopyOS** (`H:\Copy OS`) remains a separate workspace for deep copywriting craft. This vault is **business strategy + Hormozi acquisition systems**, not a full DR copy OS.
