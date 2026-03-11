# Marimo Debugging Reference

Read this file when a notebook has errors or cells are not executing. Follow the steps in order.

## Step 1: Static Validation

Run before launching the server or after editing the file.

```powershell
marimo check --fix app.py
```

This catches:
- Formatting issues (auto-fixed with `--fix`)
- Invalid cell structure
- Use `--strict` for stricter validation

## Step 2: Python Syntax Check

Parse the notebook to catch syntax errors without starting the server.

```powershell
python -c "import ast; ast.parse(open('app.py').read()); print('Syntax OK')"
```

For deeper import-level errors:

```powershell
cd path\to\project
python -c "import app; print('Import OK')"
```

## Step 3: Server Log / Terminal Inspection

If the server is running but the app is broken, check the terminal where marimo is running for Python tracebacks. Look for lines containing `Traceback`, `Error`, or `Exception`.

If you redirected output to a log file:

```powershell
# PowerShell
Select-String -Path marimo_server.log -Pattern "Traceback|Error|Exception" -Context 0,10
```

```bash
# Linux/WSL
grep -A 10 "Traceback\|Error\|Exception" marimo_server.log
```

## Step 4: Browser Console Inspection

Use the `debug_marimo.js` script from this skill's `scripts/` directory. Open browser DevTools (F12), paste the script contents into the Console tab, and execute.

The script returns:

```json
{
  "totalCells": 26,
  "statusCounts": {"idle": 20, "error": 3, "outdated": 3},
  "errorMessages": ["'pd' was also defined by: ..."],
  "tracebacks": ["Traceback (most recent call last):\n  ..."],
  "outputCount": 23,
  "plotlyCharts": 5,
  "tables": 2
}
```

**Interpreting statuses:**

| Status | Meaning | Action |
|--------|---------|--------|
| `idle` | Cell executed successfully | None |
| `outdated` | Cell needs re-execution | Run all cells (Step 5) |
| `running` | Cell is currently executing | Wait |
| `error` | Cell has an error | Read `errorMessages` and fix the `.py` file |

## Step 5: Run All Cells

After fixing code, trigger re-execution of all cells using the `run_all_cells.js` script from this skill's `scripts/` directory. Paste into browser console and execute. Wait 30-60 seconds, then run `debug_marimo.js` again to verify.

If you launched with `--watch`, simply saving the file in Cursor will trigger re-execution of affected cells automatically.

## Step 6: Restart the Server

If cells are stuck or the state is corrupted:

**Option A — In the browser:**
1. Navigate to the notebook URL
2. Click the "Restart" button (kernel icon in the toolbar)
3. Wait for all cells to re-execute

**Option B — Kill and relaunch:**

```powershell
# PowerShell
Stop-Process -Name "marimo" -Force -ErrorAction SilentlyContinue
Start-Sleep -Seconds 2
marimo edit app.py --host 127.0.0.1 --port 8080 --watch
```

```bash
# Linux/WSL
pkill -f "marimo.*--port 8080"
sleep 2
marimo edit app.py --host 0.0.0.0 --port 8080 --watch
```

## Common Error Patterns and Fixes

### MultipleDefinitionError

**Cause**: Same variable name defined in multiple cells.
**Fix**: Consolidate imports into one `imports()` cell. Use `_` prefix for cell-local variables.

### CycleError

**Cause**: Cell A depends on cell B which depends on cell A (circular).
**Fix**: Merge the two cells, or break the cycle by introducing an intermediate cell.

### NameError: name 'x' is not defined

**Cause**: Cell references a variable that isn't returned by any upstream cell, or the cell's function signature is missing that variable.
**Fix**: Ensure the upstream cell has `return (x,)` and the downstream cell includes `x` in its function signature: `def my_cell(x):`.

### Stale/Outdated Cells After File Edit

**Cause**: File was edited but cells haven't re-run (server not in `--watch` mode).
**Fix**: Use `--watch` flag when launching, or run all cells via `run_all_cells.js`, or restart the kernel.

### Port Already in Use

**Cause**: Another process (possibly a previous marimo instance) is occupying the port.
**Fix**:

```powershell
# Find what's using the port
netstat -ano | findstr :8080
# Kill by PID
Stop-Process -Id <PID> -Force
```

### ModuleNotFoundError

**Cause**: A dependency isn't installed in the active Python environment.
**Fix**: Install it (`pip install <package>` or `poetry add <package>`), or add it to the PEP 723 header and use `--sandbox` mode.
