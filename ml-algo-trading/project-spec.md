<project_specification>
  <project_name>ML Algo-Trading Skill — Vault Integration</project_name>

  <overview>
    Integrate 7 Obsidian vault algo-trading documents into the ml-algo-trading skill's
    reference files using a surgical synthesis approach. The vault documents are
    prompt/instruction-level specifications; the skill references are implementation-level
    Python guides. Integration extracts only content unique to the vault that is absent
    from existing skill refs, adds it with appropriate annotations, and does not duplicate
    or replace existing code. Success is measured by expanded coverage with zero duplication,
    consistent annotations on ambiguous items, and an updated SKILL.md reference table that
    accurately describes all new sections.
  </overview>

  <technology_stack>
    - Python >= 3.11, managed by UV
    - Markdown (Obsidian vault format for source; plain markdown for skill refs)
    - No new dependencies required — integration is documentation/code only
  </technology_stack>

  <assumptions>
    - Vault source files in `Prompts &amp; Instructions/algo trading/` are read-only
    - Existing skill reference Python implementations are correct and production-tested
    - The 9-step SKILL.md pipeline is correct and not changed by this integration
    - Agents load reference files on demand via the reference table; file size matters
    - CONFIG objects from vault are "spec templates", not authoritative function signatures
  </assumptions>

  <out_of_scope>
    - Modifying vault source files
    - Changing SKILL.md pipeline steps (Steps 0–8)
    - Integrating vault files not listed: Quantitative Research Workflow Principles,
      Financial Data Structures &amp; Labeling Methods, Alternative Data &amp; NLP for Trading,
      VectorBT Backtesting Specification, Manual Backtest Tear Sheet Specification
    - Creating a UI, API, or any runtime system
    - Updating .cursor/agents/ or .cursor/commands/ files
  </out_of_scope>

  <core_features>
    <feature name="regime-philosophy enrichment">
      Add "What Shifts Across Regimes" table (means, variances, autocorrelations,
      correlations, factor loadings) and "Asset and Timeframe Adaptations" table
      (daily/weekly/monthly/intraday characteristics) to regime-philosophy.md.
      Acceptance: both tables present, no existing content removed or duplicated.
    </feature>

    <feature name="predictability agent exec spec">
      Add annotated CONFIG object (marked as spec template), markdown report template
      (10-section structure), and expanded decision rules table to predictability-analysis.md.
      Acceptance: CONFIG has explicit annotation that function defaults take precedence;
      report template is formatted as a fenced markdown block; decision rules table
      matches vault's full set of conditions.
    </feature>

    <feature name="drawdown analysis in validation">
      Add calculate_drawdown(), time_under_water(), and validate_strategy() composite
      to validation-backtesting.md as a new "Drawdown Analysis" section.
      validate_strategy() annotated as "convenience reference, not production function."
      Acceptance: all three functions present with correct docstrings and type hints.
    </feature>

    <feature name="GA spec extension in strategy-improvement">
      Extend strategy-improvement.md Section B with GA specification details from vault:
      edge case handling (market anomalies, data quality, computational constraints),
      success criteria checklist, and output requirements spec.
      Acceptance: Section B extended, no duplication of existing GA code/pitfalls table.
    </feature>

    <feature name="eda-ml-practices reference file">
      Create new reference file eda-ml-practices.md containing:
      (1) EDA methodology with 17-point required output format,
      (2) ML trading best practices (8 items),
      (3) ML trading pitfalls (5 items),
      (4) four-phase validation checklist (pre-development, development, validation, documentation).
      Acceptance: file created, linked from SKILL.md reference table.
    </feature>

    <feature name="performance optimization in portfolio-construction">
      Add new "Performance Optimization" section to portfolio-construction.md with:
      (1) NumPy/Pandas vectorization patterns (loop vs vectorized comparison),
      (2) mp_pandas_obj() atoms-and-molecules multiprocessing function (Lopez de Prado pattern),
      (3) PortfolioManager convenience class.
      Acceptance: section present, mp_pandas_obj has full docstring, no duplication of HRP code.
    </feature>

    <feature name="SKILL.md reference table update">
      Update Reference Files table in SKILL.md: expand each row description to name new
      sections explicitly; add eda-ml-practices.md as a new row.
      Acceptance: all 10 reference files listed with accurate one-line descriptions.
    </feature>

    <feature name="CHANGELOG.md">
      Create CHANGELOG.md in skill root with a single dated entry documenting all 6 file
      changes and 1 new file creation.
      Acceptance: file created, entry dated 2026-03-10, describes each modified file.
    </feature>
  </core_features>

  <implementation_steps>
    Phase 1: Write project-constitution.md (DONE)
    Phase 2: Write project-spec.md (DONE)
    Phase 3: Update regime-philosophy.md — add What Shifts table + Timeframe table
    Phase 4: Update predictability-analysis.md — annotated CONFIG + report template + decision rules
    Phase 5: Update validation-backtesting.md — drawdown + time_under_water + validate_strategy
    Phase 6: Update strategy-improvement.md — extend Section B with GA spec details
    Phase 7: Create eda-ml-practices.md — EDA methodology, ML best practices, validation checklist
    Phase 8: Update portfolio-construction.md — Performance Optimization section
    Phase 9: Update SKILL.md reference table (expanded descriptions + eda-ml-practices row) + create CHANGELOG.md
  </implementation_steps>

  <success_criteria>
    <functional>
      - All 5 reference files updated with no duplication of existing content
      - eda-ml-practices.md created and linked from SKILL.md
      - SKILL.md reference table accurately names all new sections in each file
      - CHANGELOG.md entry written with timestamp 2026-03-10
      - project-constitution.md and project-spec.md present in skill root
    </functional>
    <ux>
      - CONFIG annotation in predictability-analysis.md prevents agent confusion on defaults
      - validate_strategy() annotation prevents agents from using it as production code
      - Each reference file remains self-contained (no broken cross-references)
      - eda-ml-practices.md is structured for fast agent scanning (headers match vault source)
    </ux>
    <technical>
      - Zero duplication of Python function implementations across reference files
      - All new Python functions have Args / Returns docstrings with type hints
      - No vault frontmatter (tags, created, description fields) bleeds into reference files
      - All file I/O in any added code uses encoding='utf-8'
    </technical>
  </success_criteria>
</project_specification>
