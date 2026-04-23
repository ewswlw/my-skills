---
name: doc-updater
description: "Invocation only — do not load for general documentation work. Synchronize a repository’s markdown documentation and .cursor rules with the actual codebase (inspection, change manifest, optional health score, mandatory dry-run approval, update log, optional git add). Use ONLY when the user explicitly runs /doc-updater, /doc updater, or @doc-updater. If activation is unclear, ask once. Not for casual doc questions or one-off README edits. Optional on the same line: scope: rel/path,rel/path — limits enumeration. Optional: say compact approval for a shorter gate when the protocol allows it."
---

# doc-updater (`/doc-updater`)

Portable documentation sync. **Code is the source of truth**; update **docs and `.mdc` rules**, not application source, unless the repo’s own constitution says otherwise.

## Before any work

1. **Priority** this workflow for the current turn unless the user says otherwise.
2. Get **`CURRENT_TIMESTAMP`** with a real shell command (no guessing). Prefer **`YYYY-MM-DD HH:MM ET`** in headings; if the repo’s constitution specifies another zone, use that and say so once.
3. **Pre-flight (mandatory):**
   - Count git-tracked files (e.g. `git ls-files | wc -l` or PowerShell `Measure-Object`).
   - Count tracked `*.parquet` (e.g. `git ls-files '*.parquet'`).
   - If **tracked files &gt; 8,000** or **parquet files &gt; 50**, **stop** and ask: narrow with inline **`scope: path,path`**, **continue with cap**, or **abort**.
4. **Scope:** If the user’s message includes **`scope: a,b`**, treat `a` and `b` as repo-relative path prefixes; filter `git ls-files` and doc reads to those prefixes where reasonable.
5. **Read the full procedure:** `references/update-docs-protocol.md` (all phases, in order).

## Hard never-forgets

- **Never** write without passing the **dry-run approval** gate in the reference.
- **Never** `git commit`; only offer **`git add`** after writes.
- **Never** destroy **`[PLANNED]` / `[FUTURE]` / `[PROPOSED]`** blocks — **skip**; put in **Manual Review**.
- **`.mdc` rule edits** get a **separate** approval section from markdown docs.
- **Missing parquet (or other data files):** do **not** remove documented schema text; mark **schema comparison skipped**.
- **Default:** target repo’s **`project-spec.md` / `project-constitution.md`** are **read for alignment** — **do not edit** unless the user explicitly approves them in a selective list.

## Language and data detection

- **Python present** (`pyproject.toml` and/or `*.py`): use Python-oriented extraction (see reference).
- **No Python, but `package.json` / `tsconfig`:** prefer listing **exported** or **routed** symbols from `*.ts`/`*.tsx`/`*.js` via structured search (not full typechecker); avoid claiming full AST if impractical.
- **Neither:** tree + `git ls-files` + README; **no** fake signatures.
- **Parquet:** if there are **no** tracked `*.parquet` files, skip the data-metadata phase. If there are **&gt; 30** parquets, inspect **at most 30** (newest by `git` log mtime or user-specified list); list the rest as **deferred this run**.

## Two-tier approval

- **Default:** full summary + per-file / key-section before/after; separate **Rules** block; rules cannot be “silently” inside a compact pass.
- **Compact:** only if the user says **`compact approval`**, the change set is **&lt; 8 files**, and **no** `.mdc` files are modified — one combined approve/cancel. If **any** `.mdc` changes, use the default gate.

## Innovation (inline invoke helpers)

- **`scope: a,b`**: comma-separated repo-relative prefixes to limit inspection and manifest noise.
- **`compact approval`**: use the short gate only when allowed above.

## Completion

End with: **`/doc-updater` completed.** and the final summary from the reference.

## Bundled specs (this skill’s own product docs)

- `project-constitution.md` — non-negotiable rules.
- `project-spec.md` — full requirements (XML).
- `references/update-docs-protocol.md` — end-user protocol to run in **any** repository.
