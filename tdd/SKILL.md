---
name: tdd
description: Test-driven development with red-green-refactor and vertical slices. Use when building features test-first, fixing bugs with TDD, or when the user says "red-green-refactor" or tracer-bullet tests.
---

# Test-Driven Development

## Philosophy

**Core principle:** Tests should verify behavior through **public interfaces**, not implementation details. Code may change entirely; good tests stay.

**Good tests** read like specs and use integration-style coverage of real paths where practical. **Bad tests** mock internals, assert on private details, or break on refactors that preserve behavior.

See [tests.md](tests.md), [mocking.md](mocking.md), [deep-modules.md](deep-modules.md), [interface-design.md](interface-design.md), [refactoring.md](refactoring.md).

## Anti-pattern: horizontal slices

Do **not** write the full test suite, then all implementation. Use **vertical** tracer bullets: one failing test → minimal pass → repeat.

## Workflow

### 1. Planning

Confirm public surface and prioritized behaviors with the user. You cannot test everything—agree on what matters.

### 2. Tracer bullet

One test for one behavior: RED then GREEN with minimal code.

### 3. Incremental loop

Repeat; no speculative features. One test at a time.

### 4. Refactor

Only when GREEN. Never refactor while RED.

## Checklist per cycle

- [ ] Test describes behavior, not internals
- [ ] Uses public interface
- [ ] Would survive internal refactors
- [ ] Smallest code to pass this test

*Adapted from [mattpocock/skills/tdd](https://github.com/mattpocock/skills/tree/main/tdd) (MIT). Companion files included alongside this skill.*
