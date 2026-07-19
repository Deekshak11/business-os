# Business OS — Technical architecture

For hiring managers and technical interviewers who want the **build side**, not marketing.

## Goals

1. **Production-shaped multi-agent loop** with a hard human gate  
2. **Multi-corpus RAG** (strategist methodology vs copy craft)  
3. **Observable stages** in UI (pipeline / plan / agents / outputs)  
4. **Deployable** API + web (Modal + Vercel)

## Components

### 1. Product shell (`apps/web`)

| View | Responsibility |
|------|----------------|
| Chat | Strategist conversation, streaming-style message log |
| Pipeline | Stage track: context → strategy → approval → execution → done |
| Plan | Structured plan review; Approve → Copy / Builder / Both |
| Agents | Visual status of strategist + specialists |
| Outputs | Paste-ready artifacts from specialists |

State machine (simplified):

```text
chatting → plan_ready / awaiting_approval → executing → done
```

Retry paths exist for failed specialist runs without re-planning when safe.

### 2. API (`services/api`)

- **Thread ID** for multi-turn context  
- **Plan schema** shared across strategist → UI → executors  
- **Handoff notes** when routing specialists  
- **Security wrappers** around user content for model calls  

Key modules:

| Path | Role |
|------|------|
| `app/agents/strategist.py` | Diagnosis, plan emission, approval flags |
| `app/agents/executor.py` | Route approved plan to copy / build |
| `app/rag/` | Index + retrieve |
| `app/schemas/plan.py` | Plan JSON contract |
| `app/llm/` | Provider abstraction |

### 3. RAG design

Two logical corpora (local paths; not public dumps):

| Corpus | Consumer | Intent |
|--------|----------|--------|
| Hormozi-style growth vault | Strategist | Stage, constraint, offer / lead systems |
| Copy OS vault | Copy specialist | Frameworks, structures, QA, swipe |

**Why multi-corpus:** one blended index collapses methodology and craft. Separation keeps strategist plans diagnostic and copy outputs craft-grounded.

Retrieval path (conceptual):

```text
query / plan section
  → embed
  → top-k from relevant collection
  → inject into specialist / strategist prompt
  → structured output + citations where applicable
```

### 4. Human-in-the-loop

```text
Strategist proposes plan
        │
        ▼
  User reviews (Plan view)
        │
   ┌────┴────┐
   │ Approve │  Reject / continue chat
   └────┬────┘
        │
   route: copy | build | both
        │
        ▼
   Executors only after approval
```

This is the production difference vs unbounded multi-agent toys.

### 5. Deploy topology

```text
Browser ──► Vercel (static + SSR if used) ──► Modal FastAPI
                                              │
                                              ├─ LLM provider APIs
                                              └─ Chroma / vector store
```

Health endpoint exposes readiness (`ok`, LLM configured) for UI “systems live” chrome.

### 6. Failure modes (treated as first-class)

| Failure | Response |
|---------|----------|
| LLM timeout / parse failure | Surface error; allow retry |
| Specialist garbage output | Parse/salvage paths in tests |
| Offline API | UI shows systems offline |
| Ambiguous plan | Stay in chat / re-plan |

### 7. What is intentionally not in public git

- API keys, Modal tokens  
- Full third-party book / playbook text  
- Client data  
- Private agent runtimes from other products  

Public value = **system design + runnable app shell + live demo**.

---

## Interview talking points

1. Why plan lock before specialists  
2. Why two RAG vaults instead of one mega-index  
3. How the plan schema keeps UI and executors aligned  
4. How Modal / Vercel split keeps API and UI deploy independent  
5. How tests cover parse salvage and strategist constraints  

---

## Related docs

- `00-MASTER-PLAN-AND-CONTINUITY.md`  
- `STATUS.md`  
- `DESIGN-SYSTEM.md`  
- `DEPLOY-MODAL-VERCEL.md`  
