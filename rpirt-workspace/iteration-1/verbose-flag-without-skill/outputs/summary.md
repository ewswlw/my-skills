# Verbose Flag — Summary

## What was done

Added a `--verbose` flag to an argparse-based CLI.

## Changes

- `parser.add_argument("--verbose", action="store_true", ...)` registers the flag; no value needed, defaults to `False`.
- A `log_debug(message, verbose)` helper centralises all debug output, writing to `sys.stderr` only when the flag is set.
- Debug calls are placed at key points: after argument parsing, before/after main logic, and on the no-input branch.

## Usage

```bash
# Normal run — no debug output
python changes.py --input hello

# Verbose run — debug lines appear on stderr
python changes.py --input hello --verbose
```

## Key design decisions

| Decision | Rationale |
|---|---|
| `action="store_true"` | Standard argparse pattern for boolean flags; no value required |
| Write to `sys.stderr` | Keeps debug output separate from stdout so piping still works cleanly |
| Centralised `log_debug` helper | Single place to change format/level later; avoids scattered `if verbose` checks |
