---
name: rpirt
description: >
  Execute any complex task at a production level using the Research, Plan, Implement, Review, Test
  methodology. Automatically scales from lightweight to full 5-phase orchestration based on task
  complexity. Each phase runs in a dedicated context (or sub-agent) and produces a markdown artifact,
  so no context bleeds between stages. The Review phase uses a dynamically generated scoring rubric
  (recursive-refine protocol) to enforce measurable quality gates — not vibes. Use this skill
  proactively whenever the user asks to "do this properly", "production level", "build this the
  right way", says "RPIRT", "5 step methodology", or when the request is clearly multi-phase and
  no workflow has been specified. Also use for complex coding tasks, business strategies, research
  projects, system designs, or any deliverable where getting it wrong would be costly.
---

# RPIRT — Research, Plan, Implement, Review, Test

A 5-phase production methodology for delivering complex work correctly the first time. Adapted from
@agentic.james' framework and enhanced with rubric-based quality enforcement in the Review phase.

The core insight: when one agent researches, plans, implements, and reviews in a single conversation,
it anchors on early decisions and misses contradictions. Separate phases with clean artifact
handoffs force re-evaluation at each stage and catch drift before it compounds.

---

## Step 0: Complexity Gate

Before starting, classify the task. Be honest — complexity inflation wastes the user's time as much
as under-engineering does.

| Level | Signals | Response |
|-------|---------|----------|
| **Simple** | Single deliverable, no ambiguity, no research needed, ≤2 files | Skip RPIRT. Just do it. |
| **Medium** | Clear goal, some research needed, 2–5 files, known constraints | Compress: combine Research + Plan in one pass, run a lightweight review without full rubric. Create only `rpirt/plan.md` and `rpirt/review.md`. |
| **Complex** | Ambiguous requirements, multiple systems, significant unknowns, 5+ files, or user explicitly invokes the methodology | Full 5-phase RPIRT below. |

If you're unsure, lean toward **Complex** — it's cheaper to run extra phases than to redo wrong work.

**Before classifying**, tell the user the level you assessed and why, in one sentence. If they push
back or say "just go", honor it and skip checkpoints from that point forward.

---

## Phase 1 — Research

**Why this phase exists:** Assumptions are the most expensive thing in complex work. A dedicated
research phase lets you gather broadly — across the web, the codebase, documentation, prior
decisions — without anchoring prematurely on a solution. Everything discovered here becomes the
foundation the plan is built on.

### What to do

- Capture the user's full intent. If anything is ambiguous, ask now — not during implementation.
- Search external sources: web, documentation, APIs, existing codebase patterns.
  - Coding tasks: scan the repo for relevant architecture, existing utilities, dependencies, and constraints.
  - Business/strategy tasks: research best practices, market context, competitive examples.
  - General tasks: find analogous examples, relevant frameworks, known failure modes.
- Identify unknowns and risks explicitly — things you couldn't find answers to are as important as what you did find.

### Artifact: `rpirt/01-research.md`

```
## Goal
[One paragraph: what the user actually wants and why]

## Findings
[Organized by source — codebase, web, docs, etc. Keep it dense, not narrative.]

## Unknowns and Risks
[Things that couldn't be resolved yet. Flag anything that could block implementation.]

## Key Constraints
[Time, tech stack, budget, non-negotiables, existing decisions that can't change]
```

### Human checkpoint

Summarize your findings in 3–5 bullets and ask: "Does this capture everything? Anything I missed or
should dig deeper on?"

If the user says "just go", skip this and all future checkpoints.

### Failure path

If research reveals the task is infeasible, fundamentally different from what was described, or
depends on an unknown that can't be resolved, surface this before writing a plan. Don't paper over
blockers.

---

## Phase 2 — Plan

**Why this phase exists:** Planning from a clean read of the research document forces synthesis
rather than momentum. The plan becomes the single source of truth for implementation. If the plan
is wrong, fix it here — not while you're 3 files deep in implementation.

### What to do

Read `rpirt/01-research.md` as your primary input. If using sub-agents, this file should be the
**only** context the planning agent receives — clean context is the point.

Produce a concrete, ordered execution plan:
- **Coding:** Architecture decisions, file-by-file changes, dependencies to install, validation criteria.
- **Business:** Phases, deliverables, success metrics, owner/stakeholder for each action.
- **General:** Ordered action items with concrete next steps and clear completion criteria.

