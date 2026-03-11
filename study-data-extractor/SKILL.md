---
name: study-data-extractor
description: "Extracts and validates the raw dataset from an academic research paper using Python data libraries. Use for requests like: recreate paper data, academic research data, extract data from paper, research replication, get data for paper."
---

# Study Data Extractor

This skill extracts and validates the raw dataset required to replicate an academic research paper. It uses a prioritized hierarchy of Python data sources, runs a rigorous 6-aspect validation process, and produces a clean, validated CSV file and a full reproducibility package.

**CRITICAL**: All file outputs **MUST** be saved within the designated project folder: `C:\Users\Eddy\Documents\Obsidian Vault\Coding Projects\Academic Research\replication\[strategy_name]\`.

## Core Workflow

1.  **Setup**: Check prerequisites and create the strategy-specific folder structure.
2.  **Requirements Extraction**: Read the paper (PDF/text), validate the input, and automatically extract data requirements. Present a summary to the user for confirmation.
3.  **Data Pull**: Fetch the required data using the prioritized data source hierarchy.
4.  **Validation Loop**: Run all 6 validation tests. If any score is <9/10, iterate on fixes until all aspects pass.
5.  **Final Output**: Generate the final validated CSV, extraction script, and assessment report.

---

## 1. Setup

### Prerequisite Check

First, verify that all necessary data sources and libraries are available.

```bash
uv add yfinance pandas_datareader && uv run python -c "import yfinance; import pandas_datareader; print('All dependencies OK')"
```

If this command fails, inform the user that the environment setup failed and stop the task.

### Create Folder Structure

All output for a given paper must be stored in a unique, strategy-specific folder.

1.  **Extract Strategy Name**: From the paper title or abstract, create a short, descriptive name in `lowercase_with_underscores` (e.g., `value_momentum_sp500`).
2.  **Create Directories**: Execute the following commands to create the full folder structure.

```powershell
$STRATEGY_NAME = "value_momentum_sp500"  # Replace with extracted name
$BASE_DIR = "C:\Users\Eddy\Documents\Obsidian Vault\Coding Projects\Academic Research\replication\$STRATEGY_NAME"

foreach ($subdir in @("data", "results", "logs", "tests", "mappings")) {
    New-Item -ItemType Directory -Path "$BASE_DIR\$subdir" -Force | Out-Null
}

