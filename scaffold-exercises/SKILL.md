---
name: scaffold-exercises
description: Scaffold course-style exercise folders with problem/solution/explainer layouts. Use when the repo uses Total TypeScript-style exercise tooling (ai-hero-cli); otherwise use generic scaffolding only.
---

# Scaffold exercises

## When this skill applies

**Full lint workflow (original upstream):** Repositories that run:

`pnpm ai-hero-cli internal lint`

If that command **does not exist** in the repo, **do not** invent it. Instead:

- Create a simple folder layout the user chooses (`section/exercise/readme.md`, etc.).
- Run **only** the repo's existing linters/formatters (e.g. `pnpm lint`, `npm test`, `uv run ruff check`).

## Upstream layout (TypeScript course repos)

When the CLI **is** present:

- Sections: `exercises/XX-section-name/`
- Exercises: `XX.YY-exercise-name/` with dash-case names
- Subfolders: at least one of `problem/`, `solution/`, `explainer/` per exercise
- Each active subfolder needs a non-empty `readme.md`; code variants may need `main.ts` per rules

**Run** `pnpm ai-hero-cli internal lint` after scaffolding and fix until clean.

## Moving exercises

Prefer `git mv` to preserve history; re-run lint after renames.

## Safety

- Never run arbitrary `pnpm`/`npm` installs unless the user asked for dependency changes.
- Confirm the user is in the intended course repo before mass-creating directories.

*Adapted from [mattpocock/skills/scaffold-exercises](https://github.com/mattpocock/skills/tree/main/scaffold-exercises) (MIT).*
