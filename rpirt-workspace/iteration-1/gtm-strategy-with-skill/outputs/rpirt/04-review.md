# 04 — Review

Phase 4 of RPIRT. Independent review of `gtm-plan.md` against plan and research artifacts.

---

## Round 1

### Rubric

| Criterion | Score | Threshold | Status | Justification |
|-----------|-------|-----------|--------|---------------|
| **ICP Specificity** — Does the plan define a precise, actionable target profile that avoids generic "law firms"? | 9/10 | 7 | PASS | ICP is named with practice areas ranked by intake pain intensity, firm size, technology stack, geographic guidance, and trigger events. Actionable. |
| **Budget Realism** — Is the $15k allocation justified with line items tied to specific outcomes, and are assumptions stress-tested? | 8/10 | 8 | PASS | Line-item budget with notes on timing and conditionality. Reserve clearly called out. Paid ads gated behind a conversion milestone. $7.4k reserve is somewhat undifferentiated — could be more specific. |
| **Timeline Realism** — Does the month-by-month plan account for sales cycle lag, sequencing dependencies, and the realities of founder bandwidth? | 7/10 | 8 | FAIL | Month targets (3–4 new customers/month from month 2 onward) assume a near-instant outbound ramp. In practice: list building takes 2–3 weeks, outreach warming takes 1–2 weeks, sales cycle 2–4 weeks. Month 2 closing 3–4 customers requires pipeline built in week 1. This is optimistic without a buffer or catch-up mechanism spelled out. |
| **Pilot Conversion Rigor** — Is the pilot-to-paid mechanism specific enough to actually work, with pricing, urgency, and fallback? | 9/10 | 8 | PASS | Pilot conversion email template is provided verbatim. Charter pricing with hard deadline. Fallback clause for non-converting pilots. Excellent. |
| **Message and Channel Fit** — Do the outreach sequences speak to the actual buyer psychology of small law firm managing partners? | 8/10 | 7 | PASS | Loss frame, ROI math, and trust frame are all present. Email and LinkedIn sequences are provided verbatim. Legal professional culture respected. Minor gap: no explicit subject line A/B testing guidance beyond 3 options. |
| **Competitive Differentiation** — Does the plan position against actual competitors in a way that is defensible and specific? | 8/10 | 7 | PASS | Competitor table included with head-to-head comparison. Win zone clearly defined. Lawmatics AI Suite competitive threat acknowledged. Could add one talking point specifically for when a prospect says "I'm looking at Lawmatics." |
| **Measurement and Accountability** — Are success metrics specific, measurable, and tied to weekly behaviors that a founder can track? | 9/10 | 8 | PASS | Weekly dashboard with 6 tracked metrics. Alert threshold at <2 calls booked per week. Monthly OKRs per month. Strong accountability structure. |
| **Contingency Planning** — Are failure modes and pivot triggers defined, not just mentioned? | 8/10 | 7 | PASS | Three contingency scenarios documented: 0/3 pilot conversion, off-track by month 3, budget depletion. Pipeline audit methodology included. |
| **Actionability** — Can a founder start executing from this document on Monday morning without needing to make additional decisions? | 8/10 | 8 | PASS | Week 1 immediate actions included. Asset checklist is a concrete gate. Templates provided verbatim. One gap: does not specify which tool to use for the target list build or in what order to prioritize the 200 targets. |
| **Market Sizing and Revenue Math** — Does the plan validate that 20 customers is achievable given the market, the channel, and the budget? | 7/10 | 7 | PASS | Math present: $750 CAC ceiling, MRR at target. Competitive density estimate missing — how many firms in the ICP geography actually exist? Without this, it's unclear if 200 targets is a significant fraction or a rounding error. Borderline pass. |

---

### Adversarial Persona: The Budget-Approving CFO

*"I'm approving $15k of spend here. Give me your answers:"*

**Attack 1 — "Your month 2 targets assume 3–4 customers but you don't start building the list
until month 1 week 2. That's a 3-week runway to close 3 deals. Typical B2B sales cycle is
4–6 weeks minimum even for small firms. Show me how month 2 closes 3 customers when the
pipeline barely exists."**

This is the sharpest challenge. The timeline on months 1–2 is optimistic. A prospect reached
in week 3 of month 1 who goes through a 3-step email sequence, a discovery call, a demo, and
a close conversation is unlikely to pay before mid-month 2 at the earliest — meaning month 2
is more likely 1–2 customers than 3–4.

**Attack 2 — "Your $7.4k reserve is 49% of the budget. You've told me what you're NOT spending
it on. You haven't told me what you ARE spending it on. That's not a budget, that's a wishlist."**

The reserve is somewhat vague. The plan says "as needed" and "do not spend speculatively" but
doesn't anticipate what high-ROI opportunities might emerge that would warrant deploying reserve.

**Attack 3 — "You assume the founder has time for 50–60 outreach contacts per week PLUS
webinar preparation PLUS demo calls PLUS customer success calls. That's a full-time outbound
sales job plus a full-time customer success job plus a product roadmap. Where does the bandwidth
come from?"**

Founder bandwidth is not explicitly addressed. The plan stacks activities without
acknowledging that in months 2–3, a founder is simultaneously: doing outreach (50–60/week),
running discovery calls (2/week), doing demos (1/week), doing customer success calls (1–2/week
for existing customers), preparing bar webinar content, writing blog posts, and running the
product. That's 3 full-time jobs.

