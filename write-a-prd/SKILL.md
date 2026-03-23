---
name: write-a-prd
description: Create a PRD through interview and codebase exploration, then deliver as markdown or an optional GitHub issue. Use when writing a PRD, product requirements, or scoping a new feature.
---

1. **Problem & ideas:** Ask for a detailed description of the problem and possible directions.

2. **Codebase:** Explore the repo to validate assumptions and see current architecture.

3. **Alignment:** Interview until the design space is clear (or use the **grill-me** skill if the user wants adversarial Q&A).

4. **Modules:** Sketch major modules to add or change; favor **deep** modules (small interface, meaningful internals). Confirm with the user.

5. **PRD draft:** Use the template below. Default deliverable **markdown in chat or a file path the user chooses**.

6. **GitHub issue:** Create with `gh issue create` **only if** the user explicitly wants GitHub as the system of record.

<prd-template>

## Problem statement

## Solution

## User stories

Numbered list: As a \<role\>, I want \<capability\>, so that \<benefit\>. Be thorough.

## Implementation decisions

Architecture, modules, interfaces, schema/API—avoid ephemeral file paths.

## Testing decisions

Behavior-level tests, boundaries, patterns to mirror.

## Out of scope

## Further notes

</prd-template>

*Adapted from [mattpocock/skills/write-a-prd](https://github.com/mattpocock/skills/tree/main/write-a-prd) (MIT).*
