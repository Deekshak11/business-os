---
title: Query Router
type: moc
source: Vault navigation
stage: all
tags: [router, moc, navigation]
keywords: [if then, diagnose, which file]
last_updated: 2026-07-16
summary: Maps user intents to the correct stage, framework, and playbook files.
when_to_use: Always check first when routing a question. Pin this file if AnythingLLM allows pin.
---

# Query Router

Use this to decide **which files** to ground on before answering.

## By scaling stage symptom

| User situation | Stage file | Also open |
|----------------|------------|-----------|
| No idea what to sell / nothing to offer | `Stage-0-Improvise.md` | `Grand-Slam-Offer.md`, `Lead-Magnet.md` |
| Free users only; never charged | `Stage-1-Monetize.md` | `Value-Equation.md`, `Grand-Slam-Offer.md`, `Money-Models-Overview.md` |
| First sales but inconsistent leads | `Stage-2-Advertise.md` | `Core-Four.md`, `Rule-of-100.md`, `Lead-Magnet.md` |
| 1–4 employees; chaos; founder is bottleneck | `Stage-3-Stabilize.md` | `Playbook-Lead-Nurture.md`, qualification rules in stage file |
| 5–9 people; too many offerings / unqualified leads | `Stage-4-Prioritize.md` | niche + product specialization frameworks |
| 10–19 people; need second product / LTV | `Stage-5-Productize.md` | `Money-Models-Overview.md`, LTV/Retention playbooks |
| 20–49; inefficient; CAC up; inconsistent closes/churn | `Stage-6-Optimize.md` | `Playbook-Goated-Ads.md`, Closing, Retention |
| 50–99; one channel; chaos; reactive CS; hiring mess | `Stage-7-Categorize.md` | Second channel, `Playbook-Lead-Nurture.md`, ATS/HRIS themes |
| 100–249; product bloat; brand diluted; premium closes drop | `Stage-8-Specialize.md` | `Playbook-Branding.md`, prune product, lead routing |
| 250–500; next big bet; M&A/R&D; capital readiness | `Stage-9-Capitalize.md` | Brand-first, specialized GTM, finance prep |

## By problem type

| Problem | Primary files |
|---------|----------------|
| Offer too weak / “price shopping” | `Grand-Slam-Offer.md`, `Value-Equation.md`, `Offer-Enhancers.md` |
| Pricing / charge more | `Pricing-And-Value.md`, `Playbook-Pricing.md`, `Playbook-Price-Raise.md` |
| Not enough leads | `Core-Four.md`, `Rule-of-100.md`, `Lead-Magnet.md`, stage 2 |
| Warm list / past customers | Warm outreach sections in `Core-Four.md`, warm materials notes |
| Cold outreach | Cold outreach in `Core-Four.md` |
| Content not converting | Content path in `Core-Four.md`, `Playbook-Hooks.md` |
| Ads not working | `Playbook-Goated-Ads.md`, `Playbook-Hooks.md`, `Playbook-Proof.md` |
| Closing / sales scripts | `Playbook-Closing.md`, CLOSER framework notes |
| Cash now | `Playbook-Fast-Cash.md`, attraction offers in Money Models |
| Customers churn / low LTV | `Playbook-Retention.md`, `Playbook-Lifetime-Value.md`, continuity in Money Models |
| Brand / positioning signal | `Playbook-Branding.md` |
| Nurture / follow-up | `Playbook-Lead-Nurture.md` |
| How money sequence works | `Money-Models-Overview.md`, attraction/upsell/downsell/continuity files |
| Ad creative volume / spend wall | `Playbook-Goated-Ads.md`, Stage 6 Optimize |
| Second acquisition channel | Stage 7 Categorize + `Core-Four.md` |
| Product too complex / prune features | Stage 8 Specialize product section |
| M&A / next product bet / raise capital readiness | Stage 9 Capitalize |
| Hiring senior talent / org design at scale | Stages 6–9 people/HR sections |
| “What should I do this week?” | Stage file for their headcount + Query Router |

## Answer recipe

1. Name **stage + constraint**  
2. Pull **1–2 frameworks** + **0–1 playbook**  
3. Give steps  
4. Cite files  

## Related MOCs

- [[Scaling-Roadmap-Overview]]
- [[Core-Frameworks-Index]]
- [[Playbooks-Index]]
