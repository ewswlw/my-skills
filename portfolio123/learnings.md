# Portfolio123 Skill — Continual Learning Journal

Structured discoveries from execution. Append-only. Promote to reference files after 3+ confirmations (or 1 high-confidence).

## Schema (per entry)

```
---
id: LEARN-YYYYMMDD-NNN
type: factor|browser_selector|api_behavior|xml_quirk|strategy_insight|credit_cost|hyperparameter
confidence: high|medium|low
confirmations: 0
promoted: false
---
**Context:** [What operation was running]
**Discovery:** [What worked or failed]
**Action:** [Add to factor-quickref | Update browser-workflows | etc.]
```

## Promotion Rules

- **3+ confirmations** → Auto-promote to target reference file (additive only)
- **1 high-confidence** (e.g., validated factor name) → Promote immediately
- **Contradiction** (new learning conflicts existing) → Flag for user review, do not auto-update

## Auto-Update Targets

| Discovery Type | Target File |
|----------------|-------------|
| factor | factor-quickref.md |
| browser_selector | browser-workflows.md |
| api_behavior, credit_cost | api-reference.md |
| xml_quirk | ranking-templates.md |
| strategy_insight | strategy-templates.md, case-studies.md, strategy-validation.md |
| hyperparameter | ai-factor-guide.md |

## Strategy DNA Fingerprinting Schema

Extract from every backtest, append to this file:

```
---
dna_id: DNA-YYYYMMDD-NNN
ranking_config: [factor names, weights, rank directions]
universe: [name or ID]
rebal_freq: Every 4 Weeks
positions: 20
sharpe: X.XX
annualized_return: X.X%
max_drawdown: -X.X%
regime_notes: [if split analysis available]
---
```

Use for personalized recommendations after 5+ fingerprints.

## Discoveries (append below)

<!-- New entries go here. Do not delete. -->

---
id: LEARN-20260317-001
type: hyperparameter
confidence: high
confirmations: 1
promoted: true
source: Andreas Himmelreich Substack #33 — "Why Your High IQ Won't Help You in Markets"
---
**Context:** AI Factor hyperparameter robustness testing
**Discovery:** ALL hyperparameter presets must produce positive lift — not just the top 3 or majority. If a signal only works under one configuration, it is fragile by definition. Real signals survive hyperparameter variance.
**Action:** Promoted to ai-factor-guide.md (All-Must-Perform Rule section)

---
id: LEARN-20260317-002
type: hyperparameter
confidence: high
confirmations: 1
promoted: true
source: Andreas Himmelreich Substack #33
---
**Context:** AI Factor outlier / preprocessing configuration
**Discovery:** Default outlier cap should be **5 sigma** (not the common 2.5 sigma). Test up to 10 sigma. Clipping at 2.5 sigma collapses signal gradient — model loses ability to distinguish "strong" from "extreme." Fat tails carry real signal.
**Action:** Promoted to ai-factor-guide.md (Preprocessing section) and andreas-reference.md (Outlier Limit Philosophy)

---
id: LEARN-20260317-003
type: strategy_insight
confidence: high
confirmations: 1
promoted: true
source: Andreas Himmelreich Substack #33
---
**Context:** Full AI Factor deployment lifecycle
**Discovery:** The workflow has 6 phases, not 3: Probe (train once 2003–2020.06) → Sense (15+ preset robustness test) → Respond (retrain exact same setup) → Verify (5-year pseudo-OOS) → Deploy (go live) → Confirm (OOS Live tracks OOS Pseudo). Each gate is binary: pass or kill and restart.
**Action:** Promoted to andreas-reference.md (Full 6-Phase Workflow section)

---
id: LEARN-20260317-004
type: strategy_insight
confidence: high
confirmations: 1
promoted: true
source: Andreas Himmelreich Substack #33
---
**Context:** Live model monitoring / retirement decision
**Discovery:** Model retirement rule — run until OOS Live stops tracking OOS Pseudo. Monthly check: market up → strategy goes up harder; market down → strategy goes down less. No calendar, no committee, no "feeling." The market decides.
**Action:** Promoted to andreas-reference.md (OOS Health Check section)

