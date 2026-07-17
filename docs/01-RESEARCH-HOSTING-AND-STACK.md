# Research: Stack & Hosting (Claim–Evidence)

**Rule:** Only verifiable primary sources (vendor docs / official product pages). No random blogs.

---

## Multi-agent orchestration

| Claim | Evidence |
|-------|----------|
| Multi-agent is for specialized context, distributed capabilities, sequential constraints — not always required | [LangChain Multi-agent](https://docs.langchain.com/oss/python/langchain/multi-agent) |
| Patterns include Subagents, Handoffs, Router, Custom LangGraph workflows | Same |
| Handoffs = state-driven transfer between specialists; term from OpenAI Agents SDK | [LangChain Handoffs](https://docs.langchain.com/oss/python/langchain/multi-agent/handoffs); [OpenAI Agents handoffs](https://openai.github.io/openai-agents-python/handoffs/) |
| Human approval = pause graph, persist state, resume with input | [LangGraph Interrupts](https://docs.langchain.com/oss/python/langgraph/interrupts) |
| Approval/reject is a documented common pattern | Same (Approve or reject section) |
| Persistence required for HITL | [LangGraph Persistence](https://docs.langchain.com/oss/python/langgraph/persistence) |

---

## RAG / metadata

| Claim | Evidence |
|-------|----------|
| Chroma supports metadata filtering via `where` on query/get | [Chroma Metadata Filtering](https://docs.trychroma.com/docs/querying-collections/metadata-filtering) |
| Logical `$and` / `$or` filters supported | Same |
| Local free embeddings model available | [Hugging Face: all-MiniLM-L6-v2](https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2) (Apache-2.0) |

---

## LLM cost (strategy/copy)

| Claim | Evidence |
|-------|----------|
| DeepSeek bills per 1M tokens with published prices (cache hit/miss/output) | [DeepSeek Models & Pricing](https://api-docs.deepseek.com/quick_start/pricing) |

---

## Realtime backend

| Claim | Evidence |
|-------|----------|
| FastAPI supports WebSockets natively | [FastAPI WebSockets](https://fastapi.tiangolo.com/advanced/websockets/) |

---

## Free / low-cost hosting

| Claim | Evidence |
|-------|----------|
| Modal Starter includes **$30/month free credits**; compute billed only when running | [Modal Pricing](https://modal.com/pricing) |
| Modal Starter: 100 containers + 10 GPU concurrency on free-credit plan | Same |
| Google Cloud Run has always-free monthly request/vCPU/memory allowances | [Google Cloud free features](https://docs.cloud.google.com/free/docs/free-cloud-features); [Cloud Run pricing](https://cloud.google.com/run/pricing) |
| Hugging Face Spaces CPU Basic is free (2 vCPU, 16 GB RAM default) | [HF Spaces Overview — Hardware](https://huggingface.co/docs/hub/spaces-overview) |
| Railway free trial = $5 one-time grant (docs) | [Railway Free Trial](https://docs.railway.com/pricing/free-trial) |
| Fly free trial is limited (2 VM hours or 7 days) | [Fly Free Trial](https://fly.io/docs/about/free-trial/) |

---

## Hosting recommendation for this project

1. **Local (this PC)** — primary development & demos  
2. **HF Spaces free CPU** or **Cloud Run free tier** — public portfolio link  
3. **Modal $30 credits** — optional serverless/GPU bursts, not required for v1  

LLM inference stays on **DeepSeek/Grok APIs** so neither local CPU nor free cloud needs a GPU for quality answers.
