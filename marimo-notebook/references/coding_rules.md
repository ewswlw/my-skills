# Marimo Coding Rules & Gotchas

Read this file when writing or debugging marimo notebook code. These rules are non-negotiable — violating them causes runtime errors.

## Reactive Execution Model

Marimo notebooks form a **directed acyclic graph (DAG)**. When a cell's dependencies change, it and all downstream cells re-execute automatically. This means:

- Cell execution order is determined by the dependency graph, not by position in the file.
- The last expression in a cell is automatically displayed as output.
- UI elements (e.g., `mo.ui.slider`) are reactive: changing them triggers re-execution of all cells that reference their `.value`.

## Variable Rules

### Rule 1: No Redefinition Across Cells

Every variable name must be defined in exactly one cell. If `pd` is imported in cell A, no other cell can assign to `pd`.

**Error**: `MultipleDefinitionError: 'pd' was also defined by: ...`

**Fix**: Consolidate all imports into a single `imports()` cell.

### Rule 2: Underscore Prefix = Cell-Local

Variables starting with `_` are scoped to their cell. Use them for loop counters, temp variables, and anything that doesn't need to be shared.

```python
@app.cell
def chart_one(mo, df, px):
    _fig = px.scatter(df, x="a", y="b")  # _fig is local
    mo.ui.plotly(_fig)
    return

@app.cell
def chart_two(mo, df, px):
    _fig = px.bar(df, x="a", y="c")  # No conflict with chart_one's _fig
    mo.ui.plotly(_fig)
    return
```

### Rule 3: Return What Downstream Cells Need

A cell's `return` statement declares which variables are available to other cells. Only return variables that other cells actually use.

```python
@app.cell
def load_data(pd):
    _raw = pd.read_csv("data.csv")       # local, not shared
    df = _raw.dropna()                     # shared downstream
    return (df,)                           # tuple required even for one var
```

### Rule 4: No Cycles

If cell A depends on cell B, cell B cannot depend on cell A. This creates a cycle and marimo will refuse to run.

### Rule 5: Cell Function Signature = Dependencies

The arguments in a cell's function signature declare its dependencies. Marimo uses these to build the DAG.

```python
@app.cell
def my_cell(mo, df, model):  # This cell depends on mo, df, and model
    ...
```

## Common Patterns

### Imports Cell

Always create one cell for all imports. Return every imported module.

```python
@app.cell
def imports():
    import marimo as mo
    import pandas as pd
    import numpy as np
    return (mo, pd, np)
```

### UI Controls Cell

Define all interactive elements in one cell. Return each element so downstream cells can access `.value`.

```python
@app.cell
def controls(mo):
    ticker = mo.ui.dropdown(options=["AAPL", "TSLA"], value="AAPL", label="Ticker")
    slider = mo.ui.slider(start=1, stop=100, value=50, label="Window")
    mo.hstack([ticker, slider])
    return (ticker, slider)
```

### Display Cells

Use `mo.md()` for markdown, `mo.ui.plotly()` for Plotly figures, `mo.ui.table()` for dataframes. The last expression is auto-displayed.

```python
@app.cell
def show_chart(mo, df, px):
    _fig = px.line(df, x="date", y="price", title="Price Chart")
    mo.ui.plotly(_fig)
    return
```

## UI Element Reference

| Element | Usage |
|---------|-------|
| `mo.ui.dropdown(options, value, label)` | Select from list |
| `mo.ui.slider(start, stop, value, step, label)` | Numeric slider |
| `mo.ui.number(start, stop, value, step, label)` | Numeric input |
| `mo.ui.text(value, label)` | Text input |
| `mo.ui.checkbox(label, value)` | Boolean toggle |
| `mo.ui.table(df, label)` | Interactive dataframe table |
| `mo.ui.plotly(fig)` | Interactive Plotly chart |
| `mo.ui.data_explorer(df)` | Full dataframe explorer |
| `mo.ui.tabs({"Tab1": el1, "Tab2": el2})` | Tabbed layout |
| `mo.hstack([el1, el2], gap=2)` | Horizontal layout |
| `mo.vstack([el1, el2], gap=1)` | Vertical layout |
| `mo.md("# Title")` | Markdown output |