---
id: LEARN-20260317-005
type: hyperparameter
confidence: high
confirmations: 1
promoted: true
source: AI-Driven Quant Investment Strategies Substack #34 — "Visualizing the Learning Logic #3: LightGBM (3/4)"
---
**Context:** LightGBM internals and overfitting risk in stock data
**Discovery:** LightGBM uses histogram binning (~255 bins per feature) for fast split search. Overfitting manifests as learning past noise as "laws" — when conditions don't repeat, produces huge directional misses. Key anti-overfitting hyperparameters: lower learning_rate + more trees, min_data_in_leaf (extremely important for stocks), constrain num_leaves/max_depth, apply feature_fraction/bagging_fraction, use time-series validation + early stopping.
**Action:** Promoted to ai-factor-guide.md (LightGBM Learning Logic, Overfitting Risk, Anti-Overfitting Hyperparameters sections)

---
id: LEARN-20260317-006
type: strategy_insight
confidence: high
confirmations: 1
promoted: true
source: AI-Driven Quant Investment Strategies Substack #34
---
**Context:** Choosing between ExtraTrees and LightGBM
**Discovery:** Default to ExtraTrees for baseline/conservative use (stable, easy to explain). Upgrade to LightGBM only when features have genuine predictive power AND regularization is applied. For stock-ranking strategies (score 500 stocks, buy top N), evaluate by hit rate in top X% — not just regression error — to better expose overfitting risk.
**Action:** Promoted to ai-factor-guide.md (ExtraTrees vs. LightGBM Decision Guideline)

---
id: LEARN-20260323-001
type: api_behavior
confidence: high
confirmations: 1
promoted: true
source: Skill sync — Portfolio123 API Guide + vault Notes
---
**Context:** Comparing UI simulation to API backtest / live workflow
**Discovery:** **UI rebalancing** behaves as **partial / if-needed** (lower turnover, positions persist). **API**-driven and many scripted flows imply **full refresh** to model ranks unless coded otherwise—**higher turnover**. Momentum strategies are especially sensitive; numbers are not interchangeable without checking semantics.
**Action:** Promoted to api-reference.md (UI vs Platform — Rebalancing Semantics)

---
id: LEARN-20260323-002
type: strategy_insight
confidence: high
confirmations: 1
promoted: true
source: Skill sync — Systvest / vault Resources synthesis
---
**Context:** Screen backtest vs portfolio simulation disagreement
**Discovery:** Differences often come from **where slippage applies** (reconstitution vs ongoing weight maintenance) and **rebalance economics**, not necessarily a “bug.” Use simulation **turnover** as a sanity check on costs.
**Action:** Promoted to strategy-validation.md

---
id: LEARN-20260323-003
type: factor
confidence: high
confirmations: 1
promoted: true
source: Vault Portfolio123 Notes — formula trials
---
**Context:** Ranking / screen formulas
**Discovery:** Names such as `Prc2FCFY`, `#PE`, `Prc2Earn`, `ROE`, `ROA` **failed** in some ranking contexts; verified alternatives include `EPSExclXorGr%TTM`, `SalesGr%TTM`, `Momentum(20)`, `Ret1Y%Chg`. Always validate with **doc_detail.jsp**—do not assume doc labels equal evaluable names.
**Action:** Cross-ref api-reference.md Common Pitfalls; factor-quickref

---
id: LEARN-20260323-004
type: browser_selector
confidence: medium
confirmations: 1
promoted: true
source: Vault Portfolio123 Notes
---
**Context:** Strategy wizard long backtest
**Discovery:** UI may reset backtest window to a short default on Run Simulation; API bypasses.
**Action:** Promoted to browser-workflows.md (Known platform quirks)

---
id: LEARN-20260405-001
type: api_behavior
confidence: high
confirmations: 1
promoted: true
source: Strategy Book experiment loop — 2026-04-05
---
**Context:** Strategy Book optimization loop using screen_backtest API + local Python ETF model
**Discovery:** `screen_backtest` is a BUY-SIDE-ONLY backtest. It does NOT include sell rules, position-level execution, cash drag, or realistic slippage. It overstated CAGR by 40% (32.79% vs 23.43%) and Sharpe by 52% (1.37 vs 0.90) compared to the same strategy run as a native P123 Simulated Strategy. Max drawdown was understated by 25pp (-40% vs -65%). NEVER treat screen_backtest results as equivalent to a full strategy simulation.
**Action:** Added critical warning to api-reference.md. Added Validation Hierarchy to SKILL.md. Added Core Rules 8-11.

---
id: LEARN-20260405-002
type: strategy_insight
confidence: high
confirmations: 1
promoted: true
source: Strategy Book experiment loop — 2026-04-05
---
**Context:** ETF momentum sleeve computed locally in Python vs P123 native ETF simulation
**Discovery:** A custom Python momentum rotation model (12-month momentum + SMA market timing) produced ~23% CAGR on SPY/TLT/GLD. The same 3-ETF universe with P123's best native ranking system (ETF Rotation - Basic) produced only 10.82% CAGR. The local model has implicit look-ahead bias (month-end resampling), zero transaction costs on rotation, and perfect execution timing. NEVER use a local Python backtester as a substitute for P123's native simulation engine.
**Action:** Added guardrail to SKILL.md Core Rule 9. Added warning to strategy-templates.md.

