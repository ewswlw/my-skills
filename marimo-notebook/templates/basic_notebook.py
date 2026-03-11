# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "marimo",
#   "pandas",
#   "numpy",
#   "plotly",
# ]
# ///

import marimo

__generated_with = "0.19.9"
app = marimo.App(width="full", app_title="My Notebook")


@app.cell
def imports():
    import marimo as mo
    import pandas as pd
    import numpy as np
    import plotly.express as px
    return (mo, pd, np, px)


@app.cell
def header(mo):
    mo.md(
        """
        # My Notebook

        Description of what this notebook does.

        ---
        """
    )
    return


@app.cell
def controls(mo):
    # Define all interactive UI elements here.
    # Access their values in downstream cells via .value
    example_slider = mo.ui.slider(start=1, stop=100, value=50, label="Example Slider")
    example_dropdown = mo.ui.dropdown(
        options=["Option A", "Option B", "Option C"],
        value="Option A",
        label="Example Dropdown",
    )
    mo.hstack([example_slider, example_dropdown], justify="start", gap=2)
    return (example_slider, example_dropdown)


@app.cell
def main_output(mo, example_slider, example_dropdown):
    mo.md(
        f"""
        ## Output

        Slider value: **{example_slider.value}**

        Dropdown value: **{example_dropdown.value}**
        """
    )
    return


if __name__ == "__main__":
    app.run()
