<project_specification>
  <project_name>Recession-alert skill: bundled Raw Data</project_name>
  <overview>This project makes the RecessionALERT Raw Data Excel exports portable by bundling them inside the `recession-alert` agent skill (`~/.claude/skills/recession-alert`), using stable snake_case filenames under `raw-data/`, with a README mapping vendor names to skill names and strict “replace all four together” refresh rules. Success is measured by: (1) all four workbooks present and named per the constitution, (2) skill documentation consistently references the skill-local paths and filenames, (3) the vault remains the export source without requiring code changes there in this scope, and (4) redistribution risk is documented conservatively.</overview>
  <technology_stack>Markdown documentation; Excel .xlsx binaries; Git with optional Git LFS for `raw-data/*.xlsx`. No application runtime is part of this bundle.</technology_stack>
  <assumptions>
    <item>The user may legally retain copies of the exports locally; public redistribution may be restricted—constitution treats public publish of `raw-data/` as disallowed unless explicitly permitted.</item>
    <item>Vendor sheet and column names inside the workbooks are unchanged from current RecessionALERT exports; only **filesystem names** of the four files are normalized in the skill.</item>
    <item>Canonical skill install path is `C:\Users\Eddy\.claude\skills\recession-alert` (user home may differ on other machines).</item>
    <item>Exports are refreshed by copying from `Coding Projects/Recession Alert/Raw Data/` in the Obsidian vault (vendor filenames) into the skill after renames per the mapping table.</item>
  </assumptions>
  <out_of_scope>
    <item>Changing vault Python loaders (`spx_timing_strategy.py`, etc.) to default to skill paths.</item>
    <item>Including `Backup of WeeklyData (2).xlk` or other backup formats in `raw-data/`.</item>
    <item>Automated sync scripts (optional future enhancement); refresh is manual per README.</item>
    <item>Duplicate skill installs under vault `.cursor/skills/`.</item>
    <item>Optional future: small verify script that checks presence and size of the four files (no new dependencies).</item>
  </out_of_scope>
  <core_features>
    <feature name="Bundled raw workbooks">As an implementer, I have the four authoritative Excel files under `raw-data/` with names `cmhi_data.xlsx`, `monthly_data_4.xlsx`, `optimum_data.xlsx`, `weekly_data_2.xlsx` so agents can load data without the vault tree. Acceptance: all four files exist; byte content matches the current vault exports (after rename only).</feature>
    <feature name="README mapping and refresh policy">As a maintainer, I can sync from vault exports without mixing filenames. Acceptance: `raw-data/README.md` lists vendor↔skill filename mapping, approximate sizes, last-refreshed field, atomic four-file rule, and manual copy/rename steps.</feature>
    <feature name="Documentation alignment">As an agent, I read `SKILL.md` and `references/*.md` and see skill-local `raw-data/` as the primary Raw Data location, with vault path documented as the human export source. Acceptance: no stale references that imply only vault paths or old vendor filenames as the skill-local canonical names.</feature>
    <feature name="Git packaging">As a maintainer, I can commit binaries without breaking remotes. Acceptance: `.gitattributes` documents LFS for `raw-data/*.xlsx` when needed; README or constitution notes noisy binary diffs on refresh.</feature>
  </core_features>
  <database_schema>
    <table name="raw_data_manifest">Not a database; `raw-data/README.md` is the human manifest (file list, mapping, last refreshed).</table>
  </database_schema>
  <api_endpoints_summary>
    <endpoint>N/A — no HTTP API.</endpoint>
  </api_endpoints_summary>
  <implementation_steps>
    <step order="1" title="Confirm naming contract">Lock the four snake_case filenames in constitution and README mapping; dependency: none.</step>
    <step order="2" title="Create raw-data tree">Add `raw-data/` with the four `.xlsx` files (copy from vault, rename only); dependency: step 1.</step>
    <step order="3" title="Write raw-data README">Author mapping table, atomic refresh rule, LFS/redistribution caution, manual sync instructions; dependency: step 2.</step>
    <step order="4" title="Update SKILL.md">Primary paths = skill `raw-data/`; vault = export source; update Raw Data file list to snake_case names; dependency: step 1.</step>
    <step order="5" title="Update reference docs">Edit `references/data-dictionary.md`, `references/loaders-and-merge.md`, and grep-fix any other references to old filenames or vault-only Raw Data paths; dependency: steps 1–2.</step>
    <step order="6" title="Git attributes">Add or adjust `.gitattributes` for LFS on `raw-data/*.xlsx` if required by remote policy; dependency: step 2.</step>
    <step order="7" title="Consistency pass">Search skill folder for stale names/paths; align triggers in `SKILL.md` frontmatter if they still imply vault-only usage; dependency: steps 4–5.</step>
    <step order="8" title="Scorecard archive">Retain recursive-refine scorecard in project history or chat for audit; dependency: spec complete.</step>
  </implementation_steps>
  <success_criteria>
    <functional>Four workbooks exist under `raw-data/` with constitutional names; README mapping and atomic refresh rule are present; docs describe skill-local loading as primary.</functional>
    <ux>Maintainers can refresh all four files in one session using README without guessing filenames.</ux>
    <technical>No contradictory filenames between constitution, README, SKILL.md, and references; public publish of `raw-data/` is explicitly discouraged pending license check.</technical>
  </success_criteria>
</project_specification>