---
id: LEARN-20260405-003
type: strategy_insight
confidence: high
confirmations: 1
promoted: true
source: Strategy Book experiment loop — 2026-04-05
---
**Context:** Portfolio combination math in evaluate.py
**Discovery:** Weighted-average CAGR (`sum(w * cagr)`) overestimates the true portfolio CAGR. Weighted-average max drawdown is meaningless (drawdowns can coincide or offset). Sharpe computed from estimated portfolio vol using average pairwise correlation is unreliable. Correct approach: compute weighted portfolio return series first, then derive all metrics from the combined series.
**Action:** Added Core Rule 11 to SKILL.md. Added validation blockquote to strategy-templates.md.

---
id: LEARN-20260405-004
type: api_behavior
confidence: high
confirmations: 1
promoted: true
source: Strategy Book experiment loop — 2026-04-05
---
**Context:** screen_backtest API parameter format
**Discovery:** The `screen_backtest` endpoint accepts EITHER a nested screen object (`{'type':'stock','universe':'nasdaq100'}`) OR an integer screen ID directly. The existing api-reference.md only documented the nested object form. Using a screen ID is more reliable for backtesting existing user screens. Also: `startDt` is clamped to ~2006-01-01 for Standard membership — earlier dates are silently ignored.
**Action:** Added screen ID integer form and membership date limits to api-reference.md.

---
id: LEARN-20260405-005
type: strategy_insight
confidence: high
confirmations: 1
promoted: true
source: Strategy Book experiment loop — 2026-04-05
---
**Context:** Correlation calculation between screen backtest returns and local ETF model returns
**Discovery:** Near-zero pairwise correlation (0.017) between screen backtest cumulative returns and locally-computed ETF returns was an artifact of: (a) different data sources, (b) different rebalancing frequencies embedded in the return streams, (c) temporal misalignment. This inflated the diversification bonus and made the composite metric misleadingly high. Correlation should only be computed between return series from the SAME simulation engine at the SAME frequency.
**Action:** Added warning to strategy-templates.md validation blockquote.

---
id: LEARN-20260405-006
type: strategy_insight
confidence: high
confirmations: 1
promoted: true
source: Strategy Book experiment loop — 2026-04-05
---
**Context:** Full Strategy Book experiment loop (14 experiments)
**Discovery:** The entire experiment loop optimized against a synthetic composite metric combining incompatible data sources. The loop declared victory (CAGR 26.26%, Sharpe 2.00) but the native P123 book showed 18.68% CAGR and 1.05 Sharpe — neither target was met. MANDATORY RULE: Any Strategy Book configuration MUST be validated via native P123 Strategy Book simulation (browser automation) before being declared as meeting targets. API screen backtests and local models are acceptable for rapid iteration/screening only, never for final validation.
**Action:** Added Pipeline 4 to strategy-templates.md. Added Strategy Book Validation Workflow to browser-workflows.md. Added Core Rule 10 to SKILL.md.

---
id: LEARN-20260407-001
type: browser_selector
confidence: high
confirmations: 1
promoted: true
source: AI Factor → Ranking System pipeline — 2026-04-07
---
**Context:** Connecting a trained AI Factor model to a ranking system for backtesting
**Discovery:** `AIFactor()` and `AIFactorValidation()` are NOT interchangeable in ranking system formulas:
- `AIFactor("ai_factor_name", "predictor_name")` → live scoring only. **Hard 5-year backtest limit.** Will fail with "AIFactor() can only be used up to 5 years in the past" for any deeper backtest.
- `AIFactorValidation("ai_factor_name", "model_name")` → uses saved validation predictions. **No backtest depth limit.** Required for any Performance tab backtest beyond 5 years.
- The model name string in `AIFactorValidation()` is the **model display name** (e.g., `"lightgbm slow 2"`), NOT the predictor slug. Get the exact string from the Validation → Models tab.
- Both strings are **case-sensitive**. Copy from the platform UI — do not type from memory.
**Action:** Promoted to ai-factor-guide.md (AIFactorValidation vs AIFactor section — expanded)

