---
name: setup-pre-commit
description: Set up Husky pre-commit hooks with lint-staged (Prettier), optional typecheck and tests in a Node/JavaScript repo. Use when the user wants pre-commit hooks, Husky, lint-staged, or commit-time format/check.
---

# Setup Pre-Commit Hooks (Node repos)

**Scope:** Repositories with a root `package.json`. For **Python-only** projects, prefer `pre-commit` (Python) or `uv run` + CI—do not force Husky unless the user wants Node tooling.

## What this sets up

- Husky + `lint-staged` + Prettier on staged files
- Optional full-repo `typecheck` and `test` in the hook if scripts exist

## Steps

### 1. Detect package manager

From lockfiles: `pnpm-lock.yaml` → pnpm, `yarn.lock` → yarn, `package-lock.json` → npm, `bun.lockb` → bun. Default npm if unclear.

### 2. Install devDependencies

`husky`, `lint-staged`, `prettier` (adjust command for the package manager).

### 3. Initialize Husky

`npx husky init` (or pnpm/yarn equivalent). Ensures `.husky/` and `prepare` script.

### 4. `.husky/pre-commit`

Typical content:

```
npx lint-staged
npm run typecheck
npm run test
```

Replace `npm` with the detected manager. **Omit** `typecheck` / `test` lines if those scripts are missing—do not invent scripts.

### 5. `.lintstagedrc`

```json
{
  "*": "prettier --ignore-unknown --write"
}
```

### 6. `.prettierrc`

Create only if no Prettier config exists; use project-consistent style or sensible defaults.

### 7. Verify

Run `npx lint-staged` on a scratch change. Ensure hooks run on a test commit (user may need to approve the commit).

## Notes

- Prettier skips unknown binary types with `--ignore-unknown`.
- Full typecheck/tests on every commit can be slow—confirm with the user if they want that or only lint-staged.

*Adapted from [mattpocock/skills/setup-pre-commit](https://github.com/mattpocock/skills/tree/main/setup-pre-commit) (MIT).*