Always include:
- **Durable Decisions:** Choices that are hard to reverse (tech stack, architecture patterns, strategic direction). Capture these explicitly — they anchor every downstream decision.
- **Definition of Done:** For each task, what does "complete" actually mean? Make it checkable.
- **Risk Mitigations:** For each risk from the research phase, what's the mitigation or contingency?

### Artifact: `rpirt/02-plan.md`

```
## Durable Decisions
[Hard-to-reverse choices, stated as facts: "Using X because Y"]

## Task Breakdown
1. [Task] — depends on: [none / task N]
   Done when: [checkable criterion]
2. ...

## Risk Mitigations
[Risk from research → mitigation strategy]
```

### Human checkpoint

Present the plan and explicitly ask for approval before any implementation begins. This is the most
consequential checkpoint — a bad plan executed well is still wrong.

If the plan reveals scope is significantly larger than the user expected, flag it and offer to
proceed, reduce scope, or re-research a narrower version.

### Failure path

If you cannot produce a plan from the research (because critical unknowns remain), go back to
Phase 1 with specific questions to answer.

---

## Phase 3 — Implement

**Why this phase exists:** Implementation should be mechanical — following the plan, not inventing
it. Separating execution from design keeps the implementation agent focused on quality, not
architecture. Design decisions made during implementation are a sign the plan was incomplete;
log them as deviations rather than silently accepting them.

### What to do

Execute the plan task-by-task, in order, following `rpirt/02-plan.md`.

With sub-agents available: split the plan into independent work streams and parallelize. Each agent
receives the plan doc plus its specific section. Parallel work streams should be genuinely
independent — shared state causes merge conflicts, both in code and in plans.

Log deviations when they happen. The plan will rarely be perfect; the goal is to capture where
reality diverged from design so the review agent can evaluate the delta, not be surprised by it.

### Artifact: `rpirt/03-progress.md` — updated as you go

```
## Status
[ ] Task 1 — [status: done / in-progress / blocked / deviated]
[ ] Task 2 — ...

## Deviations
- Task N: [what changed and why]
```

### Failure path

If a blocker appears that the plan didn't anticipate, stop and ask: continue with a workaround,
revise the plan, or re-research? Don't silently work around blockers — they usually indicate an
assumption in the plan that will surface again.

---

## Phase 4 — Review (recursive-refine protocol)

**Why this phase exists:** "Check for issues" is not a quality gate — it's wishful thinking. This
phase uses a dynamically generated rubric to score the implementation against concrete, domain-
specific criteria. The review agent should have no shared context with the implementation agent;
independence is what makes the review meaningful.

The implement/review loop runs up to 3 times. Each pass only rewrites what failed, preserving
passing work.

### Stage A: Generate the rubric

Analyze the deliverable to determine:
1. **Primary domain** (Software Engineering, Marketing, Finance, Operations, Research, etc.)
2. **Specific sub-type** (CLI tool, GTM strategy, data pipeline, API design, etc.)
3. **Intended audience and their goal** (who will use or evaluate this, and what do they care about?)

Generate 6–10 scoring criteria for this specific deliverable. Each criterion needs:
- **Name:** A short label (e.g., "Error Handling", "Market Sizing Rigor", "Timeline Realism")
- **What it measures:** One sentence
- **What 9/10 looks like:** A concrete benchmark, not platitudes
- **Threshold:** 7–9, based on how critical the criterion is for this domain

Derive the **adversarial persona** — the harshest relevant expert who would review this work:

| Sub-type | Adversarial Persona |
|----------|---------------------|
| Python CLI tool | Power user who runs it on malformed inputs at 2am |
| REST API | Engineer who has to integrate and maintain this in production |
| GTM strategy | CFO who has to approve the budget and will stress-test every assumption |
| Data pipeline | ML engineer checking for data leakage and reproducibility failures |
| Content/copy | Skeptical first-time reader with 5 seconds of attention |
| Architecture design | Senior engineer who will own this system for 3 years |

If confidence in classification is below 70%, use a General Content rubric:
Clarity, Completeness, Accuracy, Actionability, Appropriate Scope, Correctness.

### Stage B: Score

For each criterion, read the deliverable alongside `rpirt/02-plan.md` and `rpirt/01-research.md`.
Assign a score with a one-line justification. Mark PASS or FAIL against threshold.

### Stage C: Diagnose failures

