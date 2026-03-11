# Marimo CLI & Export Reference

Read this file when you need details on CLI commands, export formats, or deployment options.

## CLI Commands

| Command | Purpose |
|---------|---------|
| `marimo edit app.py` | Open notebook in editor mode (code + outputs) |
| `marimo run app.py` | Open notebook in app mode (outputs only, code hidden) |
| `marimo check --fix app.py` | Validate and auto-fix formatting issues |
| `marimo check --strict app.py` | Strict validation (catches more issues) |
| `marimo edit --sandbox app.py` | Run with sandboxed dependencies via PEP 723 metadata |
| `marimo export html app.py > out.html` | Export static HTML |
| `marimo export html-wasm app.py -o dir --mode run` | Export interactive WASM (read-only) |
| `marimo export html-wasm app.py -o dir --mode edit` | Export interactive WASM (editable) |

## Server Flags

| Flag | Purpose |
|------|---------|
| `--host 127.0.0.1` | Local access only (default, safe) |
| `--host 0.0.0.0` | Bind all interfaces (required for remote/WSL access) |
| `--port 8080` | Set port number |
| `--headless` | Don't auto-open browser |
| `--no-token` | Disable auth token (local dev only — don't use on public networks) |
| `--watch` | Live-reload when the `.py` file changes on disk |
| `--sandbox` | Auto-install PEP 723 deps in isolated env via `uv` |

### Typical local development command

```powershell
marimo edit app.py --watch
```

### Typical headless / remote command

```powershell
marimo edit app.py --host 0.0.0.0 --port 8080 --headless --no-token --watch
```

## PEP 723 Inline Dependencies (Sandbox Mode)

Add this header to the top of a notebook `.py` file to declare dependencies. When `--sandbox` is used, `uv` will automatically create an isolated environment and install them.

```python
# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "pandas>=2.0",
#   "plotly>=5.0",
#   "scikit-learn",
# ]
# ///
```

## Programmatic Execution

Run a notebook or individual cells from Python without the server:

```python
from my_notebook import app
# Run entire app, optionally override definitions
outputs, defs = app.run(defs={"batch_size": 64})
```

```python
from my_notebook import my_cell
output, definitions = my_cell.run()
```

## Multiple Notebooks on Different Ports

Run multiple notebooks simultaneously on different ports:

```powershell
# Terminal 1
marimo edit app1.py --port 8080 --watch

# Terminal 2
marimo edit app2.py --port 8081 --watch
```

## Export Options

### Static HTML

Non-interactive snapshot. Good for reports and archiving.

```powershell
marimo export html app.py > report.html
```

### Interactive WASM

Self-contained HTML that runs marimo in the browser via WebAssembly. Best for sharing interactive notebooks without requiring a server.

```powershell
# Read-only (app mode)
marimo export html-wasm app.py -o output-dir --mode run

# Editable (editor mode)
marimo export html-wasm app.py -o output-dir --mode edit
```

### Markdown

Export notebook cells as markdown (useful for documentation):

```powershell
marimo export md app.py > notebook.md
```

### Script

Export as a plain Python script (strips marimo cell structure):

```powershell
marimo export script app.py > script.py
```
