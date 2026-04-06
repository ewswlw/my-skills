# Portfolio123 Browser Automation Workflows

Login, strategy creation, AI Factor configuration, snapshot-verify pattern, and graceful degradation.

## Cursor IDE Browser Tools

- `browser_navigate` — Navigate to URL
- `browser_snapshot` — Capture page state (use before every interaction)
- `browser_click` — Click element
- `browser_type` — Type text
- `browser_select_option` — Select dropdown
- `browser_wait_for` — Wait for text, time, or textGone
- `browser_fill_form` — Fill multiple fields
- `browser_take_screenshot` — Capture screenshot

**Rule:** browser_snapshot before interactions; browser_wait_for after navigation/AJAX.

## Element Selection (Priority Order)

1. **By text content** — Most reliable. "Run Simulation", "Save", "Sign In"
2. By CSS selector/ref
3. By form field name
4. Avoid: XPath, position-based, hardcoded IDs

## Login Workflow

1. Navigate to https://www.portfolio123.com (after login, dashboard is at https://www.portfolio123.com/app/dashboard)
2. Wait for page load
3. Locate and click "Sign In" (by text)
4. Enter credentials (**prompt user** or use browser-saved password — **never** store username/password in this skill’s `.env` or markdown; see `project-constitution.md` § Web login)
5. Submit login
6. Verify: user account indicator, nav menu (MANAGE, RESEARCH, CHARTS, MODELS, RESOURCES)

**Session timeout:** "Sign In" reappears, redirect to login, nav menu gone → re-run login.

## Snapshot-Verify Pattern

Every action: **snapshot → act → wait → snapshot → verify**. If verify fails, retry with alternative selector before escalating.

## Strategy Creation Wizard (Stock or ETF)

**Path:** RESEARCH → Simulated Strategies → New → Stock (or ETF)

**Tabs in order:**
1. **General** — Name (agent_*), Type (Stock/ETF), Rebalance (Every 4 Weeks)
2. **Rebalance** — Position sizing, number of positions
3. **Universe & Ranking** — Universe, Ranking system
4. **Buy Rules** — Formula rules (e.g., Rank > 85, Close(0) > 1.2)
5. **Sell Rules** — Formula rules (e.g., RankPos > 50, gainpct - benchpct < -20)
6. **Period & Restrictions** — Start/End or MAX, transaction cost 0.005
7. **Review** — Run Simulation

**ETF (TAA):** Use Ticker("SPY,EFA,AGG") for universe, "Trend Measurement" ranking, Buy Rule: Ret1Y%Chg > 0.

## AI Factor Configuration (Phase 1 — Configure Only)

**Path:** RESEARCH → AI Factors → New (or existing)

**Steps to automate:**
1. Target variable, training universe, benchmark, currency
2. Dataset period, feature selection (130-180 features)
3. Preprocessing: Scaling (Rank or Z-Score), NA handling (median), Trim 7.5%, Outlier limit
4. Validation method: Basic Holdout, Time Series CV, Rolling TS-CV, or K-Fold Blocked
5. Model selection: LightGBM, ExtraTrees, XGBoost + preset (Maestro, etc.)
6. Enable "Save Validation Predictions"
7. Click Run Validation

**Do NOT hold browser open during training.** Provide expected wait time, instruct user to return when done.

## AI Factor Evaluation (Phase 3 — After User Returns)

1. Navigate to AI Factor → Validation → Models
2. Locate best model, click fx button for AIFactorValidation formula
3. Screenshot lift chart
4. Read Compare All table (quantile returns, H-L spread, turnover)
5. Extract: monotonicity, edge sharpness, time resilience (First Half vs Second Half)

## Strategy Book Validation Workflow

All Strategy Book performance claims MUST be validated on the native P123 platform. This is the Tier 1 (Gold) validation gate — see SKILL.md Validation Hierarchy.

**Path:** RESEARCH → Books → Simulated Books → New → Simulated

**Steps:**

1. **Create each component strategy** as a native P123 Simulated Strategy first (not just a screen)
2. **Run each component's simulation** individually and record native CAGR, Sharpe, Max DD
3. **Create the Strategy Book** via RESEARCH → Books → New → Simulated
4. **Add Assets:** Click "Add Existing Model" → select each component strategy
5. **Set Rebalance:** Configure weights (Fixed Weight or Relative Weight) and rebalance frequency
6. **Set Period:** Use MAX or specify start/end dates
7. **Run Simulation:** Click "Run Simulation" (may take several minutes for weekly strategies)
8. **Record results:** Capture CAGR, Sharpe, Max DD, Correlation from the native book summary
9. **Compare to estimates:** If native results differ from API/local estimates by >10%, report discrepancy to user with both sets of numbers. Native results are authoritative.

**Known discrepancy sources (validated 2026-04-05):**

| Source of Error | Typical Impact |
|---|---|
| Screen backtest vs. simulated strategy | CAGR overstated 30–40%, Sharpe overstated 50%+ |
| Local Python ETF model vs. P123 native ETF sim | CAGR overstated 100–200% |
| Weighted-average portfolio math vs. native book | Sharpe overstated 50–90% |
| Cross-engine correlation artifacts | Diversification bonus inflated |

## GUI-First, XML Fallback

For ranking systems: Try GUI first. After **2 failures** (timeout, Add Node spinner), switch to raw XML editor.

**Raw editor access:** Click "raw editor (no ajax)" link on ranking system page.

## Graceful Degradation (3 Attempts)

When browser automation fails 3 times, output:
1. Exact URL to navigate to
2. Field-by-field values to enter
3. Buttons to click in order
4. Expected confirmation text

Pipeline pauses until user types `done`.

## DOM Health Check

Periodically verify key pages load: Login, RESEARCH, Ranking Systems, Simulated Strategies, Books. If expected elements missing, flag possible P123 UI change.

## Known platform quirks (from vault iteration notes)

- **Long backtest period reset:** Strategy wizard (`port_wiz.jsp`) may **revert** the simulation period to a **short default** (e.g. ~1 year) when **Run Simulation** is triggered, even after selecting a long start date. **Workaround:** set period to **MAX** (or desired range) again immediately before run; or verify metrics via **API** (`screen_backtest` / strategy endpoints) which does not hit this UI bug.
- **Ranking wizard lag:** “Edit Details” / selection UI may **timeout**—use **simulation dialog** for naming, or **raw XML** for ranking edits (see GUI-First, XML Fallback).
- **Selenium / browser automation:** Prefer **60s** timeouts, **explicit wait** after navigation (AJAX), and **raw XML** when “Add Node” spins indefinitely.

## Naming Convention

All created items: `agent_[descriptive_name]` — ranking systems, strategies, universes, screens, AI factors, books.
