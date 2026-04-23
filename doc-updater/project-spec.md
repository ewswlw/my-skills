<project_specification>
  <project_name>doc-updater (global Agent Skill)</project_name>
  <overview>doc-updater is a portable, invocation-only workflow that deep-inspects a repository, compares reality to written documentation and Cursor rules, produces a change manifest and optional documentation health score, and applies updates only after mandatory dry-run approval. It exists so the same rigor as a project-local `/update-docs` command can be reused in any repo without hardcoded paths. Success is measured by: (1) no silent writes, (2) rules and docs matching discovered structure and public APIs, (3) safe handling of large repos, mixed languages, and missing data files, and (4) a repeatable run log for incremental updates.</overview>
  <technology_stack>Markdown skills; host tools: `git`, parallel read/grep/shell, optional `uv run python` or `python` for pyarrow/pandas when parquet files exist. Task subagent `explore` when available. No new dependencies in the user repo.</technology_stack>
  <assumptions>
    <item>The host environment allows shell, file read/write within the opened workspace, and `git` where the repo is a git checkout.</item>
    <item>Documentation lives under `documentation/` or `docs/`; if both exist, prefer `documentation/` and note the other in the manifest.</item>
    <item>Parquet schema reads require Python with pyarrow/pandas; if missing, data phase is skipped with an explicit note.</item>
    <item>“Module” and API extraction adapts: Python AST when `.py` is primary; TypeScript/JavaScript surface scan when `package.json` exists and no Python; else tree + file inventory only.</item>
  </assumptions>
  <out_of_scope>
    <item>Editing source code to “fix” behavior or to match documentation.</item>
    <item>Automatic `git commit`, CI deployment, or publishing docs to the web.</item>
    <item>Guaranteed running time on pathological monorepos without user scoping (pre-flight is required instead).</item>
  </out_of_scope>
  <core_features>
    <feature name="Pre-flight and scope">Before heavy work: count git-tracked files and parquet files; if over thresholds (8,000 files or 50 parquets), pause for user direction. Optional inline `scope: dir,dir` limits enumeration. Parquet full reads capped at 30 per run with explicit deferral list.</feature>
    <feature name="Timestamp and mode">Obtain `CURRENT_TIMESTAMP` from shell. Set INCREMENTAL if `{doc_root}/update_log.md` contains `## Run:`; else FULL. INCREMENTAL uses the latest run timestamp to scope `git log` and changed-file focus.</feature>
    <feature name="Four-track inspection">Parallel tracks: (1) directory tree from `git ls-files`, (2) language-appropriate module/API extraction, (3) data file metadata for tracked `*.parquet` within cap, (4) git history/status. If Task `explore` is unavailable, run the same four tracks with parallel tools.</feature>
    <feature name="Change manifest">Categories: NEW_FILES, REMOVED_FILES, RENAMED_FILES, SCHEMA_DIFFS, SIGNATURE_CHANGES, STALE_TIMESTAMPS, MISSING_DOCS. Respect [PLANNED]/[FUTURE]/[PROPOSED] — skip destructive classifications and add Manual Review. User must confirm after manifest before drafting bulk edits.</feature>
    <feature name="Draft updates (memory only)">Update `.mdc` rules to match tree and APIs; update markdown docs; regenerate `{doc}/README.md` index if that file exists; update root `CHANGELOG.md` in existing style if present. Missing parquet: never delete doc schemas. New docs from template only after approval. Optional compact approval when &lt;8 files and no .mdc changes and user says compact.</feature>
    <feature name="Documentation health score">Reproducible weighted score: coverage, freshness, schema accuracy, changelog recency, path integrity — formulas use discovered modules/paths, not a fixed app layout.</feature>
    <feature name="Dry-run approval gate">Show summary, per-file actions, and inline before/after for key sections; separate block for rules; optional per-CHANGELOG entry acceptance; user options: all / docs-only / rules-only / selective / cancel. Then write, append `update_log.md`, offer `git add` only.</feature>
  </core_features>
  <database_schema>
    <table name="n/a_logic_files">The workflow does not use a database. The following are logical file roles: `documentation/update_log.md` or `docs/update_log.md` (run history with health score table rows); `CHANGELOG.md` (optional); `.cursor/rules/**/*.mdc` (Cursor rules); `project-spec.md` and `project-constitution.md` in target repo (read-only by default).</table>
  </database_schema>
  <api_endpoints_summary>
    <endpoint>n/a — no HTTP server; the skill is a procedural contract executed by the agent in the IDE.</endpoint>
  </api_endpoints_summary>
  <implementation_steps>
    <step order="1">Merge interview answers, risk mitigations, and this spec into a single source of truth (constitution + spec files in skill folder).</step>
    <step order="2">Author `project-constitution.md` with non-negotiable bounds and thresholds.</step>
    <step order="3">Author `project-spec.md` (this document) in the required XML structure.</step>
    <step order="4">Run structured quality review (recursive-style pass) on constitution for clarity and enforceability.</step>
    <step order="5">Run the same on project-spec for testability and absence of internal contradiction.</step>
    <step order="6">Write `SKILL.md` with invocation-only `description` YAML, pre-flight, language branching, compact approval, and pointer to `references/update-docs-protocol.md`.</step>
    <step order="7">Write `references/update-docs-protocol.md` generalizing the original project command: phases, agents, manifest, per-area update guidance, health score, dry-run, write, log, git offer.</step>
    <step order="8">Verify files on disk; end user gate: explicit permission before treating any *additional* implementation in a target repo (e.g. adding a thin wrapper command) as in scope.</step>
  </implementation_steps>
  <success_criteria>
    <functional>Invoking the skill results in a manifest, optional score, and no writes without approval; rules approval is separate; incremental mode works when `update_log.md` has prior runs.</functional>
    <ux>Confidentiality and size warnings appear when appropriate; user can pass `scope:` and `compact approval`; unclear invocation triggers a single clarifying question.</ux>
    <technical>No Bond-RV-App hardcoded paths; Python/TS/no-code paths behave as specified; missing parquet and missing CHANGELOG are handled without failure.</technical>
  </success_criteria>
</project_specification>
