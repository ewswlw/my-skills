---
name: prd-to-issues
description: Break a PRD into independently workable GitHub issues using tracer-bullet vertical slices. Use when converting a PRD to issues, implementation tickets, or scoped work items.
---

# PRD to issues

Decompose a PRD into **vertical slices** (tracer bullets): each issue is a thin, end-to-end increment, not a single layer across the whole feature.

## Process

### 1. Locate the PRD

From issue number/URL, file path, or pasted content. Use `gh issue view` only if the **GitHub CLI is available** and the user wants live issues—otherwise read from files or chat.

### 2. Explore the codebase (optional)

If needed to ground estimates and dependencies.

### 3. Draft slices

Each slice:

- Cuts through the relevant stack for **one** narrow behavior.
- Is independently demoable or verifiable when done.
- Label **HITL** if it needs a human decision or review; **AFK** if implementable without blocking human input. Prefer AFK where safe.

### 4. Quiz the user

Present numbered slices with title, type (HITL/AFK), blockers, and user stories covered. Adjust until approved.

### 5. Create GitHub issues

**Only after explicit user approval** to create remote issues:

- Create with `gh issue create` in dependency order so "Blocked by" can reference real numbers, **or**
- Paste the full set of issue bodies for manual creation.

Never bulk-create or close issues on the user's behalf without confirmation.

Use a consistent body template: parent PRD link, what to build, acceptance criteria, blockers, user stories addressed.

*Adapted from [mattpocock/skills/prd-to-issues](https://github.com/mattpocock/skills/tree/main/prd-to-issues) (MIT).*
