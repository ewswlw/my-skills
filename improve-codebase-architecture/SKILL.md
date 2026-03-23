---
name: improve-codebase-architecture
description: Explore a codebase for architectural improvement opportunities, emphasizing deep modules and testability. Use when the user wants architecture review, refactoring themes, or clearer module boundaries.
---

# Improve codebase architecture

Explore the codebase as an unfamiliar contributor would: note **friction**, **shallow modules**, and places where **boundary tests** would replace scattered unit tests. Inspired by John Ousterhout's *deep module* idea: small interface, meaningful implementation.

## Process

### 1. Explore

Use **Task** (explore subagent) or systematic search. Look for:

- Concepts spread across many small files with no clear owner
- Interfaces nearly as large as implementations
- Tests that break on refactors without behavior changes
- Coupling that raises integration risk at seams

Friction you feel when navigating is signal.

### 2. Present candidates

Numbered list. For each: **cluster** of modules, **why** they're coupled, **dependency category** (see [REFERENCE.md](REFERENCE.md)), **test impact** (what could move to boundary tests).

Do not propose final interfaces yet. Ask which candidate to drill into.

### 3. User picks one candidate

### 4. Frame the problem

Before parallel design work, give a concise explanation: constraints, dependencies, rough sketch of the problem (not a final API).

### 5. Parallel interface designs

Use **Task** with multiple subagents in parallel. Different constraints per agent, e.g. minimal surface, maximum flexibility, best default path, ports-and-adapters for boundaries.

Each proposal: signature, usage example, hidden complexity, dependency handling, trade-offs.

Compare in prose; give a **recommendation**.

### 6. User selects or adjusts direction

### 7. Optional GitHub issue (RFC)

**Only with explicit user consent:** create an issue (e.g. `gh issue create`) using the template in [REFERENCE.md](REFERENCE.md), or paste the draft into chat for the user to file manually.

Never create or edit remote issues without confirmation.

*Adapted from [mattpocock/skills/improve-codebase-architecture](https://github.com/mattpocock/skills/tree/main/improve-codebase-architecture) (MIT).*
