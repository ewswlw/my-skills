---
name: grill-me
description: Interview the user relentlessly about a plan or design until shared understanding, walking the decision tree branch by branch. Use when the user wants to stress-test a plan, get grilled on a design, or says "grill me".
---

Interview the user thoroughly about every aspect of the current plan until you reach a shared understanding. Walk the design tree in order and resolve dependencies between decisions one step at a time.

For each question:

1. Give **your recommended answer** (with a short rationale).
2. If the answer is knowable from the **repository**, search or read the codebase first (e.g. `rg`, Glob, Read, Task explore subagent) instead of guessing.
3. Prefer **one focused question at a time** so tradeoffs stay clear.

Do not start implementing until the user confirms the plan is solid enough to proceed.

*Adapted from [mattpocock/skills/grill-me](https://github.com/mattpocock/skills/tree/main/grill-me) (MIT).*
