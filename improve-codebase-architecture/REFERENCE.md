# Reference

## Dependency categories

When assessing a candidate for deepening, classify dependencies:

### 1. In-process

Pure computation, in-memory state, no I/O. Often straightforward to merge and test at a boundary.

### 2. Local-substitutable

Dependencies with local test stand-ins (e.g. in-memory DB, temp dirs). Deepening is attractive when a substitute exists for tests.

### 3. Remote but owned (ports & adapters)

Your services across a network. Define a port at the module boundary; production and tests use different adapters.

### 4. True external

Third-party APIs you do not control. Mock or fake at the boundary only.

## Testing strategy

- Prefer **boundary** tests on the module's public interface over brittle tests of internals.
- When deepening replaces shallow modules, **delete redundant** tests that only checked internal wiring.

## Issue template

Use when filing a GitHub issue after user approval:

<issue-template>

## Problem

Architectural friction: shallow modules, tight coupling, integration risk, navigation cost.

## Proposed interface

- Signature and types
- Usage example
- What complexity is hidden

## Dependency strategy

Which category applies and how dependencies are injected or substituted in tests.

## Testing strategy

- New boundary tests to add
- Old tests to remove or rewrite
- Test doubles / adapters needed

## Implementation recommendations

Durable guidance **not** tied to ephemeral file paths: responsibilities, hidden details, migration path for callers.

</issue-template>

*From [mattpocock/skills/improve-codebase-architecture](https://github.com/mattpocock/skills/tree/main/improve-codebase-architecture) (MIT).*
