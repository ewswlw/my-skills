---
name: grill-me
description: Interview the user about a plan or design until shared understanding, batching all independent questions together before follow-up batches. Each question includes 4-5 concrete answer options with recommended choices, plus a decision log, clear exit read-back, and no implementation until the user says the plan is ready. Use when stress-testing a plan, getting grilled on a design, or the user says "grill me".
---

Interview the user thoroughly about every aspect of the current plan until you reach a shared understanding. Walk the design tree in **batches**: ask every question that does **not** depend on a prior answer at once, then use the user's answers to form the next batch of dependent follow-up questions.

**Non-negotiable — every question batch** must use this shape so the user can fast-path:

1. **Batch frame:** Briefly name what this batch resolves and why these questions can be answered independently.
2. **Questions first:** List all independent questions for this batch before listing answer options.
3. **Answer options below:** Under each question, provide at least **4-5 possible answers**. Mark one or more options as **`[RECOMMENDED]`** with one short rationale.
4. **Reply options:** State that the user may answer **`approve all`** (accept every recommendation), **`approve Q1, override Q2: ...`**, or free-form corrections.
5. **Next-batch note:** If some later questions depend on this batch, say they will come in the next batch after these answers are resolved.

**Before stating a recommendation:** If the best answer is knowable from the **repository**, search or read the codebase first (e.g. `rg`, Glob, Read, subagent exploration) instead of guessing. If still uncertain after a repo check, state what you assumed in the rationale.

**Dependency rule:** Do not ask questions whose wording, options, or recommendation materially depend on an unresolved prior answer. Put those into a later batch. If a question is mostly independent but has a minor dependency, state the assumption and include it in the current batch only if the answer will still be useful.

**Decision log (every turn after the first answer):** Maintain a **## Decisions so far** section in the message (or refresh it each turn). After each `approve all`, partial approval, or `override`, append one compact bullet per resolved question, for example: `- *Q:* … *Recommended:* … *Resolved:* …` Keep it scannable; on user request, offer a copy-paste block for a PRD, brainstorm, or spec.

**Example — one batch**

```markdown
This batch resolves the independent foundations: storage, audience, and success measure. These choices do not depend on each other, so answer them together.

## Questions

**Q1. What should store the local cache?**

**Q2. Who is the primary user?**

**Q3. What is the main success measure?**

## Answer Options

**Q1. What should store the local cache?**
- A. SQLite **[RECOMMENDED]** — no server process, file lives beside the app, good enough for single-user workflows.
- B. JSON files
- C. Postgres
- D. In-memory only
- E. No cache

**Q2. Who is the primary user?**
- A. The current user only **[RECOMMENDED]** — simplest scope unless collaboration is explicit.
- B. A small internal team
- C. External customers
- D. Admin operators
- E. Unsure / decide later

**Q3. What is the main success measure?**
- A. Faster task completion **[RECOMMENDED]** — easiest to observe during workflow testing.
- B. Fewer errors
- C. Lower infrastructure cost
- D. Better auditability
- E. Higher user satisfaction

**Reply options:** `approve all`, `approve Q1 and Q3, override Q2: small internal team`, or your own answer.

**Next batch:** After these are resolved, ask dependent questions about cache limits, permissions, and instrumentation.

---

## Decisions so far
- (none yet — first reply below)

```

User: `approve all`

Assistant: Record all approved decisions, then ask the next batch of dependent questions with **## Decisions so far** updated to include one resolved line per prior question.

**When to stop — "solid enough"**

- The user may end the interview with phrases like **plan is ready**, **proceed**, **good to implement**, or **we're done grilling**.
- Before stopping, give a short **read-back**: scope, main constraints, explicit **non-goals** or out-of-scope items, and any major risks you surfaced.
- Optional sanity check (only if it helps the user): dependencies addressed, risks named, out-of-scope stated — not a gate to argue over.

**Handoff (after read-back, one line):** Suggest a sensible next step and let the user pick — e.g. **`/ce-brainstorm`** or deeper exploration of one thread, **`/project-spec`** or a written spec if build clarity is still missing, or **start implementing** if the plan is small and settled.

**Implementation guard:** Do not start **implementing** (code edits, file writes for the build, or executing the plan) until the user confirms the plan is solid enough to proceed. Clarifying questions and updating the decision log are fine.

Prefer **complete independent batches** over one-question turns. On later turns, briefly confirm prior decisions if the tree branches, then ask the next dependent batch.

Fork and upstream: see `references/upstream.md`.

*Adapted from [mattpocock/skills/grill-me](https://github.com/mattpocock/skills/tree/main/grill-me) (MIT).*
