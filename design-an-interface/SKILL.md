---
name: design-an-interface
description: Generate multiple radically different interface designs for a module using parallel exploration. Use when designing an API, exploring interface options, comparing module shapes, or when the user says "design it twice".
---

# Design an Interface

From *A Philosophy of Software Design* ("Design It Twice"): your first shape is rarely the best. Produce **several meaningfully different** designs, then compare—**design only**, no implementation in this skill unless the user asks.

## Workflow

### 1. Gather requirements

Clarify: problem solved, callers, key operations, constraints (performance, compatibility, existing patterns), what stays internal vs exposed.

### 2. Generate designs (parallel)

Use the **Task** tool with multiple subagents **in parallel** (or sequential deep passes if Task is unavailable). Each subagent must pursue a **different** constraint, for example:

- Minimize surface area (1–3 entry points).
- Maximize flexibility for future use cases.
- Optimize the dominant / happiest path.
- Take inspiration from a named paradigm or library the user cares about.

Each design should include: interface signature, realistic usage example, what complexity is hidden, trade-offs.

### 3. Present

Show each design with signature, usage, and what it hides. Present sequentially so the user can compare.

### 4. Compare

Discuss simplicity, generality vs focus, whether the shape enables a deep module, ease of correct use vs misuse. Use prose; call out where designs diverge most.

### 5. Synthesize

Often the best outcome blends ideas. Offer a recommendation and optional hybrid.

## Anti-patterns

- Designs that are only cosmetically different.
- Skipping comparison.
- Implementing before the user chooses a direction.

*Adapted from [mattpocock/skills/design-an-interface](https://github.com/mattpocock/skills/tree/main/design-an-interface) (MIT).*
