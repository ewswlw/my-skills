<project_specification>
  <project_name>ShinkaEvolve Agent Skill</project_name>

  <overview>
    A self-contained Cursor agent skill that wraps all 4 ShinkaEvolve workflows
    (setup, convert, run, inspect) into a single unified SKILL.md for LLM-driven
    evolutionary code optimization. Targets Windows 10 / PowerShell users running
    Gemini as their sole LLM provider, with bundled Python scripts and 4 task
    templates for rapid experimentation. Success: an agent can scaffold a new task,
    run evolution within a $5 budget, and surface top-5 results — all without the
    user touching shinka internals or needing any provider besides Gemini.
  </overview>

  <technology_stack>
    - Python 3.11 via UV (`uv pip install shinka-evolve`)
    - shinka-evolve v0.0.4+ (PyPI package; `import shinka`)
    - Google Gemini API via google-genai:
      - Mutation LLMs: gemini-2.5-flash-preview + gemini-2.5-pro-preview
      - Embedding model: disabled (null) — Levenshtein distance for code dedup
      - Temperature sampling: [0.0, 0.5, 1.0] for mutation diversity
    - Hydra 1.3.2 (bundled with shinka for config presets)
    - Windows 10 + PowerShell (primary); cross-platform secondary
    - Workspace .venv (shared, not per-task)
  </technology_stack>

  <assumptions>
    - UV is installed and a workspace .venv exists at the project root
    - User has a valid Gemini API key stored in skill .env
    - .env propagation: before any shinka CLI call, the agent MUST either
      set $env:GOOGLE_API_KEY in the PowerShell session or copy .env to the
      task directory CWD (shinka's load_shinka_dotenv reads package-root and CWD only)
    - Windows 10 with PowerShell as primary shell (bash via WSL is secondary)
    - shinka-evolve installs cleanly from PyPI without native build deps
    - Local execution only (LocalJobConfig) — no SLURM, no Docker
    - Python is the primary language for evolved programs
    - Model names (gemini-2.5-flash-preview, gemini-2.5-pro-preview) are subject
      to Google renaming; always verify via `shinka_models` before runs
  </assumptions>

  <out_of_scope>
    - Obsidian vault note generation from results (deferred to v2)
    - SLURM / Docker cluster execution
    - Non-Python candidate languages (Julia, C++, Rust, Swift, CUDA)
    - OpenAI / Anthropic API integration (Gemini-only stack)
    - Embedding-based code deduplication (uses Levenshtein instead)
    - Custom Hydra config presets (users can add via --config-dir themselves)
  </out_of_scope>

  <core_features>
    <feature name="Task Setup (shinka-setup)">
      As an agent, scaffold a new ShinkaEvolve task from a natural-language
      description, producing evaluate.py + initial.py with EVOLVE-BLOCK markers
      + optional run_evo.py and shinka.yaml. Can start from a bundled template
      (algorithm, data processing, ML tuning, creative).
      Acceptance: smoke_test.py passes — metrics.json contains numeric
      combined_score, correct.json has correct=true, no exceptions.
    </feature>

    <feature name="Codebase Conversion (shinka-convert)">
      Convert an existing codebase into a Shinka-ready task directory by
      snapshotting relevant code into ./shinka_task/, adding tight EVOLVE-BLOCK
      markers, and generating the evaluator.
      Acceptance: sidecar directory passes smoke_test.py.
    </feature>

    <feature name="Evolution Run (shinka-run)">
      Launch async evolution batches via shinka_run CLI with Gemini models,
      enforce $5 budget cap via max_api_costs, auto-summarize results between
      batches, and propose next-batch system prompt for human-in-the-loop feedback.
      Defaults: 50 generations, 2 islands, 2 eval / 2 proposal concurrency,
      diff 60% / full 30% / cross 10% patch types.
      Acceptance: evolution completes within budget; results_dir populated
      with generation folders and SQLite DB.
    </feature>

    <feature name="Results Inspection (shinka-inspect)">
      Extract top-5 performing programs from a completed run and present them
      as a Markdown context bundle with scores, code snippets, and text feedback.
      Acceptance: inspect_best.py produces readable Markdown output.
    </feature>

    <feature name="Task Template Library">
      4 pre-built task templates as ready-to-customize scaffolds:
      (1) algorithm optimization, (2) data processing pipeline,
      (3) ML model tuning, (4) creative/novelty generation.
      Acceptance: each template's evaluate.py + initial.py passes smoke test
      out of the box.
    </feature>

    <feature name="Pre-flight Safety">
      Mandatory before any evolution launch:
      (1) shinka_models --verbose to verify Gemini API key and model availability
      (2) smoke_test.py to validate evaluator produces correct output schema
      (3) .env validation — confirm GOOGLE_API_KEY is set in environment
      Acceptance: clear error messages when any check fails.
    </feature>
  </core_features>

  <database_schema>
    N/A — ShinkaEvolve manages its own SQLite database internally via
    shinka.database.DatabaseConfig. The skill does not define additional schemas.
  </database_schema>

  <api_endpoints_summary>
    N/A — CLI-based skill. Key commands (PowerShell):
    <endpoint>shinka_run --task-dir DIR --results_dir DIR --num_generations N — Launch async evolution</endpoint>
    <endpoint>shinka_launch variant=NAME — Launch with Hydra presets</endpoint>
    <endpoint>shinka_models --verbose — Verify API keys and model availability</endpoint>
    <endpoint>shinka_visualize --port PORT --open — Launch WebUI for monitoring</endpoint>
  </api_endpoints_summary>

  <implementation_steps>
    Phase 1:  Skill Directory Setup — Create shinka-evolve/ at ~/.claude/skills/,
              .env with GOOGLE_API_KEY, SKILL.md skeleton
    Phase 2:  Setup Workflow — Task scaffolding instructions, evaluate.py/initial.py
              templates, EVOLVE-BLOCK conventions, template selection logic
    Phase 3:  Convert Workflow — Existing code conversion, sidecar directory
              strategy, minimal snapshot scope, Windows path handling
    Phase 4:  Run Workflow — shinka_run CLI with PowerShell escaping, Gemini model
              config, batch control policy, feedback loop, budget enforcement
    Phase 5:  Inspect Workflow — Top-5 program extraction, context bundle format
    Phase 6:  Bundled Scripts — smoke_test.py, inspect_best.py, run_evo.py,
              shinka.yaml default config, 4 task templates in scripts/templates/
    Phase 7:  Windows Compatibility — PowerShell commands throughout, path handling,
              .venv\Scripts\activate, env var propagation from skill .env
    Phase 8:  Pre-flight Safety — Mandatory smoke test flow, shinka_models check,
              .env validation, $5 budget cap in all configs
    Phase 9:  Reference Documentation — reference.md with full EvolutionConfig,
              DatabaseConfig, LocalJobConfig parameter tables
    Phase 10: Spec & Constitution — project-spec.md and project-constitution.md
  </implementation_steps>

  <success_criteria>
    <functional>
      All 4 workflows (setup, convert, run, inspect) documented with step-by-step
      instructions and executable on Windows 10 + PowerShell. Task templates pass
      smoke tests. Pre-flight checks catch missing .env, unavailable models, and
      evaluator failures with actionable error messages.
    </functional>
    <ux>
      An agent reading SKILL.md identifies the correct workflow within the first
      20 lines via explicit routing section. Each workflow has clear entry/exit
      conditions. Human-in-the-loop checkpoints are unambiguous.
    </ux>
    <technical>
      SKILL.md under 500 lines. All scripts use encoding='utf-8'. No hardcoded
      absolute paths. .env excluded from any git tracking. Config defaults:
      50 generations, 2 islands, 2/2 concurrency, Gemini-only, $5 cap,
      embedding_model=None, patch types diff/full/cross 60/30/10.
    </technical>
  </success_criteria>
</project_specification>