---
id: LEARN-20260407-002
type: browser_selector
confidence: high
confirmations: 1
promoted: true
source: AI Factor → Ranking System pipeline — 2026-04-07
---
**Context:** Validation method selection and prediction date coverage
**Discovery:** The validation method chosen for the AI Factor model directly controls how much historical backtest you can run on the ranking system:

| Validation Method | Prediction Window | Max Backtest Depth |
|---|---|---|
| Basic Holdout | Last N months only (holdout period only) | ~1–2 years |
| Time Series CV | Multiple expanding windows | ~3–5 years |
| Rolling Time Series CV | All fold holdout windows combined | ~5–10 years |
| K-Fold Blocked | No temporal structure | Not recommended for backtests |

- With **Basic Holdout** (default): 13-year training + 12-month holdout → predictions only cover the final 12 months (e.g., 12/28/2024–12/27/2025). Running a 2Y or longer backtest will fail with: *"No predictions are available on [date]. Saved predictions cover [start] to [end] every week."*
- With **Rolling Time Series CV** (4 folds, 5-year train, 27-month holdout): generates ~9 years of predictions (approximately 2016–2025 for a dataset ending 2025-12-27).
- **Critical:** Choose your validation method BEFORE training if you need long backtests. Changing it after requires deleting all models and retraining.
**Action:** Promoted to ai-factor-guide.md (Validation Methods section — expanded with backtest depth column)

---
id: LEARN-20260407-003
type: browser_selector
confidence: high
confirmations: 1
promoted: true
source: AI Factor → Ranking System pipeline — 2026-04-07
---
**Context:** Validation method settings are locked when models exist
**Discovery:** On the AI Factor Validation → Method tab, the validation method radio buttons (Basic Holdout / Rolling Time Series CV / etc.) become **read-only** as soon as any trained model exists. To change the method:
1. Go to Validation → Models tab
2. Check the checkbox next to each model row
3. Click **Delete** → Confirm
4. All models must be deleted before the Method tab becomes editable again
5. Then select the new method → navigate to Models → Add Model(s) → select the model → Start
**Action:** Promoted to ai-factor-guide.md (new section: Changing Validation Method)

---
id: LEARN-20260407-004
type: browser_selector
confidence: high
confirmations: 1
promoted: true
source: AI Factor → Ranking System pipeline — 2026-04-07
---
**Context:** "Save Validation Predictions" must be Yes
**Discovery:** When clicking **Start** to run validation training, a "Validate Model — Choose Worker(s)" dialog appears. It includes a **"Save Validation Predictions: Yes / No"** radio. This defaults to **neither selected** (no default). You MUST explicitly click **Yes** or `AIFactorValidation()` will have no saved predictions to use and the ranking system backtest will fail. The dialog also shows worker types (Basic, Premium, Extra30, HighMem) — the least-expensive available is auto-selected but the user can change it. HighMem shown in red = at capacity.
**Action:** Promoted to ai-factor-guide.md (new step: Save Validation Predictions = Yes)

---
id: LEARN-20260407-005
type: browser_selector
confidence: high
confirmations: 1
promoted: true
source: AI Factor → Ranking System pipeline — 2026-04-07
---
**Context:** Adding models in the "Add Model(s)" dialog — checkbox index shifts
**Discovery:** The "Add Model(s)" dialog lists all available models with checkboxes. **The checkbox DOM index shifts by 1 when a "N selected:" selection banner appears at the top.** This causes off-by-one errors when clicking by index. Safe approach:
```javascript
// Safe: select by row text content, not by index
var allCbs = Array.from(document.querySelectorAll('input[type=checkbox]'))
  .filter(c => c.getBoundingClientRect().x < 200);
allCbs.forEach(c => { if (c.checked) c.click(); }); // uncheck all first
var target = allCbs.find(c => {
  var row = c.closest('tr,[role=row]');
  return row && row.textContent.includes('lightgbm slow 2');
});
if (target) target.click();
```
Also: always click the "Add (N)" button by finding its text content, not by hardcoded coordinates — the button label changes as selections change.
**Action:** Promoted to browser-workflows.md (AI Factor — Add Model(s) dialog section)

---
id: LEARN-20260407-006
type: browser_selector
confidence: high
confirmations: 1
promoted: true
source: AI Factor → Ranking System pipeline — 2026-04-07
---
**Context:** Updating ranking system XML to use AIFactorValidation()
**Discovery:** The ranking system XML formula must use the exact format:
```xml
<Formula>AIFactorValidation(&amp;quot;agent_ml_v3_lgbm&amp;quot;, &amp;quot;lightgbm slow 2&amp;quot;)</Formula>
```
Note: in the raw XML editor, quotes are HTML-entity-encoded as `&amp;quot;`. When reading back via the UI or API, they render as `"`. The p123api client does NOT have a `rank_system_download()` method — use the browser's raw XML editor (`/app/ranking-system/{id}/editor-raw`) for direct XML manipulation.

