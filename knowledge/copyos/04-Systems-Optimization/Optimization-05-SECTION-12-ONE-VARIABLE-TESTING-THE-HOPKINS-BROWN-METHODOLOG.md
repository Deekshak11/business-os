---
title: "SECTION 1.2 — ONE-VARIABLE TESTING (THE HOPKINS + BROWN METHODOLOGY)"
type: process
source: "13 - Optimization.md"
stage: optimize
tags: [testing, metrics, ltv-cac, benchmarks]
keywords: []
parent_doc: "13 - Optimization.md"
section_id: "Optimization-05"
last_updated: 2026-07-16
summary: "Copy-OS section from 13 - Optimization.md: SECTION 1.2 — ONE-VARIABLE TESTING (THE HOPKINS + BROWN METHODOLOGY)"
when_to_use: "Use when prioritizing tests and reading metrics."
---

## **SECTION 1.2 — ONE-VARIABLE TESTING (THE HOPKINS + BROWN METHODOLOGY)**

---

**Claude Hopkins** (Scientific Advertising, Chapter 3 — "Just Salesmanship"):

> *"Test one change at a time (not multiple).*
>
> *Change the headline + the offer + the guarantee simultaneously: A winner emerges, BUT which variable caused it?*
>
> *It's impossible to know (confounded variables).*
>
> *The result: You can't replicate the success (you don't understand the mechanism), and you can't scale the learnings (it was a unique specific combination, it's not transferable)."*

---

**Todd Brown** (E5 Method):

