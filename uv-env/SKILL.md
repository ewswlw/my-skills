---
name: uv-env
description: Bootstrap a new UV Python environment from a canonical embedded dependency list (blpapi via Bloomberg index, xbbg, pandas, numpy, vectorbt, scikit-learn, scipy, statsmodels, xgboost, lightgbm, plotly, openpyxl, and 25+ others). Use when the user asks to set up a UV env, mirror python dependencies, create a new UV project, replicate a python env, bootstrap UV from pyproject, copy uv dependencies, check my UV env, or env health check. Two modes: Setup (creates env) and Health Check (detects version drift). Handles Windows paths with spaces, Bloomberg network errors, and Python version mismatches.
---

# UV Environment from Canonical Dependency List

Bootstraps a fresh UV Python environment from the canonical dependency list embedded below. No source file path needed — all packages and version constraints are baked in.

## Two Modes

- **Setup Mode** — triggered by: "set up a UV env", "new UV environment", "mirror pyproject", "replicate python env", "bootstrap UV from pyproject", "copy uv dependencies"
- **Health Check Mode** — triggered by: "check my UV env", "env health check", "check installed packages"

---

## Canonical Dependency List

This is the single source of truth. Never read from an external file at runtime.

### Runtime Dependencies

```toml
dependencies = [
    "blpapi",
    "empyrical-reloaded>=0.5.12",
    "hmmlearn>=0.3.3",
    "marimo>=0.19.10",
    "markitdown[pdf]>=0.1.5",
    "notebooklm-py[browser]",
    "nbconvert[webpdf]",
    "openpyxl>=3.1.0",
    "pandas>=2.0.0",
    "pandoc>=2.4,<3.0",
    "plotly>=5.0.0,<6.0",
    "pyarrow>=12.0.0",
    "pypandoc>=1.16,<2.0",
    "pyyaml>=6.0.0",
    "quantstats>=0.0.81",
    "scikit-learn>=1.8.0",
    "scipy>=1.17.0",
    "shap>=0.49.1",
    "statsmodels>=0.14.6",
    "ta>=0.11.0",
    "tabulate>=0.9.0",
    "xbbg>=0.8.2,<0.9.0",
    "xgboost>=3.2.0",
    "yt-dlp>=2024.0.0",
    "vectorbt>=0.28.4",
    "python-pptx>=1.0.2",
    "beautifulsoup4>=4.14.3",
    "notebooklm-mcp-cli>=0.4.6",
    "pypdf>=6.8.0",
    "playwright>=1.57.0",
    "lightgbm>=4.6.0",
    "numpy>=2.4.1",
]
```

### Dev Optional Dependencies

```toml
[project.optional-dependencies]
dev = [
    "ipykernel>=7.1.0,<8.0",
    "jupyter>=1.1.1,<2.0",
    "jupyterlab>=4.4.10,<5.0",
    "matplotlib>=3.7.0",
    "nbconvert>=7.16.6,<8.0",
    "notebook>=7.4.7,<8.0",
    "playwright>=1.56.0,<2.0",
    "pytest>=7.0.0",
    "pytest-cov>=4.0.0",
    "pytest-mock>=3.10.0",
]
```

### Python Version & Bloomberg Index

```toml
requires-python = ">=3.11,<3.15"

[tool.uv.sources]
blpapi = { index = "bloomberg" }

[[tool.uv.index]]
name = "bloomberg"
url = "https://blpapi.bloomberg.com/repository/releases/python/simple"
default = false

[[tool.uv.index]]
name = "pypi"
url = "https://pypi.org/simple"
default = true
```

---

## Setup Mode — Step by Step

### Step 1 — Confirm target directory and project name

Ask the user:
> "Where should the environment be created? (e.g. `C:\Users\Eddy\desktop code`)"
> "What should the project be named? Default: `my-project`"

**Always wait for confirmation before writing any files.**  
Always double-quote paths in PowerShell commands — paths may contain spaces.

Once confirmed, set these variables for use in all subsequent steps:

```powershell
$targetDir  = "C:\path\to\target"          # replace with user's answer
$projectName = "my-project"                 # replace with user's answer
$snakeName   = $projectName.ToLower() -replace '-','_' -replace ' ','_'
# e.g. "my-project" -> "my_project", "Desktop Code" -> "desktop_code"
```

### Step 2 — Check for existing pyproject.toml (Update Mode)

```powershell
Test-Path "<TARGET_DIR>\pyproject.toml"
```

If found, enter **Update Mode**:
1. Read the existing `[project].dependencies` list
2. Diff against the canonical list above — show what would be added and removed
3. Ask: "These changes will be applied to `[project].dependencies` only. Proceed?"
4. Never touch user-added sections (e.g. `[tool.pytest.ini_options]`, custom scripts)
5. If approved, overwrite only the `dependencies` list, then re-run `uv sync`

