# Project Constitution

## Technology Stack

- Skill packaging: Markdown (`SKILL.md`, `references/`), Excel workbooks (`.xlsx`)
- Version control: Git; use **Git LFS** for `raw-data/*.xlsx` when the remote rejects large binaries or the repo standardizes on LFS

## Project Structure

- `SKILL.md` — Agent entrypoint and workflow summary
- `references/` — Data dictionary, loaders/merge patterns, features, signals, testing patterns
- `raw-data/` — Optional RecessionALERT workbook mirror (snake_case filenames on disk inside the skill); `README.md` with vendor-to-skill name mapping, sizes, last-refreshed note, hash checks, and refresh rules
- `project-spec.md` — Full XML requirements for this skill-data bundle
- `project-constitution.md` — Hard boundaries (this file)

## Executable Commands

- Build: _Not applicable (documentation and bundled data asset)._
- Test: _No automated test command is defined inside this skill._ Validation of Excel schema and merges remains the responsibility of consumer code (e.g. `Coding Projects/Recession Alert/spx_timing_strategy.py` and its embedded tests), which is **out of scope** for the implementation gate of this bundle unless explicitly added in a follow-up project.

## Hard Boundaries

- **Vault source of truth:** In this vault, `Coding Projects/Recession Alert/Raw Data/` is authoritative and keeps vendor filenames. Skill-local `raw-data/` files are mirrors only and must not silently override the vault source.
- **Mirror naming contract:** If `raw-data/` is populated, it SHALL use exactly these four mirror filenames: `cmhi_data.xlsx`, `monthly_data_4.xlsx`, `optimum_data.xlsx`, `weekly_data_2.xlsx`. Do not rename or substitute without updating `project-constitution.md`, `project-spec.md`, `raw-data/README.md`, and every skill reference that cites Raw Data filenames.
- **Atomic refresh:** When updating from vendor exports, replace **all four** workbooks together in one logical change. Partial refresh (mixed vintages) is forbidden.
- **Licensing / distribution:** Do not publish `raw-data/` to a **public** repository or otherwise redistribute subscription-bound exports unless terms explicitly allow it. Prefer private or local-only remotes for these binaries.
- **Vault Python:** Consumer code in `Coding Projects/Recession Alert/spx_timing_strategy.py` validates and loads the vault source by default. Use skill mirrors only outside the vault or after explicit divergence checks.
- **Schema honesty:** Never invent sheets or columns. Loaders and documentation must match the vendor Excel schema; missing or mismatched structural elements **fail fast** with a clear error.
