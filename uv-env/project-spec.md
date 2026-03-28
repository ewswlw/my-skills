<project_specification>
  <project_name>UV Environment from Canonical Dependency List</project_name>
  <overview>This skill bootstraps a fresh UV-managed Python environment from a canonical, embedded dependency list derived from the Bond-RV-App project. It requires no source file path — all package names and version constraints are baked directly into the skill. The skill targets quant/finance development environments requiring Bloomberg blpapi (custom index), xbbg, and a 30+ package scientific stack. Success is measured by a completed uv sync, passing blpapi and xbbg import tests, and a printed version table. A second mode — env health check — detects drift between any existing environment and the canonical list.</overview>
  <technology_stack>UV (latest installed), CPython >=3.11 &lt;3.15, Hatchling build backend, Bloomberg package index for blpapi, PyPI for all other packages.</technology_stack>
  <assumptions>
    <item>UV is installed and on PATH on the target machine.</item>
    <item>The user will confirm the target directory and project name before any files are written.</item>
    <item>blpapi wheel availability requires Bloomberg network access; the skill documents a manual fallback.</item>
    <item>SyntaxWarning emitted by blpapi on Python 3.13 is a known Bloomberg upstream issue and does not indicate a broken install.</item>
    <item>The canonical dependency list embedded in the skill reflects the Bond-RV-App pyproject.toml at time of skill creation and may need manual updates when new packages are added to the source project.</item>
  </assumptions>
  <out_of_scope>
    <item>Reading or watching the source pyproject.toml file at runtime.</item>
    <item>Provisioning Bloomberg Terminal, API credentials, or corporate network access.</item>
    <item>Migrating application source code — dependency/env replication only.</item>
    <item>Conda, pipenv, or any non-UV workflow.</item>
    <item>Pinning exact patch versions beyond what the embedded constraints specify.</item>
  </out_of_scope>
  <core_features>
    <feature name="Setup Mode">As a developer on a new machine or in a new folder, I want to run one skill invocation and get a fully working UV environment with all canonical packages installed, so I can start writing Python immediately without manual pip commands.</feature>
    <feature name="Bloomberg Index Wiring">As a quant developer, I want blpapi resolved from the Bloomberg package index automatically, without manually passing --index-url flags, so I never hit a 404 from PyPI.</feature>
    <feature name="Flat Target Layout">As a user, I want pyproject.toml at the root of my chosen directory — no extra nested wrapper folder — so the project structure stays clean.</feature>
    <feature name="Update Mode">As a developer whose canonical list has changed, I want the skill to diff my existing environment's pyproject.toml against the embedded list and offer a targeted update, so I never silently lose user-added packages.</feature>
    <feature name="Health Check Mode">As a developer with an existing environment, I want to run a drift check that compares installed package versions against the canonical list and prints a status table, so I can spot and fix gaps instantly.</feature>
    <feature name="Smoke Tests">As a developer, I want the skill to verify blpapi and xbbg import correctly after sync, with clear pass/fail output and a version table, so I know the environment is usable before I write any code.</feature>
  </core_features>
  <database_schema>
    <table name="N_A">No database — this is a tooling/environment skill.</table>
  </database_schema>
  <api_endpoints_summary>
    <endpoint>N/A — no HTTP API.</endpoint>
  </api_endpoints_summary>
  <implementation_steps>
    <phase n="1">Confirm target directory and project name — always ask; default project name = user-supplied name or generic placeholder; abort if user declines.</phase>
    <phase n="2">Check target for existing pyproject.toml — if found, enter Update Mode: diff [project].dependencies against embedded canonical list; show additions/removals; ask permission before writing; never touch user-added sections.</phase>
    <phase n="3">Check Python availability — run uv python list; if no >=3.11,&lt;3.15 interpreter found, warn and show: uv python install 3.13</phase>
    <phase n="4">Write pyproject.toml directly into target root — project name from user, canonical dependency list, requires-python, Bloomberg index blocks, hatchling build backend; strip all source-specific tool sections.</phase>
    <phase n="5">Create package stub — mkdir &lt;snake_name&gt; and write minimal __init__.py; keep main.py as scratch file.</phase>
    <phase n="6">Create .gitignore if absent — entries: .venv/, __pycache__/, *.pyc, uv.lock</phase>
    <phase n="7">Run uv sync from target root — if blpapi resolution fails, detect network error and print: pip install --index-url=https://blpapi.bloomberg.com/repository/releases/python/simple blpapi</phase>
    <phase n="8">Smoke-test blpapi and xbbg — uv run python -c; SyntaxWarning from Bloomberg = benign (pass if exit code 0); on failure print error and fix command then stop.</phase>
    <phase n="9">Print summary — version table (blpapi, xbbg, Python, UV), list of created files, usage reminder: uv run python script.py</phase>
    <phase n="10">Health Check Mode (secondary invocation) — run uv run python -c with importlib.metadata to get installed versions; compare against embedded canonical list; print Package / Required / Installed / Status table; flag missing or out-of-range entries with exact uv add fix command.</phase>
  </implementation_steps>
  <success_criteria>
    <functional>uv sync completes without error; uv run python -c "import blpapi, xbbg" exits 0; version table printed.</functional>
    <ux>All paths double-quoted in PowerShell commands; user confirms directory and name before any file is written; update mode shows a diff before overwriting.</ux>
    <technical>SKILL.md name field is uv-env-from-pyproject; no personal file paths in skill instructions; canonical dep list is the single source of truth inside the skill.</technical>
  </success_criteria>
</project_specification>
