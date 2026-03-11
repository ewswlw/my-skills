---
name: marimo-notebook
description: "Create, run, debug, and deploy interactive marimo notebooks. Use when the user mentions 'notebook', 'marimo', 'reactive Python app', 'data app', or 'interactive dashboard'. Supports edit/run modes, dependency management, and multiple export options."
---

# Marimo Notebook Workflow

This skill provides a comprehensive workflow for developing, debugging, and deploying interactive web applications using [marimo](https://marimo.io/).

Your primary goal is to act as a backend developer. The user will interact with the notebook in their browser via a public URL that you provide. You will edit the underlying `.py` source file to make changes, fix bugs, or add features. The notebook will auto-reload in the user's browser.

## Core Workflow

Follow these sequential steps for every marimo notebook project.

1.  **Setup & Scaffolding**: Initialize the project directory and create a boilerplate notebook from the template.
2.  **Install Dependencies**: Check if `marimo` is installed and install it if needed.
3.  **Launch Server**: Run the marimo server with the correct flags for the sandbox environment.
4.  **Access the Notebook**: Server runs locally — open http://localhost:8080 in the browser.
5.  **Iterate**: Wait for user feedback, edit the `.py` file, and let the server auto-reload.
6.  **Shutdown**: When the task is complete, stop the marimo server process.

---

## 1. Setup & Scaffolding

Always start by creating a dedicated directory for the notebook.

```powershell
New-Item -ItemType Directory -Path "my-marimo-app" -Force
```

Next, create the main notebook file from the provided template.

```powershell
Copy-Item "C:\Users\Eddy\.claude\skills\marimo-notebook\templates\basic_notebook.py" -Destination "my-marimo-app\app.py"
```

---

## 2. Install Dependencies

First, check if `marimo` is already installed.

```bash
marimo --version
```

If the command fails or shows an old version, install/update it and any other required libraries.

```bash
uv add marimo pandas plotly
```

---

## 3. Launch Server

Run the marimo server. This is a long-running process — background it immediately (set `block_until_ms: 0`).

```bash
marimo edit my-marimo-app\app.py --host 127.0.0.1 --port 8080 --no-token --watch
```

| Flag | Purpose |
|---|---|
| `--host 127.0.0.1` | Bind to localhost (no need to expose externally in Cursor) |
| `--port 8080` | Use a standard port for the web service |
| `--no-token` | Disable auth token for easy local access (dev only) |
| `--watch` | Live-reload when the `.py` file changes on disk |

---

## 4. Access the Notebook

After the server is running, the notebook is accessible locally in the user's browser.

Tell the user:

> "Your marimo notebook is running at **http://localhost:8080** — open that URL in your browser to interact with it."

No port exposure needed in Cursor — the server runs directly on the local machine.

---

## 5. Iterate

Once the user has the URL, they will provide feedback. Your job is to:

1.  **Receive feedback** from the user (e.g., "change the chart title", "add a new slider").
2.  **Edit the code** in `my-marimo-app\app.py` to implement the changes.
3.  **Save the file**. The `--watch` flag will automatically reload the notebook in the user's browser.
4.  **Inform the user** that the change is live and ask for more feedback.
5.  **Repeat** this loop until the user is satisfied.

---

## 6. Shutdown

When the task is complete, you **MUST** stop the marimo server to free up resources.

```powershell
# Find and stop the process using port 8080
$conn = Get-NetTCPConnection -LocalPort 8080 -ErrorAction SilentlyContinue
if ($conn) {
    Stop-Process -Id $conn.OwningProcess -Force
    Write-Host "Marimo server on port 8080 stopped."
} else {
    Write-Host "No Marimo server found on port 8080."
}
```

---

## Quick Debugging

If the notebook has errors, check these common issues before consulting the full debugging guide.

| Error | Cause | Fix |
|---|---|---|
| `MultipleDefinitionError` | Same variable defined in 2+ cells | Consolidate definitions into one cell or use `_` prefix for local scope. |
| `CycleError` | Circular dependency (A -> B -> A) | Merge the cells or introduce an intermediate cell to break the cycle. |
| `NameError` | Variable used before definition | Ensure the upstream cell returns the variable and the downstream cell accepts it as an argument. |
| Port in use | Another process is on port 8080 | Run the shutdown command from Step 6 before re-launching. |

For a more detailed guide, read `references/debugging.md` in this skill's folder.

---

## Windows/Cursor Compatibility Notes

- Setup commands changed: `mkdir -p` → `New-Item -ItemType Directory -Force`; `cp` → `Copy-Item`.
- Template path: `C:\Users\Eddy\.claude\skills\marimo-notebook\templates\basic_notebook.py`.
- Install command: `uv add` replaces `sudo uv pip install --system`.
- Server launch: `--host 0.0.0.0` changed to `--host 127.0.0.1` (local only; no sandbox needed).
- Expose tool removed: server runs locally at http://localhost:8080 — no public URL needed.
- Shutdown: PowerShell `Get-NetTCPConnection` + `Stop-Process` replaces `lsof` + `kill -9`.
- Debugging reference path changed to relative form.