To update via CDP browser automation:
```javascript
var ta = document.querySelector('textarea');
var nativeSetter = Object.getOwnPropertyDescriptor(window.HTMLTextAreaElement.prototype, 'value').set;
nativeSetter.call(ta, newXML);
ta.dispatchEvent(new Event('input', {bubbles: true}));
```
**Action:** Promoted to ranking-templates.md (AI Factor XML formula section)

---
id: LEARN-20260407-007
type: browser_selector
confidence: high
confirmations: 1
promoted: true
source: AI Factor → Ranking System pipeline — 2026-04-07
---
**Context:** Performance tab (rank_perf.jsp) — period alignment
**Discovery:** The ranking system Performance tab period presets (1M, 6M, 1Y, 2Y, 5Y, 10Y, MAX) refer to trailing periods ending **today**. With `AIFactorValidation()`:
- If predictions end at 12/27/2025 and today is 04/07/2026, then **any preset period that extends into 2026 will fail** (including 1Y = Apr 2025 → Apr 2026).
- The correct approach is to use the **custom date picker** (calendar icon, radio value `-1`) and set the date range to match the prediction window exactly.
- Use the JS native setter trick to set the text input: `nativeSetter.call(inp, '01/07/2017 - 12/27/2025')` — the input accepts `MM/DD/YYYY - MM/DD/YYYY` format.
- The Run button on this page is a `<input type="submit" value="Run">` (not a `<button>`), found via `document.querySelectorAll('input[type=submit]')`.
- Start date should be set to the first date of the first Rolling CV holdout window. For a 15-year dataset (2010–2025), 52-week gap, 5-year train, 27-month holdout, 4 folds: first predictions start ~01/2017.
**Action:** Promoted to ai-factor-guide.md (Ranking System Backtest Date Alignment section)

---
id: LEARN-20260407-008
type: browser_selector
confidence: high
confirmations: 1
promoted: true
source: AI Factor → Ranking System pipeline — 2026-04-07
---
**Context:** P123 URL routing — old JSP vs new Svelte SPA
**Discovery:** Portfolio123 has migrated most pages from legacy JSP URLs to a modern Svelte SPA. URL mapping discovered in practice:

| Old URL | New/Working URL |
|---|---|
| `/app/opener/AIFACTOR/-2` | Use `/sv/opener/AIFACTOR/-2` or navigate via `/sv/aiFactor/{id}/validation` |
| `/rank_perf.jsp?rankid={id}` | Works — redirects to the new Performance tab UI |
| `/app/ranking-system/{id}/performance` | Blocked ("not available at your current membership level") |
| `/app/ranking-system/{id}/editor-raw` | Works for XML editing |
| `/sv/aiFactor/{id}/validation` | Works for validation tab directly |

- The Run button on the rank_perf page is a legacy form submit (`input[type=submit]`), which is why DOM queries for `<button>` with text "Run" return nothing.
- AI Factor IDs can be found in the URL when navigating to the factor's page (e.g., `aiFactor/26889/validation` → ID is 26889).
**Action:** Promoted to browser-workflows.md (URL Routing section)

---
id: LEARN-20260407-009
type: strategy_insight
confidence: high
confirmations: 1
promoted: true
source: AI Factor → Ranking System pipeline — 2026-04-07
---
**Context:** Full end-to-end pipeline: AI Factor model → Ranking System → Performance backtest
**Discovery:** Complete working sequence (validated 2026-04-07):

**Step 1 — Choose validation method for backtest depth needed:**
- Basic Holdout = ~1 year of predictions (holdout period only)
- Rolling Time Series CV = multi-year (folds × holdout months). For 9-year backtest: 4 folds, 5-year train, 27-month holdout on a 15-year dataset.

**Step 2 — Delete any existing models if changing method** (method settings lock when models exist)

**Step 3 — Select Rolling Time Series CV on Method tab** (after deleting models, method tab becomes editable)

**Step 4 — Models tab: Add Model(s) → select model by row text → click Add (N)**

**Step 5 — Click Start → "Validate Model" dialog:**
- Set "Save Validation Predictions" = **Yes** (critical — defaults to nothing)
- Click Start

**Step 6 — Wait for SUCCESS** (Basic Holdout ~5 min, Rolling CV ~10–20 min depending on folds)

