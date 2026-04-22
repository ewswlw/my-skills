# Project Constitution

## Technology Stack

- Skill packaging: Markdown (`SKILL.md`, `references/`), Excel workbooks (`.xlsx`)
- Version control: Git; use **Git LFS** for `raw-data/*.xlsx` when the remote rejects large binaries or the repo standardizes on LFS

## Project Structure

- `SKILL.md` — Agent entrypoint and workflow summary
- `references/` — Data dictionary, loaders/merge patterns, features, signals, testing patterns
- `raw-data/` — Four canonical RecessionALERT exports (snake_case filenames on disk inside the skill); `README.md` with vendor↔skill name mapping, sizes, last-refreshed note, and refresh rules
- `project-spec.md` — Full XML requirements for this skill-data bundle
- `project-constitution.md` — Hard boundaries (this file)

## Executable Commands

- Build: _Not applicable (documentation and bundled data asset)._
- Test: _No automated test command is defined inside this skill._ Validation of Excel schema and merges remains the responsibility of consumer code (e.g. `Coding Projects/Recession Alert/spx_timing_strategy.py` and its embedded tests), which is **out of scope** for the implementation gate of this bundle unless explicitly added in a follow-up project.

## Hard Boundaries

- **`raw-data/` SHALL contain exactly these four tracked workbook files:** `cmhi_data.xlsx`, `monthly_data_4.xlsx`, `optimum_data.xlsx`, `weekly_data_2.xlsx`. These names are **structural**. Do not rename or substitute without updating `project-constitution.md`, `project-spec.md`, `raw-data/README.md`, and every skill reference that cites Raw Data filenames.
- **Atomic refresh:** When updating from vendor exports, replace **all four** workbooks together in one logical change. Partial refresh (mixed vintages) is forbidden.
- **Licensing / distribution:** Do not publish `raw-data/` to a **public** repository or otherwise redistribute subscription-bound exports unless terms explicitly allow it. Prefer private or local-only remotes for these binaries.
- **Vault Python:** Do not modify `Coding Projects/Recession Alert/spx_timing_strategy.py` or other vault application code as part of this bundle’s implementation unless a separate change request authorizes it. The vault `Coding Projects/Recession Alert/Raw Data/` folder remains the **human export drop zone** and may keep vendor filenames; the skill holds the **portable snake_case** copies.
- **Schema honesty:** Never invent sheets or columns. Loaders and documentation must match the vendor Excel schema; missing or mismatched structural elements **fail fast** with a clear error.