### Step 3 — Check Python availability

```powershell
uv python list
```

If no `>=3.11,<3.15` interpreter is found, warn:
> "No compatible Python found. Install one with: `uv python install 3.13`"

Stop here until the user has a compatible Python.

### Step 4 — Write pyproject.toml

Write directly into `<TARGET_DIR>\pyproject.toml`. Do **not** run `uv init` — it would overwrite existing files.

Use the `$projectName` and `$snakeName` variables from Step 1 to fill `<project-name>` and `<snake_name>` below. Write the complete file — do not omit any dependency.

```toml
[project]
name = "<project-name>"
version = "0.1.0"
description = "UV environment — canonical dependency set"
requires-python = ">=3.11,<3.15"
dependencies = [
    "blpapi",
    "empyrical-reloaded>=0.5.12",
    "hmmlearn>=0.3.3",
    "marimo>=0.19.10",
    "markitdown[pdf]>=0.1.5",
    "notebooklm-py[browser]",
    "nbconvert[webpdf]",
    "openpyxl>=3.1.0",
    "pandas>=2.0.0",
    "pandoc>=2.4,<3.0",
    "plotly>=5.0.0,<6.0",
    "pyarrow>=12.0.0",
    "pypandoc>=1.16,<2.0",
    "pyyaml>=6.0.0",
    "quantstats>=0.0.81",
    "scikit-learn>=1.8.0",
    "scipy>=1.17.0",
    "shap>=0.49.1",
    "statsmodels>=0.14.6",
    "ta>=0.11.0",
    "tabulate>=0.9.0",
    "xbbg>=0.8.2,<0.9.0",
    "xgboost>=3.2.0",
    "yt-dlp>=2024.0.0",
    "vectorbt>=0.28.4",
    "python-pptx>=1.0.2",
    "beautifulsoup4>=4.14.3",
    "notebooklm-mcp-cli>=0.4.6",
    "pypdf>=6.8.0",
    "playwright>=1.57.0",
    "lightgbm>=4.6.0",
    "numpy>=2.4.1",
]

[project.optional-dependencies]
dev = [
    "ipykernel>=7.1.0,<8.0",
    "jupyter>=1.1.1,<2.0",
    "jupyterlab>=4.4.10,<5.0",
    "matplotlib>=3.7.0",
    "nbconvert>=7.16.6,<8.0",
    "notebook>=7.4.7,<8.0",
    "playwright>=1.56.0,<2.0",
    "pytest>=7.0.0",
    "pytest-cov>=4.0.0",
    "pytest-mock>=3.10.0",
]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.hatch.build.targets.wheel]
packages = ["<snake_name>"]

[tool.uv.sources]
blpapi = { index = "bloomberg" }

[[tool.uv.index]]
name = "bloomberg"
url = "https://blpapi.bloomberg.com/repository/releases/python/simple"
default = false

[[tool.uv.index]]
name = "pypi"
url = "https://pypi.org/simple"
default = true
```

### Step 5 — Create package stub and scratch file

```powershell
New-Item -ItemType Directory -Path "<TARGET_DIR>\<snake_name>" -Force | Out-Null
Set-Content -Path "<TARGET_DIR>\<snake_name>\__init__.py" -Value '"""<project-name> package."""'
if (-not (Test-Path "<TARGET_DIR>\main.py")) {
    Set-Content -Path "<TARGET_DIR>\main.py" -Value "# Entry-point scratch file`nprint('Hello from <project-name>')"
}
```

### Step 6 — Create .gitignore if absent

```powershell
if (-not (Test-Path "<TARGET_DIR>\.gitignore")) {
    Set-Content -Path "<TARGET_DIR>\.gitignore" -Value ".venv/`n__pycache__/`n*.pyc`nuv.lock"
}
```

### Step 7 — Run uv sync

```powershell
cd "<TARGET_DIR>"
uv sync
```

**If blpapi fails to resolve** (403 or connection error from Bloomberg index):
> "blpapi could not be fetched from the Bloomberg index. This usually means you are not on a Bloomberg-enabled network. Manual fallback:"
> ```powershell
> cd "<TARGET_DIR>"
> uv pip install --index-url=https://blpapi.bloomberg.com/repository/releases/python/simple blpapi
> ```
> Stop and wait for the user to resolve network access before continuing.

### Step 8 — Smoke tests

```powershell
uv run python -c "import blpapi; print('blpapi:', blpapi.__version__)"
uv run python -c "import xbbg; print('xbbg:', xbbg.__version__)"
```

**Interpreting results:**
- `SyntaxWarning: invalid escape sequence '\s'` from blpapi — **expected and benign** on Python 3.13. Treat as PASS if exit code is 0.
- Any `ModuleNotFoundError` or non-zero exit — print the exact error and this fix:
  ```
  uv add <package-name>
  uv sync
  ```
  Then stop. Do not continue to Step 9 until both tests pass.

### Step 9 — Print summary

Print a version table:

```
Package    Version
---------  ----------
blpapi     3.x.x
xbbg       0.8.x
Python     3.13.x
UV         0.x.x
```

Followed by:
```
Files created:
  <TARGET_DIR>\pyproject.toml
  <TARGET_DIR>\<snake_name>\__init__.py
  <TARGET_DIR>\main.py          (if new)
  <TARGET_DIR>\.gitignore       (if new)

