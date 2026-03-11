---
name: study-replicator
description: "Performs a high-fidelity, end-to-end replication of an academic research paper. Use with the `/study-replicator` command or for requests like \"replicate this paper\" or \"reproduce this study\". Accepts PDF, pasted text, or URL inputs."
---

# Study Replicator

This skill executes a rigorous, three-phase process to replicate academic research papers, primarily in finance. It chains strategy extraction, data validation, and full replication with strict, iterative quality gates at each step.

## Core Principles

- **High-Fidelity Replication**: The goal is to reproduce the paper's findings as closely as possible, without simplification or deviation.
- **No Synthetic Data**: If real data is unavailable for a required field, you **MUST** document it as a gap and lower the **Data Fidelity** score. **NEVER** invent, estimate, or synthesize data. Synthetic data is defined as any value not directly sourced from a real, verifiable data provider (e.g., Yahoo Finance, FRED). This includes model-estimated fills and values not traceable to a real observation.
- **Gated Execution**: Do not proceed to the next phase unless the current phase scores **>= 9/10** on all required dimensions.

---

## Step 0: Setup & Resumption Check

1.  **Extract Strategy Name**: From the paper title, create a short, descriptive name in `lowercase_with_underscores` (e.g., `value_momentum_sp500`).
2.  **Define Paths**: Set the base directory in PowerShell:
    ```powershell
    $STRATEGY_NAME = "value_momentum_sp500"  # Replace with extracted name
    $BASE_DIR = "C:\Users\Eddy\Documents\Obsidian Vault\Coding Projects\Academic Research\replication\$STRATEGY_NAME"
    ```
3.  **Resumption Check**: Check for the existence of sentinel files in `$BASE_DIR`:
    - If `phase2_complete.flag` exists, ask the user to confirm resuming from Phase 3.
    - If `phase1_complete.flag` exists, ask the user to confirm resuming from Phase 2.
    - Otherwise, start from Phase 1.
4.  **Create Folder Structure**: If starting from scratch, create the required directory structure:

    ```powershell
    foreach ($subdir in @("data", "results", "logs")) {
        New-Item -ItemType Directory -Path "$BASE_DIR\$subdir" -Force | Out-Null
    }
    ```

---

## Phase 1: Strategy & Logic Extraction

> **Note**: The `/strategy-extractor` skill is not included in this skill set. Perform strategy extraction directly by reading the paper and producing the `data_requirements.md` output yourself (see extraction format below).

1.  **Extract Strategy**: Read the paper (PDF or pasted text). Extract the following into `$BASE_DIR\data_requirements.md`:
    - **Strategy logic**: Entry/exit rules, rebalancing frequency, universe
    - **Securities required**: Tickers, asset classes, index members
    - **Data fields**: Price type (adj/unadj), volume, factor data, macro series
    - **Date range**: Exact start and end dates used in the paper
    - **Reference values**: Key statistics cited in the paper (Sharpe, returns, etc.) for later validation
2.  **Data Handoff**: Save the completed `data_requirements.md` to `$BASE_DIR`.
3.  **Quality Gate**: Self-assess a **composite Testability Assessment Score** across: Research Clarity, Data Availability, Implementation Complexity. Score 1–10 each; average is the composite.
4.  **Action**:
    -   If **Score >= 9/10**, create the sentinel file and proceed to Phase 2:
        ```powershell
        New-Item -ItemType File -Path "$BASE_DIR\phase1_complete.flag" -Force | Out-Null
        ```
    -   If **Score < 9/10**, begin the iteration loop. If the loop terminates without passing, follow the **Gate Failure Protocol**.

### Iteration Actions (Phase 1)

If the gate fails, try the following actions in a loop (max 10 attempts):

1.  Re-read the paper's methodology and data description sections to find missing parameters.
2.  Search for alternative Bloomberg fields or data sources for any unavailable data points.
3.  Critically re-evaluate the Research Clarity and Implementation Complexity scores with a more skeptical eye.

---

## Phase 2: Data Extraction & Validation

1.  **Invoke Skill**: Call the `/study-data-extractor` skill. The input is the `$BASE_DIR\data_requirements.md` file from Phase 1.
2.  **Data Handoff**: The primary output is the validated dataset, saved as `$BASE_DIR\data\validated_dataset.csv`.
3.  **Quality Gate**: Check the scores for all 6 validation aspects (Availability, Date Alignment, Adjustment, Spot-Checks, Summary Stats, Completeness).
4.  **Action**:
    -   If **All Scores >= 9/10**, create the sentinel file and proceed to Phase 3:
        ```powershell
        New-Item -ItemType File -Path "$BASE_DIR\phase2_complete.flag" -Force | Out-Null
        ```
    -   If **Any Score < 9/10**, begin the iteration loop. If the loop terminates without passing, follow the **Gate Failure Protocol**.

### Iteration Actions (Phase 2)

If the gate fails, try the following actions in a loop (max 10 attempts):