> *"The discipline of one variable is a science.*
>
> *The indiscipline of multiple variables is gambling.*
>
> *The market rewards science (it's replicable, scalable, and understandable).*
>
> *The market punishes gambling (it's luck not skill, it's not sustainable)."*

---

### **THE ONE-VARIABLE METHODOLOGY (A 6-Step Process):**

---

**STEP 1 — ESTABLISH A CONTROL (A Baseline Measurement):**

**What it is:** The current copy (the existing version that is running).

**The action:** Run the control (unchanged) for a minimum of 7-14 days OR until you get 100-200 conversions (whichever comes first — the threshold for statistical significance).

**Measure:** The CVR (conversion rate), the revenue, the engagement (opens/clicks for an email), and the scroll depth (for a page).

**Document:** The baseline metrics (in a spreadsheet — the date range, the traffic volume, the conversions, the CVR%, and the revenue).

---

**An example baseline:**

```
THE CONTROL — The "3 Pillars System" Sales Page

Period: Nov 1-14, 2024 (14 days)
Traffic: 2,400 visitors (organic + ads)
Conversions: 115 sales
CVR: 4.79% (115 ÷ 2,400)
Revenue: R$344,655 (115 × an average of R$2,997)
AOV: R$2,997

[The baseline is established — now you can test variations against it]
```

---

**STEP 2 — IDENTIFY A SINGLE VARIABLE TO TEST:**

**The choice is based on:** The Testing Hierarchy (from Section 1.1 — test Tier 1 first).

**Example:** Test the headline (Priority #3, after the offer/Big Idea have already been optimized).

**The variable:** ONLY the headline (the body copy, the offer, the proof, the CTA — EVERYTHING else is unchanged).

---

**Create a variation:**

**The Control Headline:**
"47 Companies Scaled 4x in 9 Months with the 3 Pillars System"

**The Variation Headline (for the Test):**
"Why Do 89% of R$30-50k Entrepreneurs NEVER Surpass R$100k? (The 3 Missing Pillars — The System That Breaks Plateaus, Validated with 4x Growth in 9 Months by 47 Companies)"

**ONLY the headline was changed** (everything else is identical — this is crucial).

---

**STEP 3 — RUN AN A/B TEST (A 50/50 Traffic Split):**

**The setup:**

- **The platform:** Google Optimize (for landing pages), Facebook (for ad variations), or an email platform (with a built-in A/B for subject lines)
- **The traffic split:** 50% sees the Control, 50% sees the Variation (a random assignment)
- **The duration:** 7-14 days OR 100-200 conversions per variation (for statistical significance)

---

**An example test:**

```
Week of Nov 15-21, 2024:

The Control (Headline A):
• Traffic: 1,200 visitors (50%)
• Conversions: 58
• CVR: 4.83%

The Variation (Headline B):
• Traffic: 1,200 visitors (50%)
• Conversions: 89
• CVR: 7.42%

The difference: +2.59 percentage points (+53.6% improvement)
```

---

**STEP 4 — ANALYZE THE STATISTICAL SIGNIFICANCE:**

**The question:** Is the difference REAL (a pattern) or LUCK (a random variance)?

---

**A Statistical Significance Calculator** (online tools — Optimizely, VWO, an AB Test Calculator):

**The inputs:**
- Visitors A: 1,200
- Conversions A: 58
- Visitors B: 1,200
- Conversions B: 89

**The output:**
- **Confidence:** 98.7% (that Variation B is better)
- **The p-value:** 0.013 (which is < the 0.05 threshold — it's statistically significant)

**The interpretation:**

**If confidence is ≥95%** (a p-value of ≤0.05): The winner is REAL ✅ (implement it).

**If confidence is <95%:** It's inconclusive (continue the test, increase the sample, OR if it's a tie = keep the control).

---

**STEP 5 — IMPLEMENT THE WINNER:**

**If Variation B wins (with 98.7% confidence):**

**The action:**
- Headline B becomes the NEW CONTROL (it replaces A everywhere).
- Scale it (roll it out to 100% of the traffic, not the 50% of the test anymore).
- The projected revenue impact: From 4.83% → 7.42% = +53.6% more conversions (a baseline of R$344k/14d becomes R$529k/14d — an additional +R$185k/14d, a R$395k/month improvement from the headline alone).

---

**STEP 6 — DOCUMENT & ITERATE:**

**Document the learning:**

```
THE TEST LOG — Headline Variation #1

Date: Nov 15-21, 2024
Element tested: The Headline
The control: "47 Companies Scaled 4x..."
The variation: "Why Do 89% of Entrepreneurs..."
The winner: The Variation (+53.6%, p=0.013) ✅
The new Control: The Variation (implemented on Nov 22, 2024)
The learning: A question headline ("Why...") + a shocking stat (89% are stuck) + a curiosity gap (the 3 missing pillars) outperformed a direct benefit statement. The avatar responds more strongly to a problem-awareness angle than to an achievement angle.
The next test: The lead type (Problem-Solution vs. a Story — to be tested in the week of Nov 22-28).
```

**Iterate:**

Variation B is the new control.

**The next week:** Create Variation C (to test a different element — the lead type now, as the headline has been optimized).

**Continuous:** Test → Implement → Test the next thing → Implement (a perpetual loop).

---

### **COMMON ONE-VARIABLE MISTAKES (5 Errors to Avoid):**

---

**ERROR #1 — Testing Multiple Variables Simultaneously:**

❌ **Bad:** Testing the headline + the lead + the offer together (changing 3 variables).

**The problem:** A winner emerged, BUT you don't know which variable caused it (the headline? the lead? the offer? a combination? — it's confounded, it's not replicable).

✅ **Correct:** Test the headline alone (in week 1), THEN the lead alone (in week 2), THEN the offer (in week 3) — they are isolated, the learnings are clear.

---

**ERROR #2 — An Insufficient Sample Size:**

❌ **Bad:** A test with 20 visitors per variation (conversions of 1 vs. 2 — a 100% difference, BUT it's noise, not a signal).

✅ **Correct:** A minimum of 100-200 conversions per variation (for statistical validity — the confidence intervals will be narrow, a signal will be detectable above the noise).

---

**ERROR #3 — A Duration That's Too Short:**

❌ **Bad:** A 24-hour test (there's daily variance — Monday's traffic is different from Saturday's, a weekday is different from a weekend, the time matters).

✅ **Correct:** A minimum of 7-14 days (to capture a weekly cycle, to average out the daily variance, for reliable data).

**The exception:** For high-volume (1,000+ conversions/day — you can test for 48-72h, as statistical significance will be reached fast).

---

**ERROR #4 — Ignoring Statistical Significance:**

❌ **Bad:** The Control has 100 conversions (5%), the Variation has 110 (5.5%) — you declare a winner (a +10% improvement).

**The problem:** A 0.5 point difference is likely noise (not a signal — a p-value of 0.23, a confidence of 77%, which is below the 95% threshold).

✅ **Correct:** Run the calculator, check for a confidence of ≥95% (p≤0.05), and ONLY implement it if it's significant.

---

**ERROR #5 — Confirmation Bias (Seeing What You Want to See):**

❌ **Bad:** You love your Variation (you spent 3h crafting it), the test shows the Control wins, but you ignore the data ("the test was flawed, my variation IS better" — it's your ego).

✅ **Correct:** The market decides (not you). If the Control wins, the Control stays (humility, being data-driven, a healthy death of the ego).

**Halbert:**

> *"The market humbles me daily (my favorites lose regularly — which is healthy, it forces improvement, the ego is irrelevant, ONLY the results matter)."*

---

```
╔═══════════════════════════════════════════════════╗
║ APPLICATION BOX — ONE-VARIABLE TESTING             ║
╠═══════════════════════════════════════════════════╣
║                                                    ║
║ ✅ THE COMPLETE PROCESS (6 Steps):                ║
║                                                    ║
║ STEP 1 — THE BASELINE (Establish a Control):      ║
║ • Run the current copy (unchanged for 7-14d OR 100-200 conversions)║
║ • Measure: The CVR, the revenue, the engagement   ║
║ • Document: The baseline metrics in a spreadsheet ║
║ Time: 7-14 days (passive — just measure)          ║
║                                                    ║
║ STEP 2 — CHOOSE A VARIABLE (A Single Element):    ║
║ • The priority: The Hierarchy's Tier 1 first (the offer, the Big Idea,║
║   the headline — the biggest levers)              ║
║ • Identify: Which element to test this week       ║
║ Time: 15 min (a decision based on the hierarchy)  ║
║                                                    ║
║ STEP 3 — CREATE A VARIATION (Change ONLY 1 Thing):║
║ • Write the variation (a different headline, an identical body)║
║ • The discipline: Resist the urge to change multiple things (it's tempting║
║   BUT fatal — only one variable)                  ║
║ Time: 30 min - 3h (depending on the element — a headline is 30 min,║
║ a lead rewrite is 2h, an offer redesign is 3h)    ║
║                                                    ║
║ STEP 4 — RUN THE TEST (A 50/50 Split):            ║
║ • The platform: Google Optimize, FB ads, email A/B║
║ • The duration: 7-14d OR 100-200 conversions each ║
║ • Monitor: Daily (to check the pacing and for technical issues)║
║ Time: 7-14 days (with 10 min/day of passive monitoring)║
║                                                    ║
║ STEP 5 — ANALYZE (A Check for Statistical Significance):║
║ • The calculator: An online AB Test Calculator (it's free)║
║ • The inputs: Visitors A/B, Conversions A/B       ║
║ • The output: A Confidence %, a p-value           ║
║ • The threshold: 95%+ confidence (p≤0.05) = significant║
║ • The decision: If it's significant = implement the winner, if Not = continue║
║   the test, OR if it's a tie = keep the control   ║
║ Time: 30 min (for analysis, the calculator, and the decision)║
║                                                    ║
║ STEP 6 — IMPLEMENT + DOCUMENT (The Winner Becomes the Control):║
║ • Replace: The control with the winner (for 100% of the traffic)║
║ • Log: The test results in a spreadsheet (the winner, the % improvement,║
║   the learnings, the date it was implemented)     ║
║ • The next step: Choose the next variable (in the Tier 1-2-3-4 order),║
║   and repeat the process (a continuous loop)      ║
║ Time: 30 min (to implement, document, and plan the next)║
║                                                    ║
║ THE TOTAL CYCLE: 8-15 days per test (for 1 variable)║
║ THE FREQUENCY: Weekly-biweekly (26-52 tests/year) ║
║ THE COMPOUNDING: Small wins accumulate (in year 1 = a +30-100%║
║ cumulative improvement from dozens of tests)      ║
║                                                    ║
║ Hopkins: "Testing isn't an expense (it's an investment that prevents║
║ a massive waste from scaling the wrong version — a 10-100:1 ROI,║
║ always test, assume nothing, the market will teach you)."║
╚═══════════════════════════════════════════════════╝
```

---

---

## Related

- Parent: `13 - Optimization.md`
- Folder: `04-Systems-Optimization/`
- MOC: `05-MOCs/Query-Router.md`