Run your scripts with:
  cd "<TARGET_DIR>"
  uv run python main.py

NOTE: Only runtime dependencies were installed (uv sync).
To also install dev dependencies (jupyter, pytest, matplotlib):
  uv sync --all-extras
```

---

## Health Check Mode — Step by Step

Triggered by: "check my UV env", "env health check", "check installed packages"

### Step 1 — Confirm environment directory

Ask: "Which environment should I check? (provide the directory containing `pyproject.toml` and `.venv`)"

### Step 2 — Get installed versions

```powershell
cd "<TARGET_DIR>"
uv run python -c "
import importlib.metadata
try:
    from packaging.version import Version
    from packaging.specifiers import SpecifierSet
    has_packaging = True
except ImportError:
    has_packaging = False

canonical = {
    'blpapi':               '',
    'empyrical-reloaded':   '>=0.5.12',
    'hmmlearn':             '>=0.3.3',
    'marimo':               '>=0.19.10',
    'markitdown':           '>=0.1.5',
    'notebooklm-py':        '',
    'nbconvert':            '',
    'openpyxl':             '>=3.1.0',
    'pandas':               '>=2.0.0',
    'pandoc':               '>=2.4,<3.0',
    'plotly':               '>=5.0.0,<6.0',
    'pyarrow':              '>=12.0.0',
    'pypandoc':             '>=1.16,<2.0',
    'pyyaml':               '>=6.0.0',
    'quantstats':           '>=0.0.81',
    'scikit-learn':         '>=1.8.0',
    'scipy':                '>=1.17.0',
    'shap':                 '>=0.49.1',
    'statsmodels':          '>=0.14.6',
    'ta':                   '>=0.11.0',
    'tabulate':             '>=0.9.0',
    'xbbg':                 '>=0.8.2,<0.9.0',
    'xgboost':              '>=3.2.0',
    'yt-dlp':               '>=2024.0.0',
    'vectorbt':             '>=0.28.4',
    'python-pptx':          '>=1.0.2',
    'beautifulsoup4':       '>=4.14.3',
    'notebooklm-mcp-cli':   '>=0.4.6',
    'pypdf':                '>=6.8.0',
    'playwright':           '>=1.57.0',
    'lightgbm':             '>=4.6.0',
    'numpy':                '>=2.4.1',
}

print(f'{\"Package\":<28} {\"Required\":<20} {\"Installed\":<14} Status')
print('-'*75)
fails = []
for pkg, spec in canonical.items():
    try:
        installed = importlib.metadata.version(pkg)
        if spec and has_packaging:
            ok = Version(installed) in SpecifierSet(spec)
        else:
            ok = True  # no constraint or packaging unavailable
        status = 'OK' if ok else 'FAIL'
        if not ok:
            fails.append((pkg, spec))
    except importlib.metadata.PackageNotFoundError:
        installed = 'MISSING'
        status = 'FAIL'
        fails.append((pkg, spec))
    req_str = spec if spec else '(any)'
    print(f'{pkg:<28} {req_str:<20} {installed:<14} {status}')

if fails:
    print()
    print('Fix commands:')
    for pkg, spec in fails:
        print(f'  uv add \"{pkg}{spec}\"')
else:
    print()
    print('All packages present and within constraints.')
"
```

### Step 3 — Interpret results

- **OK** — package is installed and its version satisfies the canonical constraint (evaluated with semver-aware `packaging.version.Version`, not string comparison — `0.8.10` correctly satisfies `<0.9.0`)
- **FAIL / MISSING** — package absent or version does not satisfy constraint; run the printed `uv add` fix command
- If `packaging` is not installed, constraint evaluation is skipped and all present packages show OK — run `uv add packaging` to enable full checks

---

## Windows / PowerShell Notes

- Always double-quote directory paths: `cd "C:\path with spaces"`
- Use `Set-Content` not `echo` to write files
- Use `New-Item -Force` to create directories idempotently
- `uv run python -c "..."` — use double-quote outer, single-quote inner for the Python string
- If UV is not on PATH, find it at: `$env:USERPROFILE\.local\bin\uv.exe`
