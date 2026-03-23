---
name: triage-issue
description: Triage a bug by exploring the codebase for root cause, then produce a TDD fix plan and optionally a GitHub issue. Use when triaging a defect, investigating a failure, or planning a test-first fix.
---

# Triage issue

Investigate the problem, identify **root cause**, and produce a **vertical-slice TDD plan** (red/green per behavior). Minimize back-and-forth questions: start from the user's report and code.

## Process

### 1. Capture

If the report is empty, ask one question: what fails vs what should happen?

### 2. Explore

Use **Task** (explore) or direct search. Track: where it surfaces, call path, root cause, related tests, recent changes (`git log` on hot files if useful).

### 3. Fix approach

Minimal change addressing root cause; affected modules; regression vs missing feature vs design issue.

### 4. TDD plan

Ordered RED/GREEN cycles—**one test at a time**, behavior through public interfaces. Avoid locking the plan to file paths that will move; describe behavior and contracts.

### 5. GitHub issue

**Only if the user asks** to file remotely: create with `gh issue create` using a template with Problem, Root cause (durable description), TDD plan, acceptance criteria.

Otherwise paste the full issue body in chat.

Do **not** auto-create issues without approval.

*Adapted from [mattpocock/skills/triage-issue](https://github.com/mattpocock/skills/tree/main/triage-issue) (MIT).*
