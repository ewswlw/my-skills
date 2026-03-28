---
name: terminal
description: Force all code execution inline in the terminal with zero new files—no scripts, temp files, or Write/StrReplace outputs. Use when the user invokes /terminal, says "terminal only", "inline", "no files", "one-liner", "quick command", "run in shell", or wants Python/PowerShell/Node/Bash without creating .py/.ps1/.js on disk. Also use when speed and minimal artifact footprint matter more than a saved codebase. Includes when to parallelize with shell subagents vs stay single-threaded.
---

# Terminal-only execution (`/terminal`)

This skill **forces** solving the task by **running commands in the terminal** and **never creating, writing, or persisting any new file** (including temp scripts, `.py`, `.ps1`, `.sh`, `.js`, `.txt`, logs you create, or patched project files). Reading existing repo files is allowed when needed; **creating or modifying files via editor tools is forbidden** while this skill is active unless the user explicitly lifts the constraint (see [Escape hatch](#escape-hatch)).

Invoke explicitly with **`/terminal`** or match the triggers in the frontmatter `description`.

---

## Hard rules (non-negotiable)

1. **No file writes:** Do not use Write, StrReplace, or any tool that creates or overwrites files. Do not use MCP or other tools that persist output to disk.
2. **No shell redirection to files:** Do not `>` / `>>` / `tee` / `Tee-Object` / `Out-File` / `Set-Content` / `New-Item` (files) / `ni` to paths; do not `curl -o` / `Invoke-RestMethod -OutFile` / `Invoke-WebRequest -OutFile`. **Stdout/stderr to the terminal only.** (Reading existing files with `Get-Content` / `type` is fine.)
3. **No temp artifacts:** Do not create scratch files in `%TEMP%`, `/tmp`, or the workspace—even if you delete them after.
4. **Inline only:** Express logic as shell pipelines, one-liners, and stdin-fed programs (`python -c`, `node -e`, `powershell -Command`, `bash -c`, heredocs to **stdin** only).
5. **Prefer the smallest hammer:** Built-ins and binaries already on `PATH` > short `uv run python -c` > longer inline blocks.
6. **If it cannot be done inline:** Stop and use the [Escape hatch](#escape-hatch)—do not silently create a file.

---

## Execution patterns

### PowerShell (Windows default)

```powershell
powershell -NoProfile -Command "& { Get-Date; $PSVersionTable.PSVersion }"
```

- **Pipelines:** `Get-ChildItem | Where-Object { $_.Length -gt 1mb }`
- **Scriptblocks:** `& { ... }` for multi-statement; use `;` between statements.
- **Quotes:** Prefer **single-quoted** `-Command` strings when no expansion is needed; double-quote when you need `$variables` (escape nested `"` as `` `\"` `` or use single-quoted here-strings for large blobs).

### Python (UV — match project rules when in this vault)

```powershell
uv run python -c "import sys; print(sys.version)"
```

- **Multiline in one `-c`:** Use `exec()` with a triple-**double**-quoted Python string so dicts can use `'a'` without clashing with shell quoting:

```powershell
uv run python -c "exec(\"\"\"import json\nprint(json.dumps({'a': 1}))\n\"\"\")"
```

- **Stdin (bash / Git Bash / WSL):** pipe or heredoc **to stdin** (no file on disk):

```bash
echo '{"x":1}' | uv run python -c "import sys,json; print(json.load(sys.stdin))"
```

### Node.js

```powershell
node -e "console.log(JSON.stringify({ok:true}))"
```

### Bash (Git Bash, WSL, or Unix)

```bash
bash -c 'echo hello | wc -c'
```

---

## Multiline strategies (still zero files)

| Approach | When to use |
|----------|-------------|
| **`exec('''...''')` in `python -c`** | Longer Python without a `.py` file; mind quoting for your shell. |
| **PowerShell `& { ... }`** | Multiple statements; keep under ~8K for sanity. |
| **Pipe previous command output** | Split into two runs: first prints JSON/lines, second consumes stdin. |
| **Heredoc to stdin** (bash/WSL) | `uv run python - <<'PY'\n...\nPY` — data flows on stdin, **no file write**. |
| **Pipe to `python -` (PowerShell)** | Multiline script with normal Python quotes — see [this section](#powershell--python-quoting-and-stdin). |
| **Avoid** | Saving to `%TEMP%\x.py` — violates this skill. |

---

## Subagents: when they help vs hurt

In **Cursor**, parallel terminal work maps to the **Task** tool with `subagent_type: "shell"` (or `generalPurpose` with explicit “terminal only, zero files” instructions)—**only when** the criteria below are met. Same rules apply inside the subagent: **no file writes.**

### Use subagents when

- **3+ independent terminal tasks** can run **in parallel** (e.g., three different `curl`/`Invoke-RestMethod` calls to unrelated endpoints, three separate metric checks).
- **Exploratory probing** might burn many retries (e.g., fuzzing CLI flags)—isolate so the main thread keeps a clean summary.
- **Phases are independent** after a fixed handoff: e.g., "fetch three JSON blobs in parallel" then you merge results in one follow-up command yourself.

### Do not use subagents when

- **Sequential dependency:** step B needs stdout/stderr or exit code from step A in the same shell session.
- **One or two commands** or a **short pipe**—overhead dominates.
- **Shared mutable cwd/env** where ordering matters and parallel runs would race.

### Good split (example)

- Agent A: `uv run python -c "..."` to compute checksum of pasted data.
- Agent B: `powershell -Command "Invoke-RestMethod ..."` to hit an API.
- **Merge in main:** single `python -c` combining both outputs you paste or pipe.

### Bad split

- Agent A runs `cd repo && git status` and Agent B runs `git diff` assuming cwd—**race / wrong cwd**. Run **one** shell session or chain with `&&`.

**PowerShell version note:** `&&` chains two commands only in **PowerShell 7+**. On **Windows PowerShell 5.1** (still common), use `;` instead (`cd repo; git status`) or separate invocations—otherwise the command fails to parse.

---

## PowerShell + Python (quoting and stdin)

`uv run python -c "..."` often **breaks on Windows** when the Python code contains **many double-quoted strings**: Cursor, PowerShell, and/or `uv` can **drop or alter quotes**, producing `SyntaxError` (e.g. `blp.bdh(CA0BNM` with no string quotes).

**Prefer (zero files, multiline OK):** pipe a script into **`python -`** (read program from stdin):

```powershell
cd "C:\path\to\project"
$env:MY_TICKER = 'CA0BNM DEC2026 Index'   # optional: avoid quoting tickers/paths in -c
@'
import os
from xbbg import blp
t = os.environ["MY_TICKER"]
print(t)
'@ | uv run python -
```

- Use a **single-quoted** here-string (`@' ... '@`) so PowerShell does **not** expand `$()` inside the Python code.
- For values with spaces, **`$env:VAR = '...'`** + `os.environ['VAR']` in Python is more reliable than embedding those strings inside `-c`.

**Fallback for short one-liners:** keep `python -c` but pass awkward strings via **environment variables** (same pattern as above) instead of inline quotes.

---

## Cookbook (copy-paste shapes)

**JSON from stdin (Python):**

```powershell
$json = '{"a":1}'; $json | uv run python -c "import sys,json; print(json.load(sys.stdin)['a'])"
```

**HTTP GET (PowerShell 5+):**

```powershell
powershell -NoProfile -Command "(Invoke-RestMethod -Uri 'https://httpbin.org/get').headers"
```

**HTTP to stdout only (no `-o` file):** `curl.exe -sS "https://httpbin.org/get"` — do not add `-o` / `--output`.

**Read-only file peek (existing files only):**

```powershell
Get-Content -Path '.\README.md' -TotalCount 20
```

**Git (read-only queries):**

```powershell
git log -1 --oneline
git status --short
```

**Env / path sanity:**

```powershell
where.exe uv
uv run python -c "import sys; print(sys.executable)"
```

---

## Escape hatch

If the task **requires** a persistent file (e.g., multi-module package, IDE integration, user asked for a saved script, or logic is too large to maintain inline), or **mutates the repo** in ways that are not one-off terminal output (e.g., `git commit`, `git checkout`, installs that write lockfiles you were not asked to touch):

1. **Say explicitly** that `/terminal` cannot complete it without files.
2. **Ask** whether to lift the no-file constraint or narrow the task to an inline subset.
3. **Never** create files without that confirmation.

---

## Agent checklist before running commands

- [ ] Am I about to create or overwrite **any** file? If yes → stop or escape hatch.
- [ ] Is this one pipeline or sequential `&&` in **one** invocation?
- [ ] For parallel work, are subtasks **actually independent**?
- [ ] Did I state **which shell** and **quoting** pitfalls for Windows?
- [ ] If `python -c` fails with mangled strings, switch to **`env` + `python -`** (stdin) or **`;`** instead of **`&&`** on PS 5.1.

---

## Windows / Cursor notes

- **Paths with spaces:** quote arguments: `cd "C:\Users\Eddy\Documents\Obsidian Vault"`.
- **UV:** In vault projects use `uv run python -c "..."` from the project root when `pyproject.toml` matters; otherwise `uv run` still resolves if UV is configured globally.
- **Long commands:** Prefer splitting into two terminal invocations with **handoff via clipboard/paste** or **stdin pipe** rather than a temp file.
- **Complex Python (Plotly, APIs, Bloomberg tickers):** prefer **`@' ... '@ | uv run python -`** over long `-c` strings — see [PowerShell + Python (quoting and stdin)](#powershell--python-quoting-and-stdin) above.
