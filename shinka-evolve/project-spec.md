<project_specification>
  <project_name>ShinkaEvolve Trading Skill</project_name>

  <overview>
    A portable Cursor/Claude agent skill that scaffolds and runs SakanaAI ShinkaEvolve
    (LLM + evolutionary search) to automatically evolve algorithmic trading signal code.
    The skill produces evaluate.py + initial.py in any project, configures Gemini API
    access via environment variables, runs shinka_run, and summarizes results. Success
    is measured by the agent's ability to go from "evolve my trading strategy" to a
    running evolution loop with proper fitness, costs, and safety guardrails in under
    5 minutes of agent interaction.
  </overview>

  <technology_stack>
    - Python >=3.10 with uv package manager
    - shinka-evolve >=0.0.4 (PyPI)
    - numpy >=1.24, pandas >=2.0
    - yfinance (optional fallback data source)
    - Google Gemini API (primary LLM for code evolution)
    - Cursor Agent Skills framework (SKILL.md + frontmatter)
  </technology_stack>

  <assumptions>
    - User has Python >=3.10 and uv installed
    - User has a valid Gemini API key (or other OpenAI-compatible key)
    - User's project has a Python environment (venv or uv-managed)
    - OHLCV data is available as CSV or downloadable via yfinance
    - User understands basic backtesting concepts (Sharpe, drawdown, costs)
  </assumptions>

  <out_of_scope>
    - Live/paper trading execution (skill produces evolved code, not a broker connector)
    - Multi-asset portfolio optimization (single-instrument signal evolution only)
    - GPU-accelerated evaluation (LocalJobConfig only; no Slurm scaffolding)
    - Custom LLM fine-tuning or local model hosting
    - Automated walk-forward or purged CV (documented as upgrade path, not default)
  </out_of_scope>

  <core_features>
    <feature name="Auto-scaffold task directory">
      As a user, when I say "evolve my trading strategy with ShinkaEvolve", the agent
      creates a task directory with evaluate.py and initial.py tailored to my data,
      so I don't have to write boilerplate from scratch.
      Acceptance: task_dir contains both files, both import correctly, evaluate.py
      runs without error on synthetic data.
    </feature>

    <feature name="Environment setup">
      As a user, the agent checks for shinka-evolve installation, installs if missing
      via uv, and verifies GEMINI_API_KEY is set in the environment.
      Acceptance: import shinka succeeds, API key env var is non-empty.
    </feature>

    <feature name="Configurable fitness function">
      As a user, combined_score uses annualized Sharpe on train data with penalties
      for turnover, drawdown, and train-test divergence, all with tunable weights.
      Acceptance: aggregate_metrics_fn returns combined_score as float, higher=better.
    </feature>

    <feature name="Safety guardrails">
      As a user, validate_fn rejects NaN signals, non-finite metrics, and too-few-bars
      results. max_api_costs defaults to $5. Agent warns if cap is removed.
      Acceptance: invalid candidates return (False, error_msg) from validate_fn.
    </feature>

    <feature name="Run evolution">
      As a user, the agent runs shinka_run with sensible defaults (50 generations,
      2 eval jobs, Gemini models) and streams progress.
      Acceptance: shinka_run exits 0, results_dir contains metrics.json.
    </feature>

    <feature name="Post-evolution inspection">
      As a user, I can run inspect_best.py to see a plain-text tearsheet of the
      best evolved strategy on both train and test sets.
      Acceptance: script prints Sharpe, CAGR, max DD, win rate, turnover.
    </feature>
  </core_features>

  <database_schema>
    N/A — ShinkaEvolve manages its own SQLite database internally.
    The skill does not define custom tables.
  </database_schema>

  <api_endpoints_summary>
    N/A — This is an agent skill, not a web service.
    External API: Google Gemini (generativelanguage.googleapis.com) for LLM mutations.
    External API: Yahoo Finance (via yfinance) for OHLCV data fallback.
  </api_endpoints_summary>

  <implementation_steps>
    Phase 1: Create skill directory at ~/.claude/skills/shinka-evolve/
    Phase 2: Write SKILL.md with frontmatter, triggers, prerequisites, agent workflow
    Phase 3: Write reference.md with full evaluate.py and initial.py templates
    Phase 4: Write scripts/inspect_best.py post-evolution tearsheet utility
    Phase 5: Write .env.example documenting GEMINI_API_KEY pattern
    Phase 6: Write project-constitution.md and project-spec.md
    Phase 7: Integrate fitness formula with all mitigations (gap penalty, DD, turnover)
    Phase 8: Verify all files, test imports, confirm skill is discoverable
  </implementation_steps>

  <success_criteria>
    <functional>
      - Agent triggers on "ShinkaEvolve", "evolve trading strategy", "program evolution"
      - evaluate.py + initial.py are generated and run without import errors
      - shinka_run completes N generations and writes results
      - inspect_best.py prints readable tearsheet
    </functional>
    <ux>
      - User goes from prompt to running evolution in under 5 minutes of interaction
      - Agent explains what it's doing at each step
      - API key is never exposed in output
    </ux>
    <technical>
      - SKILL.md under 500 lines
      - All file references one level deep from SKILL.md
      - No hardcoded API keys anywhere in the skill
      - Version-pinned dependencies
    </technical>
  </success_criteria>
</project_specification>