---

### Diagnosis (Failures Only)

**Timeline Realism (FAIL — 7/10 vs. threshold 8/10)**

- **What's wrong:** The month-by-month table shows 3–4 new customers in month 2, but the
  pipeline to support this cannot be fully built until mid-month 1. A prospect first contacted
  in week 3 of month 1 would likely close in week 2–3 of month 2, not week 1. This creates a
  structural gap in the early months that compounds if there are any misses.
- **Root cause:** The plan was built from the "what needs to happen" direction (20 customers ÷
  6 months ÷ 3–4/month) without reverse-engineering from sales cycle reality.
- **Fix:** Add a "pipeline lag acknowledgment" section. Revise the month 2 target to 1–2
  customers (with months 5–6 absorbing the slack), or add a "fast-track pilot network" tactic
  that can compress the sales cycle for the first 5 customers using warm intros rather than
  cold outreach.

**Adversarial CFO Finding #2 — Budget Reserve Specificity**

- **What's wrong:** $7,400 (49% of budget) is labeled "miscellaneous + reserve" with "do not
  spend speculatively" as guidance. This is prudent but not actionable — a founder under pressure
  to hit month 4 targets may either hoard it unnecessarily or blow it without a framework.
- **Root cause:** The reserve was scoped defensively without contingency deployment logic.
- **Fix:** Break the $7,400 reserve into labeled buckets with deployment triggers:
  e.g., "$2,000 for bar conference sponsorship IF webinar ROI > 2 customers per webinar;
  $2,000 for freelance sales support IF founder bandwidth is a bottleneck by month 3; $3,400
  true emergency reserve."

**Adversarial CFO Finding #3 — Founder Bandwidth**

- **What's wrong:** The plan stacks 5–6 concurrent workstreams in months 2–3 without
  acknowledging that a solo founder or 2-person team has finite hours.
- **Root cause:** Plans are written as if there's an infinite executor. This one treats the
  GTM plan and the product as separate concerns.
- **Fix:** Add a "Weekly Time Budget" section that shows the realistic time allocation
  (hours per activity per week) and identifies what to cut if bandwidth is constrained.
  State explicitly: "If you have fewer than 15 hours/week for GTM, deprioritize blog writing
  and webinar prep — outbound outreach is non-negotiable."

---

## Round 1 Score Summary

| Criterion | R1 Score | Threshold | Status |
|-----------|----------|-----------|--------|
| ICP Specificity | 9/10 | 7 | PASS |
| Budget Realism | 8/10 | 8 | PASS |
| Timeline Realism | 7/10 | 8 | FAIL |
| Pilot Conversion Rigor | 9/10 | 8 | PASS |
| Message and Channel Fit | 8/10 | 7 | PASS |
| Competitive Differentiation | 8/10 | 7 | PASS |
| Measurement and Accountability | 9/10 | 8 | PASS |
| Contingency Planning | 8/10 | 7 | PASS |
| Actionability | 8/10 | 8 | PASS |
| Market Sizing and Revenue Math | 7/10 | 7 | PASS |

**Failing criteria:** 1 (Timeline Realism)  
**CFO attacks requiring fixes:** 3 (timeline, reserve, bandwidth)

---

## Round 2 — Post-Fix Review

*After implementation agent addressed diagnoses: added pipeline lag note, budget reserve breakdown,
and weekly time budget section to the GTM plan.*

### Rubric Re-Score (changed criteria only)

| Criterion | R1 Score | R2 Score | Threshold | Status | Change |
|-----------|----------|----------|-----------|--------|--------|
| Timeline Realism | 7/10 | 8.5/10 | 8 | PASS | Added pipeline lag section; month 2 expectations recalibrated; fast-track warm intro tactic added |
| Budget Realism | 8/10 | 9/10 | 8 | PASS | Reserve broken into labeled buckets with deployment triggers |
| Actionability | 8/10 | 9/10 | 8 | PASS | Weekly time budget added with explicit prioritization guidance |

### Delta from Round 1

- Timeline Realism resolved: plan now explicitly acknowledges 2–4 week sales cycle lag
  and adjusts month 2 expectations downward while extending runway into months 5–6.
- Budget reserve now actionable: deployment triggers added for each bucket.
- Founder bandwidth addressed: weekly time budget added; content work explicitly marked
  lower priority than outreach.

**All criteria pass after Round 2. Proceed to Phase 5.**

---

## Final Scores (Round 2)

| Criterion | Final Score | Threshold | Status |
|-----------|-------------|-----------|--------|
| ICP Specificity | 9/10 | 7 | PASS |
| Budget Realism | 9/10 | 8 | PASS |
| Timeline Realism | 8.5/10 | 8 | PASS |
| Pilot Conversion Rigor | 9/10 | 8 | PASS |
| Message and Channel Fit | 8/10 | 7 | PASS |
| Competitive Differentiation | 8/10 | 7 | PASS |
| Measurement and Accountability | 9/10 | 8 | PASS |
| Contingency Planning | 8/10 | 7 | PASS |
| Actionability | 9/10 | 8 | PASS |
| Market Sizing and Revenue Math | 7/10 | 7 | PASS |

**Average score: 8.45/10. All criteria pass.**
