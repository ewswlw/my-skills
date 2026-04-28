# RecessionALERT Raw Data Mirror

The authoritative source for this machine is the vault export folder:
`Coding Projects/Recession Alert/Raw Data/`.

Files in this skill folder are optional portable mirrors. Treat them as valid only when all four filenames, sizes, and hashes match the vault source. **Sheet and column names inside each workbook are unchanged**; only mirror filenames are normalized to snake_case for stable paths across projects.

## Vendor export → skill filename

| Vault / vendor name (export drop zone) | Skill `raw-data/` name |
|----------------------------------------|-------------------------|
| `CMHI_DATA.xlsx` | `cmhi_data.xlsx` |
| `MonthlyData (4).xlsx` | `monthly_data_4.xlsx` |
| `OPTIMUM_DATA.xlsx` | `optimum_data.xlsx` |
| `WeeklyData (2).xlsx` | `weekly_data_2.xlsx` |

## Expected mirror bundle

| File | Size (bytes) |
|------|----------------|
| `cmhi_data.xlsx` | 748,748 |
| `monthly_data_4.xlsx` | 2,732,143 |
| `optimum_data.xlsx` | 2,460,363 |
| `weekly_data_2.xlsx` | 7,956,225 |

**Last refreshed:** 2026-04-22 (sync from vault `Coding Projects/Recession Alert/Raw Data/`).

## Refresh rules (mandatory)

1. **Atomic update:** Copy **all four** files from the same vendor export batch in `Coding Projects/Recession Alert/Raw Data/`. Do not refresh a subset (avoids mixed vintages in merges).
2. **Rename** to the skill names above when copying into this folder.
3. **Do not** add `Backup of WeeklyData (2).xlk` or other backup formats here.
4. After copying, verify hashes and sizes against the vault source, then update **Last refreshed** and the size table if file sizes changed.
5. **Licensing:** Do not publish this folder to a public repository unless your subscription terms allow redistribution.

## Git / Git LFS

The skill root may include `.gitattributes` so `raw-data/*.xlsx` uses **Git LFS**. Before committing binaries, install [Git LFS](https://git-lfs.com/) and run `git lfs install`. If you intentionally keep LFS out of this repo, remove or edit that `.gitattributes` rule so plain Git stores the files (expect large packfiles).

## Human export source

Default drop zone (vendor filenames required for vault workflows):  
`Coding Projects/Recession Alert/Raw Data/` relative to the Obsidian vault root.

Reference implementation in the vault (`spx_timing_strategy.py`) should validate and load from the vault drop zone by default. Agents using **this skill** should only use this mirror outside the vault or after an explicit mirror-sync/divergence check.
