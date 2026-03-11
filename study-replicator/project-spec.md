# Project Specification: study-replicator Skill

This document outlines the specifications for the `study-replicator` skill, as determined by the project specification interview. The skill is designed to perform a high-fidelity, end-to-end replication of academic research papers, primarily in the financial domain.

## 1. Core Functionality

The skill will chain three distinct phases, with strict quality gates between them:

1.  **Phase 1: Strategy & Logic Extraction**: Inherits from the `/strategy-extractor` skill to parse a research paper and extract its core implementable logic, data requirements, and universe.
2.  **Phase 2: Data Extraction & Validation**: Inherits from the `/study-data-extractor` skill to source, pull, and rigorously validate the raw dataset required for the study.
3.  **Phase 3: Full Replication & Grading**: A new phase that involves writing and executing Python code to replicate the paper's core statistical models or backtests, comparing the results, and grading the entire process on multiple dimensions.

## 2. Triggering and Input

-   **Trigger**: The skill will be invoked via the `/study-replicator` command and also respond to natural language phrases like "replicate this paper" or "reproduce this study."
-   **Input Formats**: The skill must accept research papers provided as a PDF file, pasted raw text, or a URL pointing to a PDF.

## 3. The Three-Phase Workflow & Quality Gates

The workflow is sequential and gated. A phase will only commence if the preceding phase meets a minimum quality threshold.

### Phase 1: Strategy Extraction

-   **Goal**: Extract the testable, implementable rules from the paper.
-   **Gate**: The `Testability Assessment` score from this phase must be **≥ 9/10**. If not, the skill will enter an iteration loop.

### Phase 2: Data Extraction

-   **Goal**: Acquire and validate the dataset identified in Phase 1.
-   **Gate**: All 6 validation aspects from the `/study-data-extractor` skill (Field Availability, Date Alignment, Adjustment Method, Spot-Checks, Summary Stats, Completeness) must score **≥ 9/10**. If not, the skill will enter an iteration loop.

### Phase 3: Full Replication

-   **Goal**: Run the paper's core statistical/backtest code and compare the output to the paper's reported results.
-   **Gate**: All 6 dimensions of the replication scorecard (see below) must score **≥ 9/10**. If not, the skill will enter an iteration loop.

## 4. Iteration, Grading, and Reporting

-   **Iteration**: Each of the three phases has its own independent iteration budget of **10 attempts** to meet its quality gate. If a phase fails to meet its gate after 10 iterations, the skill will stop at that gate, report the final scores, explain the blocking reasons, and ask the user whether to proceed or abort.
-   **Grading**: All self-grading must be justified with **quantitative evidence** cited inline (e.g., % match, error tolerance).
-   **Replication Scorecard (Phase 3)**: The final replication will be graded across these six dimensions:
    1.  **Data Fidelity**: Accuracy and completeness of the sourced data vs. the paper's description.
    2.  **Methodology Match**: Correctness of the coded logic vs. the paper's methodology.
    3.  **Results Match**: Closeness of the replicated results (e.g., Sharpe ratio, p-values) to the paper's reported results. A **±5% relative tolerance** will be used, with deviations flagged.
    4.  **Code Correctness**: Quality, efficiency, and correctness of the replication Python code.
    5.  **Reproducibility**: Ease with which another researcher could re-run the code and get the same results.
    6.  **Documentation Quality**: Clarity and completeness of the final report and code comments.
-   **Reporting**: The final output will be a **single, consolidated markdown report** covering all three phases. This report will include a plain-English **replication confidence statement**. All generated code, raw outputs, intermediate data series, and charts will be saved alongside the report.

## 5. Core Rules & Constraints

-   **No Synthetic Data**: The skill is under a hard block never to use synthetic data. If a data point cannot be sourced from real data, it must be documented as an unresolvable gap, and the replication score must be reduced.
-   **Proprietary Data**: If the paper uses a proprietary dataset (e.g., CRSP, Bloomberg), the skill will document the gap, attempt the closest free-data substitute (e.g., Yahoo Finance), clearly label it as a substitute, and reduce the Data Fidelity score accordingly.
-   **Output Location**: All data, results, logs, and code will be saved to `/home/ubuntu/Academic Research/replication/[strategy_name]/`. The extracted strategy note will also be appended to `file dump/Academic Research/strategiesextracted.md`.
-   **Iteration Log**: A detailed `iteration_log.md` will be saved, documenting every attempt, the changes made, and the scores before and after.
-   **Resumption**: The skill will be able to detect existing output files and offer to resume from the last successfully completed phase.

## 6. Implementation Details

-   **Language**: All replication code will be written in **Python**, using standard data science libraries (pandas, numpy, statsmodels, vectorbt, etc.).
-   **Saved Artifacts**: The skill will save the replication script, result tables (CSV/markdown), all intermediate outputs (factor series, signals, weights), and any generated charts.
