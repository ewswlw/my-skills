<?xml version="1.0" encoding="UTF-8"?>
<project_specification>

  <project_name>Credit Data Skill — Bloomberg Credit Market Data Fetcher</project_name>

  <overview>
    A Cursor Agent Skill providing natural-language-driven access to Bloomberg credit
    market spread and return series data. The skill consists of a Python module
    (credit_data.py) and an agent instruction file (SKILL.md). Any agent or script
    that needs OAS spreads, CDX spreads, or excess return indices for CAD IG, US IG,
    US HY, or CDX markets should use this skill. Success is measured by: correct
    Bloomberg ticker and field resolution for all 26 instruments, zero maintenance
    drift from fetch_data.py's ER chain-linking algorithm, and reliable natural
    language alias matching with no ambiguous mis-routing.
  </overview>

  <technology_stack>
    Python 3.11+, xbbg (Bloomberg Terminal bridge), pandas 2.0+, numpy 1.26+,
    uv (package manager). Bloomberg Terminal required at runtime.
  </technology_stack>

  <assumptions>
    - Bloomberg Terminal is installed, licensed, and open when data is fetched.
    - The active virtual environment contains xbbg, pandas, and numpy.
    - The user's machine is Windows (paths use backslash conventions).
    - Column names in INSTRUMENT_REGISTRY are stable downstream identifiers.
    - The ER YTD-to-index algorithm in fetch_data.py is the reference implementation.
  </assumptions>

  <out_of_scope>
    - EUR IG, GBP IG, EM spreads, EMBI, iTraxx (deferred to future extension).
    - Bloomberg real-time streaming (BDP/BDS) — historical bdh only.
    - Plotly visualisations (handled by DataPipeline in fetch_data.py).
    - YAML config file loading.
    - Bloomberg BEST_FPERIOD_OVERRIDE fetches (equity forecasts).
  </out_of_scope>

  <core_features>

    <feature name="Natural Language Alias Resolution">
      As a user or agent, I can say "cad ig", "canadian credit", "US HY spreads",
      "cdx ig er", or any of 80+ registered phrases and the skill will resolve it
      to the correct Bloomberg ticker and field without manual lookup.
      Acceptance criteria: longest-first matching prevents ambiguous collisions;
      direct column name lookup works as fallback.
    </feature>

    <feature name="Automatic Bloomberg Field Selection">
      OAS instruments use INDEX_OAS_TSY_BP; CDX instruments use
      ROLL_ADJUSTED_MID_PRICE; CDX ER indices use PX_LAST; ER YTD instruments use
      INDEX_EXCESS_RETURN_YTD. Field selection is invisible to the caller.
      Acceptance criteria: no caller ever needs to specify a field manually.
    </feature>

    <feature name="ER YTD to Chain-Linked Index Conversion">
      INDEX_EXCESS_RETURN_YTD values are automatically converted to chain-linked
      cumulative indices (base=100) using the year-by-year algorithm from
      fetch_data.py. Output columns are suffixed _index.
      Acceptance criteria: algorithm is byte-for-byte identical to the reference
      implementation; year-end rollovers produce no drift.
    </feature>

    <feature name="Multi-Series Merge">
      When multiple instruments are requested, results are outer-joined on the date
      index and forward-filled (by default) from each series' first valid date.
      Acceptance criteria: no data truncation; each series starts at its own
      Bloomberg history start, not the latest common date.
    </feature>

    <feature name="Bad-Date Correction">
      Four known Bloomberg data quality dates (all 2005-11-15) are automatically
      corrected with 'use_previous' action, matching fetch_data.py behaviour.
      Acceptance criteria: corrections applied silently on every fetch call.
    </feature>

    <feature name="Spread Context Intelligence">
      context(query) returns a formatted summary: current level, full-history
      percentile, 5-year percentile, Z-score, 52-week range bar, and regime label
      (TIGHT / FAIR / WIDE / DISTRESSED) for any OAS or CDX instrument.
      Acceptance criteria: regime thresholds at 35/65/85th full-history percentile;
      output is human-readable in terminal.
    </feature>

    <feature name="Fetch All Shortcut">
      fetch_all() and trigger phrases like "all credit data" / "fetch everything"
      pull all 26 instruments in one merged call.
      Acceptance criteria: all registry instruments returned in a single DataFrame.
    </feature>

    <feature name="Save to CSV">
      save(df, path) writes a DataFrame to UTF-8 CSV, creating parent directories
      as needed. Path is caller-specified at runtime.
      Acceptance criteria: UTF-8 encoding; no silent failures on missing dirs.
    </feature>

    <feature name="CLI Entry Point">
      credit_data.py is executable as a script: supports query, --start, --end,
      --freq, --out, --all, and --context flags.
      Acceptance criteria: uv run python credit_data.py "cad ig" works end-to-end.
    </feature>

  </core_features>

  <database_schema>
    No database. All data fetched from Bloomberg Terminal via xbbg at runtime.
    Optional CSV output via save().
  </database_schema>

  <api_endpoints_summary>
    Internal Python API only (no HTTP endpoints):
    CreditData.fetch(query, **kwargs) — resolve + fetch + merge
    CreditData.fetch_all(**kwargs) — fetch all instruments
    CreditData.resolve(query) — alias resolution only (no Bloomberg call)
    CreditData.context(query) — spread intelligence summary
    CreditData.save(df, path) — CSV persistence
  </api_endpoints_summary>

  <implementation_steps>
    Phase 1: Skill directory structure created.
    Phase 2: INSTRUMENT_REGISTRY and ALIAS_MAP built (26 instruments, 80+ aliases).
    Phase 3: CreditData core: __init__, resolve(), _get_periodicity().
    Phase 4: _fetch_columns(): field-grouped blp.bdh() calls with MultiIndex handling.
    Phase 5: _convert_er_to_index(): year-by-year chain-linking algorithm.
    Phase 6: _apply_bad_dates(): mirrors DataPipeline.clean_data().
    Phase 7: fetch(), fetch_all(), context(), save() public API.
    Phase 8: FETCH_ALL_TRIGGERS and "fetch all" routing in fetch().
    Phase 9: context() method: percentile, Z-score, 52-week range, regime label.
    Phase 10: CLI entry point + SKILL.md + ticker_registry.md + spec files.
  </implementation_steps>

  <success_criteria>

    <functional>
      - cd.fetch("cad ig") returns a single-column DataFrame with cad_oas
      - cd.fetch("cad ig er") returns cad_ig_er_index as a chain-linked series
      - cd.fetch("cdx ig") uses ROLL_ADJUSTED_MID_PRICE automatically
      - cd.fetch("all credit data") returns all 26 instruments
      - cd.context("cad ig") prints percentile, Z-score, regime label
      - cd.resolve("cad ig er") returns ['cad_ig_er'] (not ['cad_oas'])
      - Bad date 2005-11-15 is corrected without manual intervention
    </functional>

    <ux>
      - Any credit-market phrase a portfolio manager would naturally say resolves correctly
      - Bloomberg Terminal errors surface a clear "Terminal must be open" message
      - context() output is readable at a glance in a terminal window
      - CLI --help shows all options with examples
    </ux>

    <technical>
      - Zero imports from Market Data Pipeline/fetch_data.py (fully standalone)
      - ER algorithm produces identical results to fetch_data.py reference
      - All file I/O uses UTF-8 encoding explicitly
      - uv run python used for all execution
      - Type hints on all public functions
      - Docstrings on all public methods (Args / Returns / Raises)
    </technical>

  </success_criteria>

</project_specification>
