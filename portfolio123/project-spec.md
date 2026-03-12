<project_specification>
  <project_name>Portfolio123 Comprehensive Agent Skill</project_name>

  <overview>
    A full-surface Cursor Agent Skill for the Portfolio123 quantitative investing platform that automates every possible interaction — API integration via p123api, browser automation for UI-only tasks, ranking system construction, universe management, screen backtesting, AI Factor ML workflows, and data collection. The skill serves a single power user (Ultimate tier, US + Canada markets) who wants to build, test, and refine quantitative investment strategies without manually navigating the P123 platform. Success is measured by: (1) zero manual P123 UI navigation required for any supported workflow, (2) all API operations wrapped with credit tracking and error handling, (3) the skill improves itself over time through continual learning from execution outcomes.
  </overview>

  <technology_stack>
    - Python >=3.11 via uv (runtime)
    - p123api 2.2.0+ (Portfolio123 REST API wrapper, PyPI)
    - cursor-ide-browser MCP tools (browser_navigate, browser_click, browser_snapshot, browser_type, browser_select_option, browser_wait_for, browser_fill, browser_lock, browser_unlock)
    - xml.etree.ElementTree (ranking system XML construction)
    - CSV/JSON (data persistence)
    - Environment variables for API auth (P123_API_ID, P123_API_KEY)
  </technology_stack>

  <assumptions>
    - User has Portfolio123 Ultimate subscription (20-year data, full FactSet)
    - User has active API credentials with 10,000 monthly credit budget
    - User has p123api installed in their Python environment
    - Cursor IDE browser tools are available and functional
    - P123 platform URL structure remains stable (portfolio123.com)
    - P123 API endpoint signatures match p123api 2.2.0 wrapper
    - Research-only usage — no live money at risk
    - Markets covered: US + Canada only
  </assumptions>

  <out_of_scope>
    - Live trading account management (rebalance commits, transaction imports)
    - Community features (forums, shared models, research groups)
    - Scheduled/recurring operations (cron, Task Scheduler)
    - Global markets beyond US + Canada (Europe, Asia, EM)
    - Custom data imports (Imported Data Series, custom factors)
    - P123 account management (billing, subscription changes)
    - Neural Networks (Keras/DeepTables), SVM, GAM, Linear Regression algorithms
    - Random Forest algorithm (use ExtraTrees instead)
  </out_of_scope>

  <core_features>
    <feature name="API Data Collection">
      Retrieve price history (data_prices), fundamental factor data (data), and universe-level data (data_universe) with automatic credit tracking, retry logic (3x exponential backoff for transient errors), and CSV/JSON export. Includes credit balance monitoring with warnings at 80% and 95% consumption thresholds.
    </feature>

    <feature name="Ranking System Management">
      Create, update, test, and rank stocks using ranking systems via the API (rank_update, rank_ranks, rank_perf). Includes 5 ready-to-use XML templates (Value, Momentum, Quality, Growth, AI Factor), XML validation checklist, and programmatic XML generation from factor configurations. All ranking systems enforce the "agent" name prefix.
    </feature>

    <feature name="Universe Management">
      Create and update custom universes via API XML. Supports Stock universes (region, market cap, liquidity filters) and ETF universes (Ticker function). Includes templates for US Large Cap, US Small Cap, Canada, and custom filtered universes.
    </feature>

    <feature name="Screen Execution & Backtesting">
      Run inline screens (screen_run), backtests (screen_backtest), and rolling backtests (screen_rolling_backtest) via API. Supports parameter sweeps with credit cost pre-calculation and batch caps (default 20 combinations). Results exported to CSV/JSON.
    </feature>

    <feature name="Strategy Creation (Browser)">
      Automate the full Strategy Wizard via browser: General tab, Rebalance tab, Universe & Ranking tab, Buy Rules tab, Sell Rules tab, Period & Restrictions tab. Supports both Stock and ETF (TAA) strategies. Includes 3 proven strategy templates: TAA (ETF momentum rotation), Small Cap Alpha (multi-factor with risk reduction), Large Cap AI Factor (ML-driven S&P 500). Uses snapshot-verify pattern with graceful degradation to manual instructions after 3 failures.
    </feature>

    <feature name="AI Factor Workflow (Browser + API)">
      Three-phase async workflow: (1) Configure — automate dataset setup, feature selection (130-180 sweet spot), preprocessing (scaling, NA handling, trim, outliers), validation method selection (Basic Holdout, Time Series CV, Rolling TS-CV, K-Fold Blocked), and model selection via browser. Includes 16 named hyperparameter presets (13 meeting types: FastFire, DeepThinker, RuleMaster, ComplianceCore, SharpShooter, RiskBalancer, BigBrain, EarlyStopper, OverfitArtist, ZenMinimalist + 3 P123 presets: Maestro, ComplianceLite, FieldScout). Algorithms: LightGBM, ExtraTrees, XGBoost. (2) Execute — hand off to P123 cloud, provide expected wait time, instruct user to return. (3) Evaluate — navigate to results via browser, screenshot lift charts, read Compare All metrics, extract key diagnostics (monotonicity, H-L spread, turnover, time resilience). Default philosophy: "Train Wide, Filter Smart."
    </feature>

    <feature name="AI Factor Predictions (API)">
      Retrieve predictions from trained AI Factor models via aifactor_predict. Supports wrapping in FRank() for percentile ranking. Includes guidance on AIFactorValidation() vs AIFactor() usage and backtest date constraints.
    </feature>

    <feature name="Factor Discovery">
      Systematic factor name resolution using doc_detail.jsp URL protocol. Curated quick-reference of ~50 most-used factors (Valuation, Quality, Growth, Momentum, Technical, Estimates). Links to full 528-page Syntax Dictionary in vault for exhaustive lookup.
    </feature>

    <feature name="Pipeline Workflows">
      Named multi-step pipelines with dependency tracking: (1) create-and-backtest — universe → ranking system → screen backtest. (2) optimize-ranking — parameter sweep across factor weights and ranking configurations. (3) full-strategy-build — universe → ranking system → strategy creation (browser) → backtest → evaluation. All pipelines include preflight confirmation showing estimated credit cost and step summary.
    </feature>

    <feature name="Continual Learning System">
      Self-improving skill through structured discovery logging. Watches for: validated factor names, browser selector changes, API behavior differences, XML quirks, strategy performance insights, credit cost corrections, hyperparameter benchmarks. Discoveries logged to learnings.md with timestamps and confidence levels. Auto-promotes to reference files after 3+ confirmations (additive only). High-confidence discoveries (e.g., confirmed factor name) promote immediately. Contradictions flagged for user review.
      Strategy DNA Fingerprinting extracts from every backtest: (1) factor exposures — derived from the ranking system configuration used (factor names, weights, rank directions), NOT from return attribution; (2) regime profile — performance during backtest's worst drawdown vs. recovery periods; (3) turnover signature — rebalance frequency and position count; (4) universe affinity — which universe ID/name was used; (5) Sharpe/Alpha/MaxDD triplet — from API response metrics (annualized_return, sharpe_ratio, max_drawdown). Builds a personalized strategy landscape map over time.
    </feature>

    <feature name="Preflight & Safety">
      All major operations require preflight confirmation: summary of actions, estimated credit cost, and user approval. Hard enforcement of "agent" prefix on all created P123 resources. Default transaction cost of 0.005/share. Credit balance monitoring with running quotaRemaining tracking. Parameter optimization capped at 20 combinations by default.
    </feature>
  </core_features>

  <api_endpoints_summary>
    NOTE: All calls are made via p123api.Client methods using the context manager pattern:
    with p123api.Client(api_id=..., api_key=...) as client: client.method(params)
    Credit costs marked "TBD" should be discovered during first use and logged via continual learning.

    <endpoint>data_prices(identifier, start, end) — Historical price data (1 credit)</endpoint>
    <endpoint>data(tickers, formulas, startDt, endDt, pitMethod, precision) — Fundamental factor data (TBD credits)</endpoint>
    <endpoint>data_universe(universe, formulas, asOfDts) — Universe-level factor data (TBD credits, requires data license)</endpoint>
    <endpoint>rank_update(xml_string) — Create/update ranking system from XML (TBD credits)</endpoint>
    <endpoint>rank_ranks(rankingSystem, universe, asOfDt) — Get stock rankings (TBD credits)</endpoint>
    <endpoint>rank_perf(rankingSystem, universe, startDt, endDt, rebalFreq) — Ranking performance test (TBD credits)</endpoint>
    <endpoint>screen_run(screen, asOfDt) — Run inline screen (2 credits)</endpoint>
    <endpoint>screen_backtest(screen, startDt, endDt, rebalFreq) — Screen backtest (5 credits)</endpoint>
    <endpoint>screen_rolling_backtest(screen, startDt, endDt, holdingPeriod, frequency) — Rolling backtest (TBD credits, estimate ~5-10)</endpoint>
    <endpoint>strategy_get(strategy_id) — Get strategy details, read-only (TBD credits)</endpoint>
    <endpoint>strategy_holdings(strategy_id) — Get strategy holdings (TBD credits)</endpoint>
    <endpoint>aifactor_predict(predictor_id, universe, asOfDt, precision, includeNames) — AI Factor predictions (TBD credits)</endpoint>
  </api_endpoints_summary>

  <implementation_steps>
    <phase number="1" title="Skill Skeleton & Core SKILL.md">
      Create directory structure. Write SKILL.md with frontmatter, decision tree, workflow entry points, and progressive disclosure links. Target: ~200 lines.
      The decision tree must route these 9 task types to the correct reference file:
        1. "data collection" (prices, factors, universe data) → api-reference.md
        2. "ranking system" (create, update, test, rank) → ranking-templates.md
        3. "universe" (create, update, filter) → ranking-templates.md
        4. "screen / backtest" (run, backtest, rolling, parameter sweep) → api-reference.md + strategy-templates.md
        5. "strategy creation" (Stock or ETF, full wizard) → browser-workflows.md + strategy-templates.md
        6. "AI Factor" (configure, train, validate, evaluate, predict) → ai-factor-guide.md + browser-workflows.md
        7. "factor lookup" (find P123 syntax name for a concept) → factor-quickref.md
        8. "pipeline" (multi-step chained workflow) → strategy-templates.md
        9. "learning review" (review discoveries, promote learnings) → learnings.md
      Data output convention: All CSV/JSON exports saved to ./p123-output/ relative to the workspace root, with naming pattern: {operation}_{timestamp}.{csv|json} (e.g., screen_backtest_20260312_143022.csv).
    </phase>

    <phase number="2" title="API Reference File">
      Write api-reference.md: all p123api endpoints with parameters, auth setup (env vars), credit cost table, error handling (retry with backoff), code examples for every operation, response format notes (snake_case), and credit monitoring patterns.
    </phase>

    <phase number="3" title="Browser Automation Workflows">
      Write browser-workflows.md: login flow (credentials via prompt), session management (timeout detection, re-auth), strategy creation wizard (Stock + ETF, all tabs), AI Factor configuration (dataset, features, preprocessing, validation, models), snapshot-verify pattern, graceful degradation (3 attempts → manual instructions), DOM health check workflow.
    </phase>

    <phase number="4" title="Ranking System & Universe Templates">
      Write ranking-templates.md: 5 XML templates (Value, Momentum, Quality, Growth, AI Factor) with complete valid XML, XML validation checklist (Name, RankType, Scope, Weight sum, StockFormula vs StockFactor), factor discovery protocol (doc_detail.jsp), universe creation patterns (Stock filters, ETF Ticker function), GUI-first with XML fallback after 2 failures.
    </phase>

    <phase number="5" title="Strategy Templates & Pipeline Workflows">
      Write strategy-templates.md: 3 proven configs (TAA with Ret1Y%Chg filter, Small Cap Alpha with FCF/Bollinger sell rules, Large Cap AI Factor with rank momentum buy rules), buy/sell rule library, position sizing guidance, 3 named pipeline definitions with dependency tracking, preflight confirmation logic with credit cost estimation.
      Parameter sweep dimensions (for optimize-ranking pipeline): factor weights (5% increments), rebalance frequency (Day/Week/4 Weeks), position count (5/10/15/20/25/30), sell rank threshold (30/50/80), and buy rank threshold (80/85/90/95).
      Graceful degradation format: When browser automation fails after 3 attempts, output a numbered manual instruction set: (1) exact URL to navigate to, (2) field-by-field values to enter, (3) buttons to click in order, (4) expected confirmation text. Pipeline pauses until user types "done".
    </phase>

    <phase number="6" title="Factor Quick Reference">
      Write factor-quickref.md: ~50 most-used factors organized by category (Valuation: PEExclXorTTM, Pr2SalesTTM, Pr2BookQ, FCFYield; Quality: ROE%TTM, ROA, FCFTTM; Growth: SalesGr%TTM, EPSExclXorGr%PYQ; Momentum: Momentum(252), Ret1Y%Chg; Technical: ATR, BBUpper, AvgDailyTot; Estimates: AvgRec, EPS revisions). Each entry: P123 syntax name, description, rank direction, common pitfalls.
    </phase>

    <phase number="7" title="AI Factor Guide & Hyperparameter Presets">
      Write ai-factor-guide.md: full ML workflow, dataset preparation, feature engineering (130-180 sweet spot), preprocessing (Rank vs Z-Score scaling, NA handling via median, 7.5% trim, outlier limits), all 4 validation methods with guidance on when to use each, all 16 hyperparameter presets with configs, 3-phase configure/execute/evaluate async pattern, evaluation diagnostics checklist (monotonicity, edge sharpness, noise, time shift, H-L spread, turnover analysis, time resilience — structural vs semantic), "Train Wide, Filter Smart" as default.
      Source hyperparameter values from the vault file: file dump/Portfolio123/Portfolio123 AI Factor Reference.md (contains all 13 meeting types with detailed configurations and the 3 P123 presets).
      This file may exceed 400 lines given 16 presets + 4 validation methods + diagnostics. Allowed up to 600 lines; use collapsible sections or split into ai-factor-guide.md (workflow + evaluation, ~300 lines) and hyperparameter-presets.md (all 16 presets, ~250 lines) if needed.
    </phase>

    <phase number="8" title="Continual Learning System">
      Write learnings.md (structured journal template with discovery types, timestamps, confidence levels, promotion status). Add learning hooks to SKILL.md (what to watch for after each operation type). Define promotion rules (3+ confirmations → auto-update, 1 high-confidence → immediate, contradiction → flag). Define auto-update targets per reference file. Implement Strategy DNA Fingerprinting schema (factor exposures, regime profile, turnover signature, universe affinity, performance triplet). Safety rails: append-only journal, additive-only reference updates, conflict detection, rollback comments.
    </phase>

    <phase number="9" title="Andreas Knowledge Base">
      Write andreas-reference.md: robustness-first philosophy, percentile ranking design rationale, ensemble design (LightGBM arrow + ExtraTrees shield role splitting), universe selection (homogeneous vs massive, death zone avoidance), training philosophy (uninterrupted 2003-2020 window, Basic Holdout, no walk-forward), OOS validation rigor (pseudo-OOS with 0.5 cents slippage, OOS Live must replicate OOS Pseudo), feature stability audit, time-aware training, live deployment checklist.
    </phase>

    <phase number="10" title="Integration Testing & Validation">
      Walk through each reference file: verify all cross-references resolve, XML templates parse with ElementTree, API code examples are syntactically correct, browser workflows reference correct MCP tool names (browser_navigate, browser_click, browser_snapshot, etc.), SKILL.md decision tree routes correctly for every task type. Verify SKILL.md stays under 500 lines. Verify total reference file sizes are reasonable for progressive disclosure.
    </phase>

    <phase number="11" title="Final Polish & Delivery">
      Add terminology glossary (consistent terms: "ranking system" not "ranker", "universe" not "watchlist", "factor" not "variable"). Remove any time-sensitive info. Verify all file paths use forward slashes. Confirm skill description triggers correctly for: "portfolio123", "P123", "ranking system", "backtest", "AI factor", "screen", "universe", "strategy". Final token budget audit across all files. Verify project-constitution.md hard boundaries are not violated by any reference file.
    </phase>
  </implementation_steps>

  <success_criteria>
    <functional>
      - All 12 API endpoints wrapped with working code examples
      - All 5 ranking system XML templates parse without errors
      - All 3 strategy templates contain valid buy/sell rule syntax
      - All 16 hyperparameter presets have complete configurations
      - Browser workflows cover login, strategy creation, AI Factor config, and evaluation
      - Pipeline workflows correctly chain dependent steps
      - Continual learning system logs discoveries and promotes to reference files
      - Factor quick-reference contains ~50 validated factor names
    </functional>
    <ux>
      - SKILL.md routes any P123 task to the correct reference file in one decision
      - Preflight confirmations are concise (action + credit cost + confirm prompt)
      - Graceful degradation provides actionable manual instructions within 30 seconds
      - Strategy DNA fingerprints produce useful recommendations after 5+ backtests
      - Credit warnings are timely (80%, 95% thresholds) and non-blocking
    </ux>
    <technical>
      - SKILL.md under 500 lines
      - Most reference files under 400 lines; ai-factor-guide.md allowed up to 600 lines (or split into two files)
      - Per-invocation context cost: ~200 lines base + ~100-300 lines for active reference file
      - All XML examples valid against P123's parser rules
      - All API code examples runnable with valid credentials
      - Learnings.md append-only with structured schema
      - No credentials stored in any skill file
    </technical>
  </success_criteria>
</project_specification>