**Step 7 — Update ranking system formula to `AIFactorValidation()`:**
```xml
<Formula>AIFactorValidation(&amp;quot;AI_FACTOR_NAME&amp;quot;, &amp;quot;MODEL_DISPLAY_NAME&amp;quot;)</Formula>
```
Where MODEL_DISPLAY_NAME = the name shown in the Validation → Models tab (not the predictor slug).

**Step 8 — Performance tab: Use custom date range** aligned to prediction window:
- Navigate to `rank_perf.jsp?rankid={id}` (old URL still works)
- Click the calendar radio (value="-1")
- Set date range to cover prediction window: e.g., `01/07/2017 - 12/27/2025`
- Click Run (`input[type=submit][value="Run"]`)

**Result from 2026-04-07 run (agent_lgbm_v3_ranking, ID 541832):**
- Period: 1/7/2017 → 12/27/2025 (9 years)
- Bucket 20 CAGR: 12.10% | Benchmark: 15.02%
- Spearman rank correlation: 0.88 (strong monotonic ordering)
- First Half (2017–2021): Bucket 20 = 21.83%
- Second Half (2021–2025): Bucket 20 = 2.99%
**Action:** Promoted to ai-factor-guide.md as new section "Full Pipeline: AI Factor to Ranking System Backtest"

---
id: LEARN-20260413-001
type: browser_selector
confidence: high
confirmations: 1
promoted: true
source: P123 TAA ETF strategy search — 2026-04-13
---
**Context:** Editing buy rules in a P123 simulated strategy wizard (edit mode)
**Discovery:** `port_simul3.jsp` AJAX calls via `jsPort.loadPortTab()` do **NOT** persist buy rule changes to the database. The server re-renders the tab using submitted form data but the underlying saved strategy remains unchanged. Verified by: navigating away and back — the old values reappear. The only mechanism that actually saves buy rule changes is submitting the form to `port_sim_go.jsp` via `jsPort.run()`.
**Action:** Promoted to browser-workflows.md (P123 Wizard Save Mechanism section)

---
id: LEARN-20260413-002
type: browser_selector
confidence: high
confirmations: 1
promoted: true
source: P123 TAA ETF strategy search — 2026-04-13
---
**Context:** Inserting double-quoted strings into P123 formula textareas via CDP
**Discovery:** The `type` command in `cdp.mjs` (and `Input.insertText` via CDP) strips double-quote characters when passed through PowerShell string arguments. Workaround: construct the string in JavaScript using `String.fromCharCode(34)` for each double-quote character, then call `document.execCommand('insertText', false, formula)`. This is the ONLY reliable way to insert quoted strings into P123's formula textareas.

```javascript
var q = String.fromCharCode(34);
var formula = 'Ticker(' + q + 'SPY,IWM,...,USMV' + q + ')';
document.execCommand('insertText', false, formula);
```
**Action:** Promoted to browser-workflows.md (CDP Double-Quote Workaround section)

---
id: LEARN-20260413-003
type: browser_selector
confidence: high
confirmations: 1
promoted: true
source: P123 TAA ETF strategy search — 2026-04-13
---
**Context:** Editing buy rule textareas in P123 wizard (controlled by JavaScript framework)
**Discovery:** P123's formula textareas are controlled by a JavaScript framework (React/jQuery). Direct DOM manipulation (`ta.value = x`, native setter + `dispatchEvent`) does NOT reliably persist. `document.execCommand('insertText', false, text)` DOES work when the textarea is focused via a real click (`cdp.mjs clickxy`) immediately before — it triggers the framework's input event handlers. Critical sequence:
1. `node cdp.mjs clickxy <tab> <cx> <cy>` — physically focus the textarea
2. `node cdp.mjs eval <tab> "ta.focus(); ta.select();"` — select all
3. `node cdp.mjs eval <tab> "document.execCommand('insertText', false, text);"` — insert

Do NOT use `cdp.mjs type` for strings containing double quotes — they get stripped.
**Action:** Promoted to browser-workflows.md (CDP Formula Textarea Editing section)

---
id: LEARN-20260413-004
type: browser_selector
confidence: high
confirmations: 1
promoted: true
source: P123 TAA ETF strategy search — 2026-04-13
---
**Context:** P123 wizard save + run mechanism (strategy edit mode)
**Discovery:** `jsPort.run(Date.now(), true)` is the correct call to save AND run a P123 simulation. It:
1. Skips the component properties naming modal (skip=true)
2. Changes form action to `port_sim_go.jsp?{timestamp}`
3. Calls `verifyInputs()` to check for formula errors
4. Submits the full form — this is the only actual database save in the wizard