For each failing criterion:
1. **What's wrong:** Specific examples from the deliverable.
2. **Root cause:** Why it fails — not just what's wrong, but why.
3. **How to fix:** Concrete, actionable instructions that the implementation agent can execute.

Then apply the adversarial persona: attack the deliverable from their perspective. What would they
tear apart? Merge any new findings into the diagnosis.

### Stage D: Loop

Send the diagnosis back to Phase 3. The implementation agent addresses only the failing criteria —
passing work is preserved.

**Termination conditions:**
- All criteria pass their threshold, OR
- 3 implementation/review rounds have completed, OR
- Scores plateau (no improvement across 2 consecutive rounds)

On termination, finalize and proceed to Phase 5.

### Artifact: `rpirt/04-review.md` — one section per round

```
## Round N

### Rubric
| Criterion | Score | Threshold | Status | Justification |
|-----------|-------|-----------|--------|---------------|
| ...       | X/10  | Y/10      | PASS/FAIL | ... |

### Adversarial Persona: [derived persona]

### Diagnosis (failures only)
**[Criterion name]**
- What's wrong: ...
- Root cause: ...
- Fix: ...

### Delta from Round N-1
[Score changes, what improved, what remains]
```

---

## Phase 5 — Test

**Why this phase exists:** Review checks quality in isolation. Testing validates the deliverable
works in the real environment where it will actually be used. These are different questions.
A perfectly written CLI tool that crashes on the user's OS has passed review and failed testing.

### What to do

Test in the production environment — not a simulation of it.

- **Coding:** Run the system end-to-end. Test the actual user-facing surfaces (CLI commands, API
  endpoints, UI flows) with real inputs, including edge cases and adversarial inputs. Don't stop
  at unit tests — they tell you the parts work, not that the system works.
- **Business/Strategy:** Validate against real constraints. Does the math add up? Does the timeline
  account for dependencies? Would the target audience actually respond to this?
- **General:** Walk through the deliverable as the end user would experience it, step by step.
  Where does it break, confuse, or fall short?

### Artifact: `rpirt/05-test-results.md`

```
## What Was Tested
[Surfaces, scenarios, inputs]

## Results
| Test | Result | Evidence |
|------|--------|----------|
| ... | PASS/FAIL | ... |

## Remaining Risks
[Known limitations, untested scenarios, things that need monitoring in production]
```

### Final delivery

Deliver the completed work plus a summary scorecard:
- Review rubric: initial scores vs. final scores, iterations taken
- Test results: pass/fail summary
- Remaining risks

---

## Sub-Agent Strategy

The value of RPIRT is clean context between phases. Sub-agents make this automatic; without them,
you simulate it using artifacts as context boundaries.

### With sub-agents (Task tool available)

- **Research:** Spawn parallel agents for different vectors (web search, codebase exploration,
  documentation). Each gets only the user's original request. Merge their outputs into
  `rpirt/01-research.md`.
- **Plan:** Single agent receives only `rpirt/01-research.md`. No other context.
- **Implement:** Spawn parallel agents for independent work streams. Each receives `rpirt/02-plan.md`
  and its specific task section. Parallel streams must be genuinely independent.
- **Review:** Independent agent receives `rpirt/01-research.md`, `rpirt/02-plan.md`, the
  deliverable, and `rpirt/03-progress.md` (including deviations). No shared context with the
  implementer — independence is what makes the review credible.
- **Test:** Single agent runs integration tests in the target environment.

### Without sub-agents (sequential)

Run each phase in order. At the start of each phase, explicitly acknowledge: "Beginning Phase N.
My context for this phase is: [list the artifacts]." This simulates the clean handoff.

The markdown artifacts serve as the context separation mechanism. Don't skip writing them even if
they feel like overhead — they're the whole point.

---

## Artifact Reference

```
rpirt/
  01-research.md      — findings, unknowns, constraints
  02-plan.md          — durable decisions, task breakdown, DoD
  03-progress.md      — checklist + deviation log
  04-review.md        — rubric scores + diagnosis, one section per round
  05-test-results.md  — test scenarios + results + remaining risks
```

Medium-complexity tasks (compressed mode): create only `rpirt/plan.md` and `rpirt/review.md`.

---

## Windows / Cursor Compatibility

- No environment-specific changes required. All phases are tool and OS agnostic.
- Sub-agents use the Task tool in Cursor. In Claude Code, use the same Task invocation pattern.
- Artifact paths use forward slashes (`rpirt/01-research.md`) — works on both Windows and Unix.
