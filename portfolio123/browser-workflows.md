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
| Screen backtest vs. simulated strategy | Results differ — screen is buy-side-only |
| Local Python ETF model vs. P123 native ETF sim | Look-ahead bias, zero transaction costs |
| Weighted-average portfolio math vs. native book | Mathematically incorrect — use weighted return series |
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


## P123 Wizard Save Mechanism (Critical)

**CRITICAL:** `jsPort.loadPortTab()` and AJAX calls to `port_simul3.jsp` do **NOT** persist changes to the database. They only re-render the current tab. Navigating away discards all changes.

The **only** reliable save in the strategy wizard is submitting the full form to `port_sim_go.jsp` via `jsPort.run()`:

```javascript
// After setting formulas via execCommand (see CDP Formula Editing below):
jsPort.run(Date.now(), true); // true = skip naming modal
// Page navigates to port_summary.jsp on success, or shows inline error
```

After calling `jsPort.run()`, wait 8-12 seconds before checking results. A successful save+run redirects to the strategy summary page. An inline error means a formula was rejected.

## jsPort API Reference (Strategy Wizard)

The P123 wizard exposes a `jsPort` global with these key methods (validated 2026-04-13):

| Method | Purpose |
|--------|---------|
| `jsPort.run(msec, skip)` | Save + run simulation. `skip=true` skips naming modal. **This is the only real save.** |
| `jsPort.loadPortTab()` | AJAX reload current tab (re-renders only, does NOT save to DB) |
| `jsPort.filterInsert(type, name, formula)` | Add a new rule (type 0=buy, 1=sell) |
| `jsPort.filterDeleteElem(index)` | Delete rule at index WITHOUT triggering a confirm dialog |
| `jsPort.showTextEditor(...)` | Open text editor view |
| `jsPort.verifyInputs()` | Validate all formulas - returns false if any error |
| `jsPort.switchTab(tabId)` | Switch wizard tab |

Get full list: `Object.getOwnPropertyNames(jsPort).filter(k=>typeof jsPort[k]==='function')`

## CDP Formula Textarea Editing

P123 formula textareas are controlled by a JavaScript framework. Direct `.value` setters do NOT persist reliably. Use `execCommand('insertText')` instead:

```javascript
// 1. Physically focus the textarea first (cdp.mjs clickxy on the field)
// 2. Select all and insert new formula
var ta = document.querySelector('textarea[name=buyruleformula_0]');
ta.focus();
ta.select();
// 3. Build quoted strings using String.fromCharCode(34) - never rely on shell quoting
var q = String.fromCharCode(34);
var formula = 'Ticker(' + q + 'SPY,IWM,EFA,EEM,TLT,IEF' + q + ')';
document.execCommand('insertText', false, formula);
// 4. Verify before running
console.log(ta.value);
```

**Never use `cdp.mjs type` for strings with double quotes** - PowerShell strips them. Always construct quoted strings via `String.fromCharCode(34)`.

## jsPort.filterDeleteElem vs UI Delete Button

**Never click the X/delete icon on buy/sell rules via CDP.** It triggers a native `confirm()` dialog that **blocks the CDP thread** indefinitely. To safely delete a rule:

```javascript
jsPort.filterDeleteElem(0); // Delete buy rule at index 0 - no dialog
```

If a CDP session becomes blocked (all commands hang): manually click OK in Chrome's confirm dialog to unblock, then kill the Node.js process and restart `cdp.mjs list`.

## ETF Ranking System Limitation

P123's strategy wizard does **not** support inline custom ranking formulas for ETF strategies. The wizard only shows built-in ranking system options.

**Workaround options:**
1. Create a **custom Ranking System** separately (RESEARCH -> Ranking Systems -> New), then select it in the wizard dropdown
2. Best built-in proxies: **"Price Uptrend - Basic"** = short-term momentum (no ATR normalization); **"ETF Rotation - Basic"** = 12-month momentum
3. "Price Uptrend - Basic" **lacks ATR normalization** - concentrates in high-volatility ETFs during stress, worsening max drawdown vs risk-adjusted momentum

## Known platform quirks (from vault iteration notes)

- **Long backtest period reset:** Strategy wizard (`port_wiz.jsp`) may **revert** the simulation period to a **short default** (e.g. ~1 year) when **Run Simulation** is triggered, even after selecting a long start date. **Workaround:** set period to **MAX** (or desired range) again immediately before run; or verify metrics via **API** (`screen_backtest` / strategy endpoints) which does not hit this UI bug.
- **Ranking wizard lag:** “Edit Details” / selection UI may **timeout**—use **simulation dialog** for naming, or **raw XML** for ranking edits (see GUI-First, XML Fallback).
- **Selenium / browser automation:** Prefer **60s** timeouts, **explicit wait** after navigation (AJAX), and **raw XML** when “Add Node” spins indefinitely.
- **confirm() dialog blocks CDP:** Native `confirm()` dialogs (triggered by delete icons) block CDP thread completely. All commands hang until dismissed manually in Chrome. Use `jsPort.filterDeleteElem(index)` to avoid triggering them.
- **`jsPort.saveChanges()` is broken:** Throws Internal Server Error. Use `jsPort.run(Date.now(), true)` instead.
- **`loadPortTab()` is not a save:** Re-renders the tab but does NOT write to the database. Only `jsPort.run()` saves.

## Naming Convention

All created items: `agent_[descriptive_name]` — ranking systems, strategies, universes, screens, AI factors, books.
