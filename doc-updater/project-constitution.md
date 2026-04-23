# Project Constitution

## Technology Stack
- **Skill format:** Markdown (Claude/Cursor `SKILL.md` + `references/*.md`); no runtime language version required for the skill package itself
- **Target repositories:** Any; inspection uses host shell, `git`, and optional `python` for parquet (when present)
- **Database:** None. Persistent artifacts are **files only** in the user’s repo (`update_log.md`, `CHANGELOG.md`, etc.)

## Project Structure
- `C:\Users\Eddy\.claude\skills\doc-updater\` (or the user’s `~/.claude/skills/doc-updater/`)  
  - `SKILL.md` — entry point, hard rules, pre-flight, pointers to `references/`
  - `project-constitution.md` — immutable constraints (this file)
  - `project-spec.md` — full requirements (XML)
  - `references/update-docs-protocol.md` — full phased procedure for any project

## Executable Commands
- **Build:** n/a (documentation skill)
- **Test:** n/a (manual: invoke `/doc-updater` in a test repo and verify dry-run)
- **Timestamp (Windows):** `powershell -Command "Get-Date -Format 'yyyy-MM-dd HH:mm'"` before any log entry
- **Timestamp (Unix):** `date '+%Y-%m-%d %H:%M'`

## Hard Boundaries
- **Never** modify application source in the user’s project by default: e.g. `*.py`, `*.ts`, `*.tsx`, `*.js`, `*.jsx`, `*.html`, `*.css`, `*.go`, `*.rs`, `*.java` — only documentation, **`.cursor/rules/**/*.mdc`**, and agreed doc-adjacent files. (Exception: only if the user’s own constitution explicitly reclassifies a path as “docs.”)
- **Never** `git commit`; at most offer `git add` with a suggested message.
- **Never** write doc/rule/CHANGELOG changes without passing the **mandatory dry-run and approval** gate.
- **Never** assume date/time; always run a real shell timestamp command.
- **Never** overwrite content in sections tagged **`[PLANNED]`**, **`[FUTURE]`**, or **`[PROPOSED]`** — skip; list in Manual Review.
- **Never** delete documented data schemas when raw files (e.g. parquet) are missing — mark *schema comparison skipped*.
- **Rules (`.mdc`) changes** require a **separate** user approval block from other docs.
- **Default:** do **not** edit the target repo’s `project-spec.md` or `project-constitution.md` unless the user explicitly includes them in selective approval.
- **Invocation-only:** the skill is used **only** when the user clearly invokes it (`/doc-updater`, `@doc-updater`); if unclear, **ask once** before running the full protocol.
- **Pre-flight:** if **git-tracked file count** exceeds **8,000** or **parquet** count exceeds **50**, **stop** and require an explicit sub-scope, continuation, or cap before deep inspection.
- **Parquet deep-read cap:** at most **30** parquet files fully inspected per run unless the user increases scope; list remainder as *not inspected this run*.

## Confidentiality
- Use **repo-relative** paths in manifests and `update_log.md` (no machine root paths in shipped logs).
- Warn when broad enumeration may be sensitive; allow optional `scope: path,path` on the same line as the invoke to limit inspection.

## Code vs documentation truth
- When code and documentation disagree, **update documentation** to match the code (not the reverse), except items routed to **Manual Review**.
