---
title: "SECTION 6.2 — TRIGGERS & TAGS (Behavior-Based Automation)"
type: process
source: "11 - Funnels and Email Sequences.md"
stage: funnels
tags: [funnels, email, sequences, value-ladder]
keywords: []
parent_doc: "11 - Funnels and Email Sequences.md"
section_id: "Funnels-Email-29"
last_updated: 2026-07-16
summary: "Copy-OS section from 11 - Funnels and Email Sequences.md: SECTION 6.2 — TRIGGERS & TAGS (Behavior-Based Automation)"
when_to_use: "Use when mapping funnels or value ladder."
---

## **SECTION 6.2 — TRIGGERS & TAGS (Behavior-Based Automation)**

---

**Automation = sequences triggered by behaviors** (not a manual send — it's automatic based on subscriber actions).

---

### **COMMON TRIGGERS (10 Types):**

---

**TRIGGER #1 — OPT-IN (Subscribe Form):**

**Behavior:** A subscriber submits their email (on a lead magnet, a landing page).

**Automated action:** Send indoctrination email #1 instantly (welcome, deliver the lead magnet).

**Setup:** In the platform (ActiveCampaign): Form submission → triggers the "Indoctrination Sequence" to start → email #1 sends automatically in 0-5 min.

---

**TRIGGER #2 — LINK CLICK (Email Engagement):**

**Behavior:** A subscriber clicks a specific link in an email (a signal of interest — they clicked on the VSL, the offer, the case study).

**Action:** Add a tag (interest level, for segmentation), trigger a sequence (a specific follow-up for that interest).

**Example:** They clicked the VSL link in an email → Tag "VSL Interest" → Triggers the "VSL Follow-Up Sequence" (+24h, a 3-email nurture for VSL viewers).

---

**TRIGGER #3 — PURCHASE (Transaction Complete):**

**Behavior:** A customer completes checkout (payment is processed).

**Action:** Add a "Customer" tag, unsubscribe them from prospect sequences (indoctrination, nurture), subscribe them to customer sequences (onboarding, upsell, retention).

**Segmentation:** Prospects vs. Customers (different emails for each — prospects are for selling, customers are for delivering/upselling/retaining).

---

**TRIGGER #4 — ABANDONED CART (Started Checkout, Didn't Complete):**

**Behavior:** Added a product to the cart, began checkout, and exited (didn't complete payment — 70% of carts are abandoned on average).

**Action:** Tag "Abandoned Cart," trigger a recovery sequence (3 emails: +1h, +24h, +48h — with urgency, an optional 5-10% discount in the final email, recovers 15-30%).

**Ladeira:** "Abandoned carts in Brazil are at 72% (higher than the US at 68% — mobile checkout friction, complexity of payment methods, a cultural hesitation for comparison shopping). A recovery sequence is critical (it recovers 20-28% of carts = R$20-80k/month in revenue depending on volume)."

---

**TRIGGER #5 — EMAIL OPEN (Engagement Signal):**

**Behavior:** Opens an email (moderate interest — they opened it, they didn't ignore it).

**Action:** Tag "Engaged" (for segmentation), score +1 (an engagement score accumulates).

**Segmentation:** Engaged (opens 3+ of the last 10 emails) vs. Cold (opens 0 of the last 30 emails) — different sequences for each.

---

**TRIGGER #6 — NO OPEN FOR 30 DAYS (Inactivity):**

**Behavior:** Zero opens for 30 consecutive days (a signal of disengagement).

**Action:** Tag "Inactive," trigger a re-engagement sequence (a 4-email win-back, an incentive to return, a survey on why they're inactive, a final offer OR a clean removal from the list).

---

**TRIGGER #7 — UNSUBSCRIBE (Exit Signal):**

**Behavior:** Clicks the unsubscribe link (they are leaving).

**Action:** An unsubscribe page (with an optional survey on why they're leaving — to collect feedback, an incentive to stay with an offer to "reduce the frequency?", but respecting the decision to exit if confirmed).

---

**TRIGGER #8 — DATE-BASED (Anniversary, Birthday, Milestone):**

**Behavior:** A date is reached (a customer's 1-year anniversary, a subscriber's birthday).

**Action:** A special email (gratitude for being a customer for 1 year, a birthday discount, a milestone celebration — relationship personalization).

---

**TRIGGER #9 — SURVEY RESPONSE (Segmentation Data):**

**Behavior:** Completes a survey (interests, goals, budget, situation — data is collected).

**Action:** Tags are based on the answers (an interest "high-ticket" tag if their budget is R$5k+, a "scale" goal tag if they answered scaling), personalized segmentation sequences.

---

**TRIGGER #10 — WEBINAR ATTENDANCE (Event Participation):**

**Behavior:** Attended a webinar live (extreme engagement — they invested 90 min).

**Action:** Tag "Webinar Attendee," a post-webinar sequence (no replay offer, did they purchase the offer?, a personalized follow-up for their attendance).

---

### **TAGS STRATEGY (Ladeira's VTSD Practice):**

**Tags = labels for subscribers** (to categorize, segment, and personalize).

---

**Tag categories:**

**A. Source tags:** Where they came from (Facebook Ad, Google SEO, Referral, Webinar — for attribution).

**B. Interest tags:** What they were interested in (clicked VSL, applied for High-Ticket, downloaded Templates — behavioral signals).

**C. Engagement tags:** Their activity level (Engaged opens 50%+, Moderate 20-49%, Cold <20% — for segmentation).

**D. Customer tags:** Their purchase status (Prospect, Tripwire Customer, Core Customer, High-Ticket Customer — for the lifecycle).

**E. Goal tags:** Their objectives (Scale Business, Get Clients, Learn Skill — for personalization).

---

**Example tagging workflow:**

```
Subscriber João:

Day 1 opt-in (from a "Facebook Ad Lead Magnet" form):
→ Tag: "Source: Facebook"
→ Tag: "Lead Magnet: Copywriting Guide"
→ Trigger: Indoctrination Sequence

Day 3 clicks the VSL link (in email #3):
→ Tag: "Interest: VSL"
→ Tag: "Engagement: High" (opens 3/3 emails)
→ Trigger: VSL Follow-Up Sequence

Day 5 purchases the R$47 Tripwire:
→ Tag: "Customer: Tripwire"
→ Tag: "Product: Templates Pack"
→ Remove: Prospect sequences
→ Trigger: Customer Onboarding

Day 45 purchases the R$1,997 Core offer:
→ Tag: "Customer: Core"
→ Tag: "Value Ladder: Tier 3"
→ Trigger: High-Ticket Upsell Sequence

Day 180 responds to a survey with "Goal: Scale to R$100k":
→ Tag: "Goal: Scaling"
→ Segmentation: He receives scaling-focused emails (not the client acquisition-focused ones others receive)

João's total tags: 9 (source, lead magnet, 2 interests, engagement, 2 customer, 2 products, a goal — comprehensive profiling, emails personalized to his behavior/interests)
```

---

**The power of segmentation:**

**A generic email blast:** "Learn copywriting" (sent to everyone — irrelevant to 60%, 18% opens).

**A segmented email:** "Scale your copywriting business to R$100k" (sent ONLY to those with the "Goal: Scaling" tag — relevant to 90%, 42% opens).

**The difference:** 2.3x more opens (segmentation vs. a blast — personalization matters).

---

```
╔═══════════════════════════════════════════════════╗
║ APPLICATION BOX — AUTOMATION SETUP WORKFLOW        ║
╠═══════════════════════════════════════════════════╣
║                                                    ║
║ ✅ COMPLETE AUTOMATION SETUP (Platform: ActiveCampaign║
║ as an example, others are similar):               ║
║                                                    ║
║ STEP 1 — CREATE THE SEQUENCES (Content First):    ║
║ • Write the emails (7 indoctrination, 10 nurture, 5 soap║
║   opera, 20 launch, 4 re-engagement — 46+ emails total)║
║ • Upload to the platform (each email is separate, with a subject/body)║
║ • Time: 8-15h (writing 46 emails @ 15-20min each) ║
║                                                    ║
║ STEP 2 — SETUP THE TRIGGERS (Behavior → Action):  ║
║ • Opt-in form → Indoctrination starts             ║
║ • VSL link click → Tag "VSL Interest" + Follow-up║
║ • Purchase → Tag "Customer" + Onboarding          ║
║ • Cart abandon → Recovery sequence               ║
║ • 30d no open → Re-engagement                     ║
║ • [Setup each trigger — 10 total, 30-60min each]  ║
║                                                    ║
║ STEP 3 — STRUCTURE THE TAGS (Categorize Subscribers):║
║ • Source tags (5-10 — Facebook, Google, Referral, etc)║
║ • Interest tags (8-12 — VSL, Templates, High-Ticket, etc)║
║ • Engagement tags (3 — High/Moderate/Cold)        ║
║ • Customer tags (5 — Prospect, Tripwire, Core, High, VIP)║
║ • Goal tags (5-8 — Scale, Clients, Learn, etc)    ║
║ Total: 26-38 tags (for comprehensive profiling)   ║
║                                                    ║
║ STEP 4 — SEGMENTATION RULES (Personalize Sends):  ║
║ • Create segments (Tag combinations — "Goal: Scaling"║
║   + "Customer: Core" + "Engagement: High" = a specific segment║
║   for ultra-targeted emails)                      ║
║ • Test the segments (is the size adequate? 50+ subscribers is a viable║
║   minimum, <50 = merge into a broader one)        ║
║                                                    ║
║ STEP 5 — INTEGRATION (Connect the Ecosystem):     ║
║ • Email ↔ Funnel (ClickFunnels, Kajabi — sync contacts)║
║ • Email ↔ CRM (if there's a sales team — Pipedrive, HubSpot)║
║ • Email ↔ Payment (Stripe, PayPal — for purchase triggers)║
║ • Email ↔ Webinar (Zoom, Demio — for registration/attendance)║
║                                                    ║
║ STEP 6 — TEST THE WORKFLOW (Before Going Live):   ║
║ • A test subscriber (yourself — opt-in, trigger sequences,║
║   receive the emails, check that the timing/content/links work)║
║ • Fix bugs (broken links, missing emails, wrong timing)║
║ • Live launch (with real traffic, monitor the dashboard)║
║                                                    ║
║ TOTAL SETUP TIME: 15-25h (writing the sequences 8-15h + ║
║ automation config 4-6h + testing/fixes 3-4h)      ║
║                                                    ║
║ ONE-TIME: An upfront investment (15-25h), then it runs║
║ perpetually on autopilot (infinite ROI — the sequences work║
║ 24/7 without you, scaling to unlimited subscribers).║
╚═══════════════════════════════════════════════════╝
```

---

---

## Related

- Parent: `11 - Funnels and Email Sequences.md`
- Folder: `03-Tactical-Execution/`
- MOC: `05-MOCs/Query-Router.md`
