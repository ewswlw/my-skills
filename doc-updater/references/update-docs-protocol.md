# Documentation update protocol (any repository)

Generalized from a project-local `/update-docs` command. **Do not hardcode** one app’s directory names; **discover** each section at run time unless the user provided `scope:` prefixes in the invoke message.

**Companion rules:** `SKILL.md` pre-flight, `project-constitution.md`, `project-spec.md` in the same skill folder.

---

## CRITICAL execution protocol

1. **Priority:** run this workflow first for the session slice; drop other tasks unless the user overrides.
2. **NEVER modify application source** (`*.py`, `*.ts`, `*.tsx`, `*.js`, `*.jsx`, `*.html`, `*.css`, etc.) — documentation, **`.cursor/rules/**/*.mdc`**, root **`CHANGELOG.md`** (if present), and **`{doc_root}/update_log.md`** only.
3. **NEVER write** without **explicit user approval** after a full dry-run — **mandatory gate**.
4. **NEVER assume** date/time — run a shell timestamp before any log (see `SKILL.md`).
5. **NEVER overwrite** **`[PLANNED]`**, **`[FUTURE]`**, **`[PROPOSED]`** sections — skip; list under **Manual Review**.
6. **NEVER delete** documented schemas when data files are missing — mark **schema comparison skipped**.
7. **NEVER auto-commit** — offer `git add` + suggested message only.
8. **Rules (`.mdc`)** require **separate** approval from markdown documentation.
9. **Code is truth** — on conflict, update **docs** to match code (or Manual Review if unsafe to touch).
10. **Timestamps** in user-facing headers: agree a format with the repo (default `YYYY-MM-DD HH:MM ET`).
11. **Completion line:** **`/doc-updater` completed.**

---

## Discover `doc_root`

- If `documentation/` exists → **`doc_root = documentation/`**
- Else if `docs/` exists → **`doc_root = docs/`**
- Else → **ask** the user where markdown documentation lives, or scope to `scope:` only.

**Update log path:** `{doc_root}/update_log.md` (create on first successful write if approved).

---

## Phase 1 — Mode and timestamp

### 1.1 `CURRENT_TIMESTAMP`

Store from shell (see `SKILL.md`).

### 1.2 FULL vs INCREMENTAL

If `{doc_root}/update_log.md` exists and contains **`## Run:`** → **INCREMENTAL**: parse the **most recent** run’s timestamp as `LAST_UPDATE_TIMESTAMP`. Otherwise → **FULL AUDIT**.

Report: `Running in [FULL AUDIT / INCREMENTAL] mode. Last documentation update: [LAST_UPDATE_TIMESTAMP or Never].`

---

## Phase 2 — Four-track inspection

Use **Task** `subagent_type="explore"` **×4** when available; otherwise run the **same four tracks** with parallel tools.

### Agent 1 — Directory tree

**Prompt (template):** Build a hierarchical view of **git-tracked** files: `git ls-files`. Apply **`scope:`** filters if provided. Group by top-level directory; list extensions. Return a tree suitable for comparing to “project structure” docs and rules.

### Agent 2 — Module / API extraction (language-adaptive)

**If Python is in use** (`*.py` present, `pyproject.toml`, etc.):

- For each relevant `*.py` (respect `scope:`; prefer packages, `src/`, `*_pipeline/`, `analytics/`, root entry scripts), extract: module docstring (first line), class names + method signatures (name, params, return), top-level function signatures, module-level `UPPER_SNAKE` constants, imports. Organize by path.

**If no Python but JS/TS exists:**

- Enumerate `*.ts`, `*.tsx`, `*.js` (exclude `node_modules`, `dist`). For each file, collect exports (e.g. `export function`, `export const`, `export class`, default exports) and **file path**. Do not claim full type inference if the environment cannot run `tsc`.

**If neither:**

- Produce a **file inventory** with sizes/roles from names and any README; **no** fabricated signatures.

### Agent 3 — Data files (parquet)

Run **only if** tracked `*.parquet` exist and count ≤ **30** for this run (see `SKILL.md` cap). For each selected file:

- Schema: `pyarrow.parquet.read_schema` or equivalent.
- Row count: file metadata.
- **Optional** “latest date” only if a sensible time column exists (try common names: `Date`, `date`, `timestamp`); if missing, note “no time column.”

If **no parquet**, skip entirely. If **deferred** over cap, list paths under **Deferred data inspection**.

### Agent 4 — Git

**FULL:** e.g. last 50 commits, adds, deletes, renames, `git status --short`.

**INCREMENTAL:** same with `--since="LAST_UPDATE_TIMESTAMP"` (adjust to valid git date format).

### 2.5 Merge

Single **inspection dataset** for Phase 3.

---

## Phase 3 — Staleness analysis and change manifest

### 3.1 Read targets in parallel

**Rules:** all **`.cursor/rules/**/*.mdc`** (respect `scope:` if it excludes `.cursor`, then only read rules if in scope — if nothing to read, say so).

**Docs:** all **`{doc_root}/*.md`** except `README.md` and `update_log.md` unless you need them for context; **include** `{doc_root}/README.md` for index regen later.