Workflow for editing and saving a strategy via CDP:
```javascript
// 1. Fix formula via execCommand (see LEARN-20260413-003)
// 2. Verify the value is correct
var ta = document.querySelector('textarea[name=buyruleformula_0]');
console.log(ta.value); // Must show the correct formula

// 3. Save + run
jsPort.run(Date.now(), true);
```
Then wait ~10s and screenshot — the page will navigate to `port_summary.jsp?portid=XXX` on success, or show an error inline.
**Action:** Promoted to browser-workflows.md (P123 Wizard Save Mechanism section)

---
id: LEARN-20260413-005
type: browser_selector
confidence: high
confirmations: 1
promoted: true
source: P123 TAA ETF strategy search — 2026-04-13
---
**Context:** Chrome CDP connection blocked by P123 delete confirm dialog
**Discovery:** Clicking the X (cut/delete) icon on P123 buy/sell rules triggers a native JavaScript `confirm()` dialog ("Are you sure?"). This dialog BLOCKS the Chrome DevTools Protocol thread, causing ALL subsequent CDP commands (`shot`, `eval`, `list`) to hang indefinitely. The hang persists even after killing Node.js processes. The Chrome debugging port becomes unresponsive.

Fix: manually click OK/Cancel in the Chrome browser window to dismiss the dialog, then CDP reconnects.

Prevention: avoid clicking delete icons on P123 formula rows via CDP. Use `jsPort.filterDeleteElem(index)` programmatically instead of triggering the UI delete:
```javascript
// Safe: delete rule at index 0 without triggering confirm dialog
jsPort.filterDeleteElem(0); // Returns the old index; does not show confirm
```
**Action:** Promoted to browser-workflows.md (Known platform quirks section)

---
id: LEARN-20260413-006
type: browser_selector
confidence: high
confirmations: 1
promoted: true
source: P123 TAA ETF strategy search — 2026-04-13
---
**Context:** P123 wizard JavaScript API methods discovered via introspection
**Discovery:** The P123 strategy wizard exposes a `jsPort` global object with the following key methods (complete list via `Object.getOwnPropertyNames(jsPort).filter(k=>typeof jsPort[k]==='function')`):

| Method | Purpose |
|--------|---------|
| `jsPort.run(msec, skip)` | Save + run simulation. `skip=true` skips naming modal |
| `jsPort.loadPortTab()` | AJAX reload current tab (does NOT save to DB) |
| `jsPort.saveChanges()` | Attempts to save — causes Internal Server Error, do NOT use |
| `jsPort.filterInsert(type, name, formula)` | Add a new rule (type 0=buy, 1=sell) |
| `jsPort.filterDeleteElem(index)` | Delete rule at index WITHOUT a confirm dialog |
| `jsPort.showTextEditor(...)` | Open text editor view |
| `jsPort.verifyInputs()` | Validate all formulas — returns false if any error |
| `jsPort.switchTab(tabId)` | Switch wizard tab (does not save) |
| `jsPort.goToTab(tabId)` | Navigate to a tab |
| `jsPort.selectedTab` | Current tab number (3=Buy, 4=Sell, etc.) |
| `jsPort.TAB_BUY`, `jsPort.TAB_SELL` | Tab constants (3, 4, ...) |

**Action:** Promoted to browser-workflows.md (jsPort API Reference section)

---
id: LEARN-20260413-007
type: strategy_insight
confidence: high
confirmations: 1
promoted: true
source: P123 TAA ETF strategy search — 2026-04-13
---
**Context:** ETF-only TAA strategy performance over 2006–2026
**Discovery:** For ETF-only TAA strategies over the 2006–2026 period (covering 2008 GFC and 2020 COVID crash), the realistic performance frontier is:
- **CAGR:** 8–12% (best momentum-based rotation)
- **Max Drawdown:** -40% to -55% (equity ETF exposure)
- **Calmar Ratio:** 0.15–0.30
- **Sharpe:** 0.5–0.8

Targets of CAGR >15% AND Calmar >1 simultaneously are **structurally infeasible** for ETF-only TAA from 2006 (requires MaxDD < 15% at 15% CAGR — impossible while holding equity ETFs through 2008). If both targets must be met: (a) restrict to post-GFC period (2010+), (b) allow individual stocks, or (c) relax to 12% CAGR + Calmar >0.5.
**Action:** Promoted to case-studies.md (ETF TAA Feasibility Benchmarks section)

