# Copy-OS (RAG-Optimized)

Structured copywriting knowledge base for **AnythingLLM**, rebuilt from the original 14-doc Copy OS (`H:\Copy OS`) using the same method as Hormozi Business Strategist:

- Hierarchical folders (strategy → architecture → tactics → systems)
- **Section-level files** (not mega-docs) for precise retrieval
- YAML frontmatter on every file (`type`, `when_to_use`, `parent_doc`, tags)
- MOCs + Query Router + AGENT-SCHEMA

**Originals preserved at:** `H:\Copy OS\` (untouched).  
**This vault:** `H:\Copy-OS\` — upload **this** into AnythingLLM.

---

## Stats

| Item | Count |
|------|--------|
| Source mega-docs | 14 |
| RAG section files | ~412 (+ 14 per-doc indexes) |
| Folders | 00–06 + root agent docs |

---

## Folder map

| Folder | Role |
|--------|------|
| `00-Navigation/` | How to use OS, workflows, glossary |
| `01-Strategic-Foundation/` | Laws, market diagnosis, positioning, offers |
| `02-Copy-Architecture/` | Structures, headlines/leads, bullets |
| `03-Tactical-Execution/` | Proof, language, funnels/email, objections |
| `04-Systems-Optimization/` | Testing, metrics, contexts, swipes/templates |
| `05-MOCs/` | Indexes + Query Router (brain) |
| `06-Resources/` | Notes / pointers to originals |

---

## AnythingLLM setup

1. Workspace name: **CopyOS** (or keep existing and **replace** docs with this vault)
2. Upload `H:\Copy-OS\` only — **do not** re-upload the 14 mega-files alongside (duplicate noise)
3. Settings: Accuracy Optimized reranking; Max Context Snippets **6–8**
4. Paste system prompt from `AGENT-SCHEMA.md`
5. Optional pin: `05-MOCs/Query-Router.md` + `05-MOCs/Master-Index.md`

---

## How the agent should work

1. Diagnose task (headline? offer? full VSL? email sequence?)
2. Open Query Router → correct folder/section
3. Pull formulas/checklists/swipes
4. Cite **file names** (e.g. `Headlines-Leads-12-....md`)
5. For pure **business strategy / stage / money model** → send user to **Hormozi Business Strategist** workspace

---

## Rebuild

If you edit originals in `H:\Copy OS\`:

```bash
python H:\Copy-OS\_build_rag_vault.py
```

Then re-write root MOCs if needed (script rebuilds section files + per-doc indexes only).