Write-Host "Created folder structure at $BASE_DIR"
```

---

## 2. Requirements Extraction

This step is semi-automated. The agent reads the paper, validates it, extracts requirements, and asks the user for confirmation.

1.  **Read Paper**: Read the attached PDF or text file.
2.  **Validate Input**: Check if the extracted text is valid. If the text is very short (<500 characters) or lacks common academic terms, assume it is a scanned image. Inform the user and ask them to paste the text directly.
3.  **Extract Requirements**: Parse the text and extract the following into a structured format (e.g., JSON):
    *   **Securities**: Tickers, ISINs, CUSIPs.
    *   **Fields**: Specific data points needed (e.g., `["Adjusted Close", "Volume"]`).
    *   **Date Range**: Exact start and end dates.
    *   **Reference Values**: Any specific data points or summary statistics for validation.
4.  **Confirm with User**: Present the extracted requirements in a clean table and ask the user to confirm or correct them before proceeding.
5.  **Save Requirements**: Once confirmed, save the requirements to `mappings\data_requirements.md` and `data\reference_values.json`.

---

## 3. Data Pull

Create and execute a Python script `extract_raw_data.py` that uses the following prioritized data source hierarchy. For full implementation details, read `references/extraction_script_template.py` and `references/validation_tests.md` in this skill's folder.

**Data Source Hierarchy:**

1.  **`yfinance` Library**: Primary source for equity/ETF data — `yfinance.download(tickers, start=start, end=end, auto_adjust=True)`.
2.  **`yfinance` Ticker API**: Fallback for more granular requests — `yfinance.Ticker(symbol).history(period=...)`.
3.  **`pandas_datareader`**: For macroeconomic data from FRED — `pandas_datareader.data.get_data_fred(series, start, end)`.
4.  **Web search**: Last resort for obscure data.

Run the script with:
```bash
uv run python extract_raw_data.py
```

---

## 4. Validation Loop

Run the 6-aspect validation process. Each aspect is a separate Python script in the `tests\` directory that generates a score from 1-10. **All 6 aspects must score >=9/10.**

| # | Aspect | Question | Test Script |
|---|---|---|---|
| 1 | **Field Availability** | Does every required data point exist? | `test_availability.py` |
| 2 | **Date Alignment** | Does the CSV cover the paper's exact date range? | `test_date_alignment.py` |
| 3 | **Adjustment Method** | Does the price series type match the paper? | `test_adjustment_method.py` |
| 4 | **Spot-Checks** | Do paper values match the CSV within tolerance (±1%)? | `test_spot_checks.py` |
| 5 | **Summary Stats** | Do computed stats match paper-reported stats? | `test_summary_stats.py` |
| 6 | **Completeness** | Is the final CSV complete with minimal NaN values? | `test_completeness.py` |

Run each test with `uv run python tests\test_[aspect].py`.

If any aspect scores <9, enter an iterative loop: diagnose, fix, re-run, and log until all scores pass.

---

## 5. Final Output

Once all validation aspects pass, generate the final reproducibility package: a clean CSV, the extraction script, and a detailed assessment report.

---

## Quick Reference

### Iteration & Setup Fixes

| Phase | Problem | Fix |
|---|---|---|
| **Setup** | Dependency installation fails | Inform user and stop. The environment is not ready. |
| **Input** | PDF is unreadable (scanned image) | Inform user and ask them to paste the text directly. |
| **Validation** | Availability score is low | Try next data source in hierarchy; search for alternative tickers. |
| **Validation** | Date Alignment is off | Adjust start/end dates; check for holiday calendar mismatches. |
| **Validation** | Adjustment Method mismatch | Switch between `auto_adjust=True` and `auto_adjust=False`; compute total return manually. |
| **Validation** | Spot-Checks fail | Document systematic differences (e.g., Yahoo vs. Bloomberg); verify reference values. |
| **Validation** | Summary Stats mismatch | Match the paper's exact calculation method (e.g., log returns vs. simple returns). |
| **Validation** | Completeness is low | Fill small gaps with `ffill` or interpolation; document large gaps as a limitation. |

### Scoring Keys (Target: >=9/10)

-   **Availability**: 10 = all fields found; 9 = minor workarounds needed.
-   **Date Alignment**: 10 = exact range; 9 = >=99% coverage.
-   **Adjustment**: 10 = perfect match; 9 = minor, documented differences.
-   **Spot-Checks**: 10 = >=95% match within 1% error; 9 = >=90% match.
-   **Summary Stats**: 10 = >=90% match within 5%; 9 = >=80% match.
-   **Completeness**: 10 = >=99% overall fill rate; 9 = >=95% fill rate.

---

## Windows/Cursor Compatibility Notes

- Frontmatter description: removed "Manus-native data sources" — now uses standard Python libraries.
- Output path changed from `/home/ubuntu/Academic Research/replication/` to `C:\Users\Eddy\Documents\Obsidian Vault\Coding Projects\Academic Research\replication\`.
- Install command: `uv add yfinance pandas_datareader` replaces `sudo uv pip install --system`.
- Python verify command: `uv run python -c` replaces `python3.11 -c`.
- Bash variables and `mkdir -p` replaced with PowerShell `$VAR = "..."` and `New-Item -ItemType Directory -Force`.
- Data source hierarchy updated: removed Manus `/stock-analysis` skill MCP calls; replaced with direct `yfinance` library calls.
- Reference file paths changed to relative form: `references/[file]` in this skill's folder.
- Test scripts run with `uv run python tests\test_[aspect].py`.
