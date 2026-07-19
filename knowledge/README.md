# Knowledge vaults (Business OS RAG)

This folder is the **public proof** that Business OS is not a thin chat wrapper.  
Strategist and Copy specialists retrieve from **curated, section-level corpora** with YAML frontmatter for routing.

| Vault | Path | Role in product |
|-------|------|-----------------|
| **Hormozi growth systems** | [`hormozi/`](./hormozi/) | Business Strategist RAG — stages, offers, leads, money models, playbooks |
| **Copy OS persuasion systems** | [`copyos/`](./copyos/) | Copywriting specialist RAG — frameworks, structures, checklists, swipes |

Live product: [app.deekshak.site](https://app.deekshak.site) · Portfolio: [deekshak.site/#flagship](https://deekshak.site/#flagship)

---

## Scale (hire signal)

### `hormozi/` — Strategist

| Item | Count / shape |
|------|----------------|
| Core books (distilled) | 3 ($100M Offers, Leads, Money Models lineage) |
| Implementation playbooks | 12+ |
| Layout | Core frameworks · Scaling stages 0–9 · Playbooks · Summaries · MOCs |
| Form | RAG section files + agent schema (not raw PDF dumps) |

### `copyos/` — Copy specialist

| Item | Approx |
|------|--------|
| Source mega-docs | 14 |
| RAG section files | ~400+ |
| Named frameworks | 112 |
| Structures / templates | 32 |
| Checklists & QA | 58 |
| Swipe / examples | 600+ references in system |
| Authors / sources | 40+ (classic + modern persuasion) |
| Layout | Navigation · Strategic foundation · Copy architecture · Tactical execution · Systems · MOCs |

---

## How Business OS uses these

```text
User problem
    → Strategist retrieves from knowledge/hormozi
    → Emits structured plan (citations / framework names)
    → Human plan lock
    → Copy specialist retrieves from knowledge/copyos  (if routed)
    → Builder produces implementation drafts (if routed)
    → Outputs (paste-ready)
```

**Invariant:** dual corpora on purpose. One blended index collapses “business diagnosis” and “copy craft.”

---

## What is NOT in this repo

- Desktop **raw book PDFs / full transcript dumps** (`Alex and Leila`, etc.)
- API keys, client PII, production Chroma binary dumps
- Private Modal secrets

These folders are the **distilled, RAG-optimized** vaults used to build the agent pipeline (hierarchical MD + frontmatter + MOCs + agent schemas).

---

## Local rebuild (optional)

If you maintain upstream sources:

```powershell
# Copy OS section builder (if present)
python knowledge/copyos/_build_rag_vault.py
```

Re-index into your vector store (Chroma / AnythingLLM / peers) per `services/api` RAG modules.

---

## Attribution

Methodology content originates from published authors and commercial training materials (Hormozi systems, classic copywriters, etc.).  
**Operational packaging** (folder schema, frontmatter, MOCs, agent routing, product integration) is part of the Business OS implementation for portfolio / demo use.

If you fork: replace vaults with material you have rights to use.
