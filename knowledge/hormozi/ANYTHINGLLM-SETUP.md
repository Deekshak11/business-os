# AnythingLLM Setup — Hormozi Business Strategist

## 1. Create workspace

Name: **Hormozi Business Strategist**

## 2. Upload documents

Upload the folder:

`H:\Hormozi-Business-Strategist\`

Include all subfolders. **Do not** also upload `C:\Users\user\Desktop\Alex and Leila` into this workspace (raw dumps will poison retrieval).

## 3. System prompt

Open `AGENT-SCHEMA.md` → copy body into Workspace **System Prompt**.

## 4. Recommended vector settings

| Setting | Start with |
|---------|------------|
| Search preference (LanceDB) | **Accuracy Optimized** (reranking) |
| Max context snippets | **6–8** |
| Document similarity threshold | Default; if misses relevant docs → lower / No Restriction |

## 5. Optional pinning

Pin only tiny navigation hubs if answers feel unfocused:

- `04-MOCs/Query-Router.md`
- `04-MOCs/Scaling-Roadmap-Overview.md`

Do **not** pin large playbooks or multi-framework dumps.

## 6. Test queries

1. “I’m solo, sold a few clients, leads are inconsistent — what should I do?”  
   → Expect Stage 2 + Rule of 100 + Core Four + cite files  

2. “How do I make my offer not price-shopped?”  
   → Grand Slam + Value Equation + Offer Enhancers  

3. “Customers churn every month”  
   → Retention playbook + LTV + Stage 3 CS  

4. “Write me a full VSL long-form”  
   → Strategist gives offer/hooks/proof; directs deep copy craft to **CopyOS** workspace  

## 7. Keep separate from CopyOS

| Workspace | Role |
|-----------|------|
| Hormozi Business Strategist | Strategy, offers, leads, stages, money models, playbooks |
| CopyOS | Deep copywriting craft |