**Root:** `CHANGELOG.md` if present.

**Optional read:** target repo `project-spec.md` / `project-constitution.md` for terminology — **do not edit** unless explicitly approved later.

### 3.2 Categories

| Category | Meaning |
|----------|--------|
| `NEW_FILES` | On disk / in git, not reflected in docs |
| `REMOVED_FILES` | Referenced in docs but gone (not inside [PLANNED]/[FUTURE]/[PROPOSED]) |
| `RENAMED_FILES` | From git rename detection vs doc text |
| `SCHEMA_DIFFS` | Data file schema vs documented |
| `SIGNATURE_CHANGES` | API vs documented |
| `STALE_TIMESTAMPS` | Doc “Last Updated” vs material code changes |
| `MISSING_DOCS` | Major area with no doc coverage |

### 3.3 Manifest table

```
CHANGE MANIFEST (YYYY-MM-DD HH:MM ET)
Mode: [FULL AUDIT / INCREMENTAL]

| # | Category | Item | Affected Docs |
...
```

Ask: **Change Manifest ready. Proceed to draft updates? (yes/no)** and wait.

---

## Phases 4–5 — Draft in memory (no writes yet)

### Rules (`.mdc`)

Align **directory tree** with Agent 1; **pipelines/modules** with Agent 2; **logging paths** with actual log dirs if your project documents them; **execution** with real CLI entrypoints; **patterns** with real code style; **web** with any dashboard paths; **overview** with `pyproject.toml` / `package.json` deps when relevant; **paths** with path rules.

### Markdown under `{doc_root}`

For each file, map sections to manifest items. **Data architecture**-style files: sync schema tables from Agent 3. **Business logic** docs: align formulas with docstrings or code. **Integration** docs: verify file paths exist. Respect **[PLANNED]** files: **no** overwrite; at most a short **note** pointing to live schema doc if needed.

### New files

If `MISSING_DOCS`: prepare a **new** `{doc_root}/[Module].md` from the template in the original command (Overview, File Structure, Configuration, I/O, Key APIs, Execution). **Do not write** until approval.

### Phase 7 — README index

If `{doc_root}/README.md` exists, plan regeneration of index sections from sibling `.md` titles and first paragraphs. If **no** README, **skip** and list in manifest.

### Phase 8 — CHANGELOG

If `CHANGELOG.md` **exists**, read recent entries; draft new entries matching **style**. **Deduplicate** against existing text. Insert **below** any top reminder block. If **no** `CHANGELOG.md`, **skip** (unless user asked to create one — not default).

### Phase 9 — Documentation health score

Compute (weights from spec / Bond-RV-App reference):

- **Coverage (30%)** — documented modules vs discovered “module” units (pipeline dirs, major packages, entry scripts).
- **Freshness (20%)** — “Last Updated” vs wall clock.
- **Schema (20%)** — matching columns vs documented (skip missing files without penalty).
- **CHANGELOG (15%)** — recency of last entry if file exists; else neutral or 0 with note.
- **Paths (15%)** — paths mentioned in docs/rules that exist on disk or in git.

Show **Total** and sub-scores.

---

## Phase 10 — Dry-run gate (mandatory)

1. Summary table of **file → action** (UPDATE / REGEN / APPEND / CREATE).
2. Inline **before/after** for substantive edits.
3. **Separate** “Rules file changes” block — user must confirm rules (cannot hide inside compact if `.mdc` change exists).
4. **CHANGELOG** entries: show draft entries; if repo uses per-entry review, support **[Accept / Edit / Reject]** per entry.
5. **Manual Review** list (planned sections, deferred parquets, ambiguous removals).
6. **Approval options:** `[1] All` / `[2] Docs only` / `[3] Rules only` / `[4] Selective` / `[5] Cancel`  
   **Compact path** (only if allowed in `SKILL.md`): one approve/cancel for small, no-rules batches.

**Wait** for explicit choice. **No writes** until then.

---

## Phase 11 — Write

Only approved files. Update **“Last Updated”** where your style requires. Append **`## Run: …`** to `{doc_root}/update_log.md` with mode, file lists, skips, manual review, health table row.

---

## Phase 12 — Git

`git status --short`. Offer:

```
git add <approved paths>
```

Suggested message: e.g. `docs: sync documentation and rules (YYYY-MM-DD HH:MM)` — **do not** `git commit`.

---

## Phase 13 — Completion

State **`/doc-updater` completed.`** and print:

- Health score (and delta if you stored previous in log)
- Counts: updated, created, CHANGELOG entries, manual review items, deferred parquets, staged (yes/no), log path

---

## Windows vs Unix

Prefer **PowerShell** one-liner for timestamps on Windows; on macOS/Linux use `date`. Keep paths **forward-slash** in markdown where possible for portability.

---

## On missing tools

- **No Python:** skip parquet phase; state clearly.
- **No git:** refuse FULL/INCREMENTAL git phases; use filesystem-only tree with a warning.
- **No Task subagent:** already covered — parallelize with native tools.