1.  **Availability**: Try the next data source in the hierarchy (e.g., `yfinance.download` → `yfinance.Ticker` → `pandas_datareader`).
2.  **Date Alignment**: Adjust start/end dates; check for holiday calendar mismatches.
3.  **Adjustment Method**: Switch between `auto_adjust=True` and `auto_adjust=False`; compute total return manually.
4.  **Spot-Checks/Summary Stats**: Double-check the paper's exact calculation method (log vs. simple returns, etc.).
5.  **Completeness**: For small gaps, try `ffill` or interpolation and document it. For large gaps, flag as a limitation and lower the score.

---

## Phase 3: Full Replication & Grading

1.  **Code Implementation**: Write a Python script `$BASE_DIR\replication.py`. Use the template from `references/replication_script_template.py` in this skill's folder as a starting point. The script must load `$BASE_DIR\data\validated_dataset.csv`.
2.  **Generate Outputs**: The script must save all outputs to `$BASE_DIR\results\` (e.g., `final_results.csv`, `intermediate_factor_series.csv`, `figure1.png`).
3.  **Run the script**:
    ```bash
    uv run python replication.py
    ```
4.  **Self-Grading**: Grade the replication against the **6-Dimension Scorecard**. Each score must be justified with quantitative evidence.
5.  **Quality Gate**: All 6 dimensions must score **>= 9/10**.
6.  **Action**:
    -   If **All Scores >= 9/10**, create the sentinel file and proceed to the final report:
        ```powershell
        New-Item -ItemType File -Path "$BASE_DIR\phase3_complete.flag" -Force | Out-Null
        ```
    -   If **Any Score < 9/10**, begin the iteration loop. If the loop terminates, follow the **Gate Failure Protocol**.

### Replication Scorecard (Phase 3)

| # | Dimension | What 9/10 Looks Like |
|---|---|---|
| 1 | **Data Fidelity** | All data sourced from real providers; any gaps are documented; no synthetic data used. |
| 2 | **Methodology Match** | A line-by-line code review confirms no logical deviations from the paper's described methodology. |
| 3 | **Results Match** | Key numerical results (e.g., Sharpe, coefficients) are within **±5%** of the paper's reported values. |
| 4 | **Code Correctness** | Code is clean, efficient, and free of bugs or logical errors. |
| 5 | **Reproducibility** | The script can be re-run to produce the exact same outputs. |
| 6 | **Documentation Quality** | The final report is clear, and the code is well-commented. |

### Iteration Actions (Phase 3)

If the gate fails, try the following actions in a loop (max 10 attempts):

1.  **Results Match**: Check tolerance calculations, date alignments, and look-ahead bias.
2.  **Methodology Match**: Re-read the paper's methods section against your code, line-by-line.
3.  **Code Correctness**: Add unit tests for key functions; simplify complex code.

---

## Iteration & Gate Failure Protocol

-   **Iteration Budget**: Each phase has a **maximum of 10 iterations**.
-   **Termination**: A loop terminates if the gate passes, max iterations are reached, or the score plateaus (no improvement across 2 consecutive iterations).
-   **Gate Failure Report**: If a loop terminates without passing, you **MUST** stop and report to the user with a structured table:

| Phase | Dimension | Best Score | Blocking Reason | Recommended Next Action |
|---|---|---|---|---|
| ... | ... | ... | ... | ... |

-   **Logging**: You **MUST** log every iteration attempt in `$BASE_DIR\logs\iteration_log.md`. Use this template for each entry:

    ```markdown
    ### Iteration 5 (Phase 2)

    -   **Action Taken**: Switched from `auto_adjust=True` to `auto_adjust=False` and manually calculated total returns.
    -   **Scores Before**: { "Adjustment": 7, "Spot-Checks": 6 }
    -   **Scores After**: { "Adjustment": 9, "Spot-Checks": 8 }
    ```

---

## Final Output & Deliverables

1.  **Consolidated Report**: A single `$BASE_DIR\replication_report.md` file covering all 3 phases, the final scorecards, and a plain-English **replication confidence statement**.
2.  **Code & Outputs**: The `replication.py` script and all its outputs in `$BASE_DIR\results\`.
3.  **Logs**: The `iteration_log.md` file in `$BASE_DIR\logs\`.
4.  **Strategy Note**: Append the extracted strategy note to `C:\Users\Eddy\Documents\Obsidian Vault\file dump\Academic Research\strategiesextracted.md`. If the file does not exist, create it.

---

## Windows/Cursor Compatibility Notes

- `/strategy-extractor` skill reference removed (skill not available); Phase 1 now self-contained with direct extraction instructions and format.

- All paths changed from `/home/ubuntu/Academic Research/replication/` to `C:\Users\Eddy\Documents\Obsidian Vault\Coding Projects\Academic Research\replication\`.
- Bash variable syntax (`BASE_DIR="..."`) replaced with PowerShell (`$BASE_DIR = "..."`).
- `mkdir -p` replaced with `New-Item -ItemType Directory -Force`.
- `touch` sentinel files replaced with `New-Item -ItemType File -Path "..." -Force | Out-Null`.
- Replication script run with `uv run python replication.py`.
- Reference template path changed to relative form: `references/replication_script_template.py` in this skill's folder.
- Data source hierarchy updated to use `yfinance` directly (no Manus MCP dependencies).
- Strategy note output path updated to vault's `file dump\Academic Research\strategiesextracted.md`.