---
id: LEARN-20260413-008
type: strategy_insight
confidence: high
confirmations: 1
promoted: true
source: P123 TAA ETF strategy search — 2026-04-13
---
**Context:** screen_backtest (Tier 3) vs native simulation (Tier 2) discrepancy for ETF strategies
**Discovery:** For ETF momentum TAA strategies, `screen_backtest` showed ~3.25% CAGR (Tier 3), but the same strategy in P123 native simulation showed **10.36% CAGR** (Tier 2) — a **3x underestimation** by screen_backtest. This is opposite to the typical stock strategy pattern where screen_backtest *overstates* CAGR.

Explanation: `screen_backtest` for ETF TAA only backtests the "screen" (buy-side filter), typically returning the single best-ranked ETF per period — it is not running a portfolio simulation. The native simulation holds N positions simultaneously, rebalances via ranking, and compounds correctly. The Tier 3 haircut of 30-40% is calibrated for *stock* strategies and should NOT be applied mechanically to ETF TAA.

**Rule:** For ETF rotation strategies, use Tier 2 (native simulation) directly. Do not use Tier 3 screen_backtest results as estimates for ETF TAA performance — they will dramatically underestimate (not overestimate) the strategy.
**Action:** Promoted to strategy-validation.md (ETF TAA Exception section) and api-reference.md warning

---
id: LEARN-20260413-009
type: strategy_insight
confidence: high
confirmations: 1
promoted: true
source: P123 TAA ETF strategy search — 2026-04-13
---
**Context:** P123 wizard ranking system selection for ETF strategies
**Discovery:** P123's strategy creation wizard does NOT support custom formula ranking for ETF simulated strategies. The "Universe & Ranking" tab only shows built-in ranking systems from the dropdown. You cannot use `Ret%Chg(63)/ATR(63)` (risk-adjusted momentum) as a ranking formula inline.

Workarounds (in order of complexity):
1. **Create a custom Ranking System** separately (RESEARCH → Ranking Systems → New), encode the formula there, then select it in the wizard's ranking dropdown
2. **Use the closest built-in:** "Price Uptrend - Basic" for short-term momentum, "ETF Rotation - Basic" for 12-month momentum
3. **Encode via Buy Rules** — use a buy rule like `Rank > 80` with a pre-created ranking system to approximate the formula

Note: "Price Uptrend - Basic" uses 60-day price change + EMA/SMA ratio — it lacks ATR normalization. This increases allocation to high-volatility ETFs during stress periods, worsening drawdowns.
**Action:** Promoted to browser-workflows.md (ETF Ranking System Limitation section) and strategy-templates.md

---
id: LEARN-20260414-001
type: hyperparameter
confidence: high
confirmations: 1
promoted: true
source: AI-Driven Quant Investment Strategies Substack #37 — "Visualizing the Learning Logic #7: Extra Trees (3/3)"
---
**Context:** ExtraTrees learning logic — why averaging works, when it beats LightGBM, and how to evaluate it correctly
**Discovery:** Three key insights from the final ExtraTrees learning logic post:

1. **Averaging cancels directional blow-ups:** Each tree overshoots in a different direction due to random feature selection and random thresholds. When deviation directions differ across trees, the average cancels them out — roughness of any single tree is absorbed. More trees = more directional diversity = more cancellation = lower variance.

2. **ExtraTrees can outperform LightGBM in noisy markets:** LightGBM "smartly" picks up past noise → "confident misses" in crash months. ExtraTrees doesn't try to nail the target with one tree; it stabilizes by averaging → "less sharpness, but fewer blow-ups." In stock markets, operational value of "milder ways of missing" can exceed "strong ability to force a hit."

3. **RMSE alone is misleading for ranking-based strategies:** Good RMSE = good at hitting the numeric value (3MRel%), but in operation we buy top-ranked names — what matters is ranking ability. Even with good RMSE, if Top 10% is weak, strategy won't win. Even with worse RMSE, if Top 10% is strong and stable, high operational value. Evaluate ExtraTrees with a metric set: RMSE (regression accuracy) + Top 10% average 3MRel / hit rate (ranking performance) + Decile performance (whether ranking works cleanly).

**Complementarity note:** LightGBM fixes residuals (sharp, overfitting risk); ExtraTrees averages random trees (rounder, more stable). Common real-world workflow: average predictions of both models (model ensembling) to reduce blow-ups while still aiming for upside.
**Action:** Promoted to ai-factor-guide.md (ExtraTrees Learning Logic — 3 new subsections + ensemble note)
