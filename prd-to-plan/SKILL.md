---
name: prd-to-plan
description: Turn a PRD into a multi-phase implementation plan using tracer-bullet vertical slices, saved as a local Markdown file under ./plans/. Use when breaking down a PRD, building phased plans, or when the user says "tracer bullets".
---

# PRD to plan

Break a PRD into **vertical slices** (tracer bullets). Output is a Markdown file under **`./plans/`** in the repo (create the folder if missing).

## Process

### 1. Confirm PRD source

PRD should be in context, a file path, or a linked issue. If missing, ask the user to paste or point to it.

### 2. Explore the codebase

Understand architecture, layers, and patterns so slices are realistic.

### 3. Durable decisions

Capture stable choices that phases share: routing, schema shape, auth model, external boundaries. Put these in the plan header.

### 4. Draft vertical slices

Each phase is a **thin end-to-end** slice (not "all DB then all API"). Rules:

- Completes a narrow path through relevant layers; demoable or verifiable alone.
- Prefer several thin phases over a few thick ones.
- Avoid naming incidental file/function names that will churn; **do** include durable decisions (routes, model names).

### 5. Quiz the user

Iterate on granularity and merges/splits until they approve.

### 6. Write the plan file

Path example: `./plans/<feature-slug>.md`. Use clear phase headings, user story references, acceptance criteria per phase.

## Python note

If the project uses **uv**, use `uv run` for any project scripts invoked while validating the plan—never assume global Python.

*Adapted from [mattpocock/skills/prd-to-plan](https://github.com/mattpocock/skills/tree/main/prd-to-plan) (MIT).*
