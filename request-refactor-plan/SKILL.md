---
name: request-refactor-plan
description: Create a detailed refactor plan with small commits via interview, then optionally file it as a GitHub issue. Use when planning a refactor, RFC-style change, or safe incremental steps.
---

Follow these steps unless the user asks for a lighter pass:

1. **Problem:** Ask for a detailed description of the problem and candidate solutions.

2. **Verify:** Explore the repo to validate assumptions and see current structure.

3. **Options:** Surface alternatives they may not have considered.

4. **Interview:** Go deep on implementation intent, risks, and constraints.

5. **Scope:** Agree explicitly on what is in/out of scope.

6. **Tests:** Check existing coverage; if weak, agree on testing strategy before refactoring.

7. **Commits:** Break work into **small** commits that each leave the repo in a working state (Fowler-style).

8. **Deliverable:** Produce the plan using the template below. **Do not** create a GitHub issue unless the user explicitly asks—offer the draft and paste the template into chat by default.

<refactor-plan-template>

## Problem statement

## Solution

## Commits

Ordered list of tiny commits; each step keeps the system working.

## Decision document

Modules, interfaces, architecture, schema/API contracts—**without** fragile file paths or code snippets.

## Testing decisions

What behavior to test, at which boundaries, patterns to mirror from existing tests.

## Out of scope

## Further notes (optional)

</refactor-plan-template>

*Adapted from [mattpocock/skills/request-refactor-plan](https://github.com/mattpocock/skills/tree/main/request-refactor-plan) (MIT).*
