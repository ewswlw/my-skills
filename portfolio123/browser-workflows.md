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

> **Using Cursor IDE browser tools?** See [Simulated Strategy Creation (Full Browser Workflow)](#cursor-ide-browser-mcp-automation--p123-specific-patterns) for MCP-specific patterns, stale-ref workarounds, and JS injection recipes.

**Path:** RESEARCH → Simulated Strategies → New → Stock (or ETF)

**Tabs in order:**
1. **General** (`st=0`) — Name (agent_*), Type (Stock/ETF), Rebalance (Every 4 Weeks)
2. **Rebalance** (`st=1`) — Position sizing, number of positions
3. **Universe & Ranking** (`st=2`) — Universe, Ranking system
4. **Buy Rules** (`st=3`) — Formula rules (e.g., Rank > 85, Close(0) > 1.2)
5. **Sell Rules** (`st=4`) — Formula rules (e.g., RankPos > 50, gainpct - benchpct < -20)
6. **Period & Restrictions** (`st=7`) — Start/End or MAX, transaction cost 0.005
7. **Review** (`st=8`) — Run Simulation

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

## Cursor IDE Browser (MCP) Automation — P123-Specific Patterns

The Cursor IDE browser tools (`browser_navigate`, `browser_click`, `browser_fill`, `browser_snapshot`, `browser_take_screenshot`, `browser_mouse_click_xy`, `browser_wait_for`, `browser_press_key`, `browser_scroll`, `browser_hover`) interact with P123 differently than CDP/Selenium. P123's dynamic DOM and custom UI components cause persistent stale element references and click interceptions. The patterns below are battle-tested solutions.

### The Core Problem: Stale Element References

P123 re-renders DOM elements aggressively. Any `browser_click` or `browser_fill` using a ref from `browser_snapshot` may fail with "Stale element reference" because the page re-rendered between the snapshot and the action. This is the **single most common failure mode** on P123.

**Mitigation hierarchy (try in order):**

1. **Immediate action after snapshot** — Take snapshot, then immediately use the ref in the next tool call. Do not insert other browser operations between snapshot and action.
2. **Coordinate-based clicks** — Use `browser_take_screenshot` followed immediately by `browser_mouse_click_xy` with coordinates read from the screenshot. Useful for stable, visible elements.
3. **JavaScript injection** — The nuclear option that always works. Use `browser_navigate` with a `javascript:void(...)` URL to directly manipulate the DOM. This bypasses all ref staleness issues.

### JavaScript Injection Pattern (Most Reliable)

When `browser_click` or `browser_fill` fail repeatedly, inject JavaScript via `browser_navigate` with `javascript:void(...)`. This bypasses all ref staleness.

**Core patterns:**

```javascript
// Pattern 1: Click hidden/stale element by text content
javascript:void((function(){
  var els=document.querySelectorAll('li,a,button');
  for(var i=0;i<els.length;i++){
    if(els[i].textContent.trim()==='TARGET_TEXT'){els[i].click();break;}
  }
})())

// Pattern 2: Set textarea/input value
javascript:void(document.querySelector('textarea').value='NEW_CONTENT')

// Pattern 3: Click dialog primary button
javascript:void(document.querySelector('button.btn-primary').click())

// Pattern 4: Extract element attribute for debugging (writes to document.title)
javascript:void(document.title=document.querySelector('a[data-id]').getAttribute('data-id'))
```

See subsections below for P123-specific applications of each pattern (Save As, portId extraction, universe OK, etc.).

### Ranking System: Raw XML Editor via Browser

**Path:** Navigate to ranking system → Settings → Raw XML editor

**Finding the ranking system ID:** Navigate to any ranking system page — the ID is in the URL (e.g., `/app/ranking-system/541832/editor` → ID is `541832`). Alternatively, list rankings via the RESEARCH → Ranking Systems opener and extract `data-id` attributes.

**Steps:**
1. Navigate to `https://www.portfolio123.com/app/ranking-system/{id}/editor-raw`
2. `browser_snapshot` to get textarea ref
3. **Do NOT use `browser_fill` or `browser_type`** on the textarea — it triggers stale element errors due to P123's DOM re-rendering
4. Use JavaScript injection to set the value: `javascript:void(document.querySelector('textarea').value='NEW_XML')`
5. Save via the Save menu — if "Save" link is visible, first try `browser_click`. If it fails, use JS injection

**"Save As" for new ranking from existing:**
The "Save As" option is hidden inside a dropdown menu. Direct `browser_click` on the `<li>` fails because it has zero dimensions.

```javascript
// Trigger Save As menu item (hidden in dropdown)
javascript:void((function(){
  var items=document.querySelectorAll('li');
  for(var i=0;i<items.length;i++){
    if(items[i].textContent.trim()==='Save As'){
      items[i].click();
      break;
    }
  }
})())
```

After "Save As" triggers a dialog, fill the name field with `browser_fill` and click OK/Save.

### Simulated Strategy Creation (Full Browser Workflow)

**Entry point:** `https://www.portfolio123.com/port_wiz.jsp` (wizard) or RESEARCH → Simulated Strategies → New → Stock

**Wizard tabs (in order, `st=` parameter):**
| Tab | st= | Key Fields |
|-----|-----|------------|
| General | 0 | Name, Currency, Starting Capital, Commission, Slippage, Transaction Type |
| Rebalance | 1 | Sizing Method, Ideal Positions, Rebalance Frequency |
| Universe & Ranking | 2 | Universe dropdown, Benchmark, Ranking System |
| Buy | 3 | Buy rule formulas |
| Sell | 4 | Sell rule formulas |
| Stop Loss | 5 | Strategy |
| Hedge | 6 | Market timing |
| Period & Restrictions | 7 | Date range textbox, Exposure List, Restrictions |
| Review | 8 | Full config summary + Run Simulation button |

**Direct tab navigation:** `https://www.portfolio123.com/port_wiz.jsp?st=N`

#### Universe Selection Dialog

Clicking the Universe field opens a "Choose Universe" modal dialog. This modal **intercepts** all clicks to underlying page elements. Inside the modal:

1. The universe dropdown may need `browser_mouse_click_xy` (coordinate-based) if `browser_click` returns stale refs
2. After selecting a universe, the "OK" button frequently goes stale — use JS injection:
```javascript
javascript:void(document.querySelector('button.btn-primary,button[class*=primary]').click())
```

#### Period & Restrictions Date Range

The date range field (`st=7`) is a single textbox accepting `MM/DD/YYYY - MM/DD/YYYY` format. Use `browser_fill` — this field works reliably with standard fill.

**Critical for AI Factor strategies:** The simulation period MUST fall within the AI Factor prediction window. Check the prediction coverage dates before setting the period. Error message if exceeded: *"No predictions are available on [date]. Saved predictions cover [start] to [end] every week."*

#### Running the Simulation

From the Review tab (`st=8`):
1. Click "Run Simulation" (or "Re-Run Simulation" for existing strategies)
2. If creating a new strategy, a "New Simulated Strategy Properties" dialog appears — fill the Name field, then click Save
3. The Save button shows "Please wait..." while processing — wait 10-15 seconds
4. The page redirects to `port_summary.jsp?portid=ID` on success

**If "Run Simulation" button goes stale:**
```javascript
javascript:void(document.querySelector('a[href*=run],a.btn-primary,#SimulButton').click())
```

### Strategy Summary Page & Navigation

**Direct URL:** `https://www.portfolio123.com/port_summary.jsp?portid={PORTID}`

**Finding the PORTID:** The strategy opener sidebar (`/app/opener/ptf`) lists strategies as `<a>` elements with `data-id` attributes in format `item_SIM_{EXTERNAL_ID}_{CATEGORY_ID}_{PORTID}`. The PORTID is the **last number** in the data-id string.

```javascript
// Extract data-id and all attributes from a strategy link
javascript:void((function(){
  var links=document.querySelectorAll('a');
  for(var i=0;i<links.length;i++){
    if(links[i].textContent.trim()==='STRATEGY_NAME'){
      document.title='ATTRS:'+links[i].getAttribute('data-id');
      break;
    }
  }
})())
```

**data-id format:** `item_SIM_{externalId}_{categoryId}_{portId}`
- Use the **last number** (`portId`) for `port_summary.jsp?portid=`
- The first number (`externalId`) returns "Access Restricted" on `port_summary.jsp`

**Strategy opener sidebar behavior:**
- Links use `href="#"` with JavaScript click handlers
- Single-click selects the item in the sidebar but does NOT open it in the main content area
- Double-click (via `browser_mouse_click_xy` with `double_click: true`) also does not reliably open the strategy
- **Best approach:** Extract the portId from `data-id` and navigate directly to `port_summary.jsp?portid={portId}`

### Re-Running a Simulation (Existing Strategy)

1. Navigate to `port_summary.jsp?portid={ID}`
2. Click the "Re-Run" tab
3. The page loads the wizard at `port_wiz.jsp?st=8` (Review tab) with a "Re-Run Simulation" button
4. Make any parameter changes (e.g., fix the date range on the Period tab)
5. Click "Re-Run Simulation" — the button is `<a id="SimulButton">`
6. Wait for the simulation to complete (redirects to summary page)

### Edit-and-Re-Run Loop — Battle-Tested Sequence (2026-04-16)

The single most reliable sequence for "tweak a rule, re-run, read metrics" on an existing strategy. Use this verbatim — every step earned its place from a failure in the prior iteration.

```
1. browser_navigate → port_summary.jsp?portid={ID}      # confirms strategy exists
2. browser_navigate → javascript:void(window.location.href='/port_wiz.jsp?st=8&portid={ID}')
                                                         # MUST include &portid={ID} or wizard
                                                         # opens with no portfolio context
3. browser_click → desired tab (Buy / Sell / Rebalance / Period)
4. browser_wait_for time:2                              # Svelte render
5. browser_snapshot                                      # get fresh refs (Buy/Sell only)
6. browser_fill on form fields                           # see "Buy/Sell Rule Textareas" below
7. browser_navigate → javascript:void(jsPort.generateBy('SimulButton'))
                                                         # the only reliable sim trigger
8. browser_wait_for time:60                              # typical 8yr daily sim
9. browser_navigate → port_summary.jsp?portid={ID}
10. browser_take_screenshot fullPage:true                # ONLY way to read metrics
```

**Why each step matters:**

- **Step 2 — `&portid={ID}` is mandatory.** Navigating to `port_wiz.jsp?st=8` alone renders only chrome with no form fields. The wizard's `st=` parameter is sticky to the last visited tab, not literal — you cannot rely on it without the portid.
- **Step 7 — `jsPort.generateBy('SimulButton')` over clicking.** Clicking the "Re-Run Simulation" link gets stale/intercepted ~50% of the time on Svelte re-renders. The JS call works every time. Note: the existing `jsPort.run(Date.now(), true)` documented above is for the wizard form-submit flow; `generateBy('SimulButton')` is the correct call when re-running an already-saved strategy.
- **Step 10 — fullPage screenshot, not snapshot.** `port_summary.jsp` renders metrics (CAGR/Sharpe/DD) inside a table the snapshot tree does not traverse. You will get back nothing useful from `browser_snapshot` for results.

### Buy/Sell Rule Textareas — Exact Ref Pattern

Buy and Sell tabs render rules as alternating label/textarea pairs:

| Element | Role |
|---------|------|
| `e175` | Buy1 label |
| `e176` | Buy1 formula textarea |
| `e177` | Buy2 label |
| `e178` | Buy2 formula textarea |

Use `browser_fill` directly on the textarea ref. **Do not** use JavaScript injection here — it triggers the "Quick Rules" popup. **To clear a rule, fill with `" "` (single space)** — empty string sometimes leaves the prior value in place.

### Form Field Locations (Don't Guess the Tab)

| What you want to set | Tab that owns it |
|---------------------|------------------|
| Position count / sizing method | **Rebalance** (NOT General) |
| Buy / Sell rule formulas | **Buy** / **Sell** — fields render only after clicking the tab + waiting 2s |
| Backtest period | **Period & Restrictions** |
| Universe / Ranking system | **Universe & Ranking** |

### `#bench` Beats `$SPY` in Buy/Sell Rules

Even though `$SPY` is documented as a valid series alias, it errors with `Formula '$SPY' not found` inside Buy/Sell rule formulas on simulated strategies. Use `#bench` instead when the strategy benchmark is set to SPY (it resolves to whatever the strategy's configured benchmark is).

```
# Works:
Close(0,#bench) > SMA(200,0,#bench)

# Fails:
Close(0,$SPY) > SMA(200,0,$SPY)
```

Lowercase `#bench` is fine. This pattern is the canonical way to add SMA-based market timing hedges.

### Sentinel Value: -100000000

If `port_summary.jsp` shows "Number of Positions: -100000000" (or similar absurd negatives on other metrics), the sim has **not yet run or errored silently**. Do not bother reading other metrics — re-trigger the sim via step 7 above. This is more reliable than parsing for explicit error text, which P123 sometimes suppresses.

### P123 URL Quick Reference

| Purpose | URL Pattern |
|---------|-------------|
| Strategy wizard | `port_wiz.jsp?st={0-8}` |
| Strategy summary | `port_summary.jsp?portid={PORTID}` |
| Simulation runner | `port_sim_go.jsp?{timestamp}` |
| Strategy opener | `app/opener/ptf` |
| Ranking raw editor | `app/ranking-system/{id}/editor-raw` |
| Ranking performance | `rank_perf.jsp?rankid={id}` |
| AI Factor validation | `sv/aiFactor/{id}/validation` |

### Common Error Patterns & Solutions

| Error | Cause | Solution |
|-------|-------|----------|
| "Stale element reference" | P123 DOM re-rendered between snapshot and action | Re-snapshot + immediate action, or use JS injection |
| "Click target intercepted" | Modal dialog is blocking underlying elements | Interact with the modal first, or dismiss it |
| "Element not visible (zero dimensions)" | Hidden menu item or collapsed dropdown | Use JS injection to click by text content |
| "Access Restricted" on `port_summary.jsp` | Wrong ID — used externalId instead of portId | Extract portId (last number) from `data-id` attribute |
| "No predictions available on [date]" | Simulation period extends beyond AI Factor prediction window | Adjust period to fall within prediction dates (check `learnings.md` LEARN-20260407-002) |
| Blank page on navigation | URL pattern incorrect for P123's SPA router | Try legacy JSP URLs (`port_summary.jsp`, `rank_perf.jsp`) instead of SPA routes |
| Wizard renders chrome only, no form fields | Navigated to `port_wiz.jsp?st=N` without `&portid={ID}` | Always append `&portid={ID}` when re-entering the wizard for an existing strategy |
| `Formula '$SPY' not found` in Buy/Sell rule | `$SPY` series alias not recognized inside rule formulas | Use `#bench` (resolves to strategy benchmark) instead of `$SPY` |
| Re-Run tab navigates but no sim runs | Clicking Re-Run only loads wizard at `st=8`; doesn't execute | Trigger via `javascript:void(jsPort.generateBy('SimulButton'))` |
| Metrics missing from snapshot of summary page | `port_summary.jsp` metrics live in tables `browser_snapshot` doesn't traverse | Use `browser_take_screenshot` with `fullPage: true` |
| "Quick Rules" popup appears when editing rule | Used JS injection to set buy/sell textarea value | Use `browser_fill` directly on the textarea ref instead |
| "Number of Positions: -100000000" sentinel | Sim hasn't run yet or errored silently | Re-trigger sim via `jsPort.generateBy('SimulButton')` — don't trust other metrics on the page |

## Naming Convention

All created items: `agent_[descriptive_name]` — ranking systems, strategies, universes, screens, AI factors, books.
