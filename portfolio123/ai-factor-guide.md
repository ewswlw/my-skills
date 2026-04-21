# Portfolio123 AI Factor Guide

Full ML workflow, 16 hyperparameter presets, 4 validation methods, evaluation diagnostics.

## Deep dive (vault — optional)

This file is the **operational** guide. For **long-form** methodology—feature-scaling narrative, Z-Score variants, LineReg/PctDev intuition, extended hyperparameter “meeting types,” quantile diagnostics, and worked philosophy—open the Obsidian note:

`file dump/Portfolio123/Portfolio123 AI Factor Reference.md`

If the workspace has no vault, rely on **andreas-reference.md**, P123 help, and `doc_detail.jsp` factor validation. Do not assume the vault file is on disk.

**Presets source:** vault `Portfolio123 AI Factor Reference.md` (also summarized below).

## Default Philosophy: Train Wide, Filter Smart

- Train on broad, noisy universe (all stocks with liquidity)
- Apply quality filters at portfolio strategy level, not pre-filter training data
- 130-180 features optimal
- Avoid pre-filtering universes before training

## Three-Phase Async Workflow

**Phase 1 — Configure (browser, ~5 min):** Dataset, features, preprocessing, validation method, model selection. Automate via browser.

**Phase 2 — Execute (P123 cloud):** Click Run Validation. Do NOT hold browser open. Provide expected wait time. User returns when done.

**Phase 3 — Evaluate (browser, ~3 min):** Navigate to results, screenshot lift charts, read Compare All, extract diagnostics.

## Dataset Preparation

- **Features:** 130-180 sweet spot. Import from ranking systems, Factor Lists, or other AI Factors.
- **Target:** 3M or 12M total/relative return. For **combined multi-month targets**: sum of 1-month + 2-month + 3-month forward returns ("1+2+3MTR" style) — overweight the front month if picks should work immediately and still persist. Match horizon to trading cadence: ~200-400% annual turnover suggests 3-month target is reasonable.
- **Period:** 2003-2020.06 recommended (avoid 2020-2021 for training — not representative)
- **Gap:** 52-week gap between training and validation

## Preprocessing

- **Scaling:** Rank (percentile) or Z-Score. Rank maintains order, Z-Score normalizes.
- **NA handling:** Replace with median
- **Trim:** 7.5% each side (15% total omitted for distribution stats)
- **Outlier limit:** **5 sigma default** (not 2.5 sigma). Test up to 10 sigma to confirm optimality. Clipping at 2.5 sigma collapses the signal gradient — the model can no longer distinguish "strong" from "extreme." Fat tails carry signal, not noise.

**Practitioner divergence note:** The settings above are derived from Andreas Himmelreich ("Recipe A: broad/robust"). An alternative practitioner recipe (Systematic Investing, "Recipe B: regional/specialized") uses **2.5% tail trim + 3-sigma outlier cap** with Z-score normalization. Both are valid and reflect different philosophy — Recipe A preserves fat-tail signal; Recipe B reduces outlier influence. Neither is objectively correct; choose based on your universe characteristics and validate in your own backtests.

## Validation Methods

| Method | When to Use | Prediction Window | Max Backtest Depth |
|--------|-------------|-------------------|--------------------|
| **Basic Holdout** | Default. Single train/validation split. Avoids walk-forward overfitting. | Holdout period only (last N months) | ~1–2 years |
| **Time Series CV** | Multiple validation periods, expanding training. More robust. | Multiple expanding windows | ~3–5 years |
| **Rolling Time Series CV** | Fixed training window, sliding. Best for long backtests. | All fold holdout windows combined | ~5–10 years |
| **K-Fold Blocked** | Maximizes data use. Temporal order not respected. | No temporal guarantee | Not recommended for backtests |

**Critical:** The validation method determines how many years of predictions are saved, which in turn limits how far back the ranking system Performance tab can backtest using `AIFactorValidation()`. Choose before training — changing later requires deleting all models.

### Practitioner Recipe B: Regional ML (Systematic Investing)

A concrete alternative to the Andreas-derived defaults above, optimized for **regional specialization** (train separate models per US / Ex-US universe).

| Setting | Value |
|---------|-------|
| Models | 3× LightGBM duplicates per region (US, Ex-US) for stability testing |
| Features | ~100 features from factor literature |
| Dataset | 2004–present, **weekly** bars |
| Target | Sum of 1m + 2m + 3m forward returns, cross-sectional normalization per date |
| Feature scaling | Z-score, 2.5% tail trim, 3-sigma outlier cap |
| CV method | Time-series CV |
| Train/val gap | 26 weeks |
| Folds | 19 |
| Holdout per fold | 12 months |
| Duplicate models | Train duplicates with same spec to test stability (if results diverge, signal is fragile) |

**Validation Sharpe ranges (author-reported, not targets):** Global 2.65–2.81, USA 1.64–1.90, Ex-US 1.98–2.11.

**Framing:** This is Recipe B (regional/specialized), complementing Recipe A (broad/robust from Andreas). Neither overrides the other. The key differences: Recipe B trains on region-homogeneous universes for cleaner ML signal; Recipe A trains wide to capture dominant cross-regime patterns.

### Changing Validation Method (after models exist)

The Method tab fields are **read-only while any trained model exists**. To change:
1. Go to Validation → **Models** tab
2. Check the checkbox next to every model row
3. Click **Delete** → **Confirm** (repeat for all models)
4. Return to Validation → **Method** tab (now editable)
5. Select new method → adjust Folds / Training Period / Holdout Period
6. Go back to Models → **Add Model(s)** → select model → **Start**

## Algorithms

- **LightGBM** — High performance, directional targets. Risk: overfitting, high turnover. Mode: "efficiently try to hit the target" — sharper but can miss badly when it overfits.
- **ExtraTrees** — Robust, lower turnover. Good for noisy horizons. Mode: "reduce noise by averaging" — stability-oriented, easier to explain.
- **XGBoost** — Alternative gradient boosting.

**Ensemble (Small Cap Alpha):** LightGBM (ranking) + ExtraTrees (buy filter). LightGBM finds patterns; ExtraTrees gates quality.

**Model ensembling (prediction averaging):** Distinct from the buy-filter ensemble above — this pattern averages the raw prediction scores of LightGBM and ExtraTrees into a single composite. LightGBM fixes residuals (sharp, carries overfitting risk); ExtraTrees averages random trees (rounder, often more stable). Averaging their predictions combines strengths: reduce blow-ups while still aiming for upside.

**Structured side-by-side narrative (series roadmap, few features × noise, bias–variance, ranking-tail metrics when RMSE is insufficient):** see [lightgbm-vs-extratrees-learning.md](lightgbm-vs-extratrees-learning.md). Conceptual only—validate in native P123 (Validation Hierarchy in `SKILL.md`).

### LightGBM Learning Logic: How It Works

LightGBM uses **histogram binning**: instead of searching infinite real-valued split thresholds, it rounds continuous features (e.g., ROE) into ~255 bins. Each stock's feature value becomes a bin index. Split search becomes finite: "which bin boundary reduces loss most?" using precomputed bin-level gradient aggregates.

- **Result:** Dramatically faster split search → can evaluate more features and candidates → better splits
- **Investing intuition:** Instead of "find the perfect ROE decimal cutoff," bucket ROE into ranges and use range statistics to compare quickly

### LightGBM Overfitting Risk

LightGBM can learn past noise as real "laws." When conditions don't repeat in the future, the model confidently predicts in the wrong direction → huge misses. This risk is amplified with:
- Deep leaf-wise growth (high `num_leaves` / `max_depth`)
- Many trees without regularization

### LightGBM Anti-Overfitting Hyperparameters

| Parameter | Recommendation | Why |
|-----------|---------------|-----|
| `learning_rate` (η) | Lower (e.g., 0.01) + more trees | Don't nail it in one shot; correct gradually |
| `min_data_in_leaf` | Set meaningfully (e.g., 100) | **Extremely important for stocks** — prevents optimizing to a handful of stocks |
| `num_leaves` / `max_depth` | Constrain (e.g., max_depth=7) | Overly fine branching becomes a "past-only rule" |
| `feature_fraction` / `bagging_fraction` | Apply sampling | Reduce dependence on features that happened to work |
| Validation | Time-series walk-forward + early stopping | Random splits hide future performance collapse |

### ExtraTrees Learning Logic: How It Works

ExtraTrees builds many trees where **both feature selection and split thresholds are chosen randomly** — neither is optimized.

**Tree structure:**
- Each tree starts from the same universe (e.g., S&P 500) but selects a different first feature to split on.
  - Tree 1 may open on `ROE > *` → then `ΔSales` at the next level
  - Tree 2 may open on `OpMgn > *` → then `ΔEPS`
  - Tree 3 may open on `RSI > *` → then another random split
- At each branch, the `> *` threshold is also randomly set — not chosen to minimize loss.
- At every **leaf**, the model returns the **average 3MRel of all stocks in that leaf** as the prediction.

**Single-stock routing (why averaging matters):**
StockA follows a different path in every tree because features and thresholds differ — it lands in different leaves and picks up different leaf-average 3MRel values. ExtraTrees **deliberately produces noisy, varying per-tree predictions** and then averages them. The averaging is the design; individual tree roughness is expected and absorbed.

**It is not "pure luck":**
Even with random candidates, splits that separate groups with meaningfully different 3MRel behavior tend to survive the random selection process. Purely uninformative splits get averaged away across enough trees.

**Contrast with LightGBM:**
- LightGBM: searches for the split that reduces loss the most — **"make each tree smart"**
- ExtraTrees: generates split candidates randomly and builds many different trees — **"one tree can be rough; win by quantity"**

**Why averaging cancels blow-ups (the core strength):**
Tree 1 might slightly overshoot upward because of one boundary, Tree 2 downward because of another, Tree 3 drifts in yet another direction. When the deviation directions differ across trees, the final average makes them cancel out. This dilutes any single tree's roughness → predictions become more stable (variance goes down). More trees = more directional diversity = more cancellation.

**Why ExtraTrees can outperform LightGBM in stock markets:**
LightGBM's sharpness (see Overfitting Risk above) means it can produce "confident misses" in crash months — picking up past noise as signal. ExtraTrees does not try to nail the target with a single tree; it stabilizes by averaging → "less sharpness, but fewer blow-ups." In stock markets, the operational value of "milder ways of missing" can exceed "strong ability to force a hit" — that is where ExtraTrees looks stronger.

**RMSE interpretation warning (critical for ranking-based strategies):**
RMSE measures how far predictions deviate from realized values and penalizes big misses (quadratic penalty). Good RMSE = "good at hitting the numeric value (3MRel%)." But in operation, we buy the top-ranked names — what we need is **ranking ability**, not regression accuracy. Even with good RMSE, if the Top 10% is weak, the strategy won't win. Even with somewhat worse RMSE, if the Top 10% is strong and stable, the strategy has high operational value. ExtraTrees often shows value here: a more stable Top 10% even when its RMSE is not the best. (See also Evaluation Diagnostics Checklist item 8 below.)

**Practical evaluation metric set for ExtraTrees:**
| Metric | What It Measures |
|--------|------------------|
| RMSE | Regression accuracy — ability to hit the numeric value |
| Top 10% average 3MRel / hit rate | Operational "hits" — ranking performance where it matters |
| Decile performance | Whether the ranking works cleanly (higher deciles should outperform lower) |

Use all three together; no single metric tells the full story.

**Practical consequence for P123:**
ExtraTrees is harder to overfit because no tree is optimizing to past data. High `n_estimators` (e.g., 600) matters — more trees = more diversity in the average = more stable out-of-sample prediction.

### ExtraTrees vs. LightGBM Decision Guideline

| Scenario | Choice |
|----------|--------|
| Starting out / baseline / conservative | **ExtraTrees** — stable, easy to explain, hard to overfit |
| Features have genuine predictive power AND you apply regularization | **LightGBM** — more accuracy but requires careful tuning |
| Buy filter / quality gate in ensemble | **ExtraTrees** |
| Ranking 500 stocks monthly, buy top-ranked | Compare by **hit rate in top X%** not regression error — reveals LightGBM strength and overfitting risk more clearly |

## Key Hyperparameter Presets

**Small Cap Alpha Engine (Andreas):**
- LightGBM: n_estimators=1000, learning_rate=0.01, max_depth=7, min_child_samples=100
- ExtraTrees: n_estimators=600, max_features=0.3

**Maestro (P123 default):** Balanced, professional-grade. Use when unsure.

**All-Must-Perform Rule:** When testing hyperparameter presets, ALL sets must produce positive lift — not just the top three. If the signal only works under one specific configuration, it is fragile. Real signals survive hyperparameter variance by design.

**13 Meeting Types:** FastFire, DeepThinker, RuleMaster, ComplianceCore, SharpShooter, RiskBalancer, BigBrain, EarlyStopper, OverfitArtist, ZenMinimalist — see vault AI Factor Reference for full configs.

**3 P123 Presets:** Maestro, ComplianceLite, FieldScout.

## AIFactorValidation vs AIFactor

| | `AIFactor()` | `AIFactorValidation()` |
|---|---|---|
| **Purpose** | Live scoring, real-time prediction | Backtesting with saved predictions |
| **Backtest limit** | **5 years max** — hard P123 limit | **None** — limited only by prediction window |
| **Data source** | Live predictor server | Saved validation predictions from training run |
| **Formula string** | `AIFactor("ai_factor_name", "predictor_slug")` | `AIFactorValidation("ai_factor_name", "model_display_name")` |
| **Model name arg** | Predictor name from Predictors tab | Model display name from Validation → Models tab |

**Formula exact syntax (in ranking system XML):**
```xml
<Formula>AIFactorValidation(&amp;quot;agent_ml_v3_lgbm&amp;quot;, &amp;quot;lightgbm slow 2&amp;quot;)</Formula>
```
Quotes are HTML-entity-encoded in raw XML (`&amp;quot;`). Both name strings are **case-sensitive** — copy from the UI.

**MANDATORY:** Enable **"Save Validation Predictions = Yes"** in the training dialog. The dialog defaults to neither Yes nor No selected. Without this, `AIFactorValidation()` has nothing to query and every backtest date will fail with "No predictions are available."

### Training Dialog — Save Validation Predictions

When clicking **Start** on a validation model, a "Validate Model — Choose Worker(s)" dialog appears:
- **Worker types:** Basic (cheapest), Premium, Extra30 (30 CPU), HighMem (170GB) — auto-selects least expensive available
- **Save Validation Predictions:** defaults to NOTHING selected — **always click Yes explicitly**
- HighMem shown in red = at capacity (choose another worker or wait)
- Training time: Basic Holdout ~5 min, Rolling Time Series CV ~10–20 min

## Evaluation Diagnostics Checklist

1. **Monotonicity:** Bar chart rises Bucket 1 → 50?
2. **Edge sharpness:** Bucket 1 and 50 clearly separated?
3. **Noise:** Random spikes between adjacent buckets?
4. **Time shift:** First Half vs Second Half — do extremes stay consistent?
5. **H-L spread:** Top vs bottom quantile return gap
6. **Turnover:** High bucket turnover — practical to implement?
7. **Time resilience:** Structural (shape stable) vs Semantic (does Bucket1 stay "bad"?)
8. **Hit rate in top X%:** For stock-scoring strategies, evaluate ranking performance (hit rate in top 10%/20%) in addition to regression error — better reflects real portfolio impact and exposes overfitting risk

## Ranking System with AI Factor

```xml
<Formula>AIFactorValidation(&amp;quot;Exact AI Factor Name&amp;quot;, &amp;quot;Exact Model Display Name&amp;quot;)</Formula>
```

- **Case-sensitive** — copy both strings from the P123 UI.
- AI Factor Name: from the Overview tab (the factor's display name, e.g., `agent_ml_v3_lgbm`)
- Model Display Name: from Validation → Models tab (e.g., `lightgbm slow 2`) — NOT the predictor slug
- Use `AIFactorValidation()` (not `AIFactor()`) for any backtest deeper than 5 years
- The p123api client has no `rank_system_download()` method — use the raw XML editor at `/app/ranking-system/{id}/editor-raw` for direct XML updates

## Classic vs ML Blend Weights

When combining a classic multifactor ranking with an AI Factor in the same ranking system, the weight split matters. A 5-point grid tested in practice (source: Systematic Investing, Layers of Return Part VI):

| Classic weight | ML weight | Character |
|---------------|-----------|-----------|
| 100% | 0% | Pure classic multifactor |
| 95% | 5% | ML kicker |
| 50% | 50% | Equal blend |
| 5% | 95% | Classic kicker (**operational recommendation**) |
| 0% | 100% | Pure ML |

**Recommendation:** Use **5% classic / 95% ML** ("classic kicker") as the default operational setup. The small classic weight moderates junk-stock exposure, reduces turnover slightly, and anchors buys without negating ML edge.

**How to implement in ranking XML** — two sibling composites with explicit weights:

```xml
<RankingSystem RankType="Higher">
  <Composite Name="agent_classic" Weight="5" Label="Classic Kicker" RankType="Higher">
    <!-- your classic multifactor nodes here (Template 6 structure) -->
  </Composite>
  <Composite Name="agent_ml" Weight="95" Label="ML Factor" RankType="Higher">
    <StockFormula Name="ai_validation" RankType="Higher" Scope="Universe" Weight="100">
      <Formula>AIFactorValidation("agent_your_factor", "your_model_name")</Formula>
    </StockFormula>
  </Composite>
</RankingSystem>
```

**Short side:** Use approximately **50% ML weight** for short strategies (shorter horizon target variable than long book).

## Full Pipeline: AI Factor → Ranking System Backtest

Complete validated sequence (confirmed 2026-04-07, agent_lgbm_v3_ranking ID 541832):

### 1. Choose Validation Method for Required Backtest Depth
- Basic Holdout → ~1 year of predictions (last holdout period only)
- Rolling Time Series CV, 4 folds, 5-year train, 27-month holdout → ~9 years of predictions

For Rolling CV, predictions start ~= `dataset_start + training_period + gap`. Example:
- Dataset: 2010–2025 (15 years), Training: 5 years, Gap: 52 weeks
- First fold holdout starts: 2010 + 5yr + 1yr gap = ~2016/Q4
- Backtest can start from: **~01/07/2017**

### 2. Delete Existing Models if Changing Method
Method tab is read-only while models exist. Delete all → Method tab unlocks → select new method.

### 3. Train Model with Save Validation Predictions = Yes
In the "Validate Model" dialog: click **Yes** explicitly. Without this, all backtest dates will fail.

### 4. Update Ranking System XML Formula
Change from `AIFactor()` to `AIFactorValidation()` with the model's display name:
```xml
<Formula>AIFactorValidation(&amp;quot;agent_ml_v3_lgbm&amp;quot;, &amp;quot;lightgbm slow 2&amp;quot;)</Formula>
```

### 5. Set Performance Tab Date Range to Match Prediction Window
- Navigate to `rank_perf.jsp?rankid={id}` (the old JSP URL still works and routes correctly)
- The **Run** button is `<input type="submit" value="Run">` (not a `<button>`)
- Click the calendar icon radio (value=`-1`) to enable custom dates
- Set range to cover prediction window: e.g., `01/07/2017 - 12/27/2025`
- Do NOT use preset periods (1Y, 2Y, MAX) — they extend to today, past the prediction end date
- Error you'll see if dates are wrong: *"No predictions are available on [date]. Saved predictions cover [start] to [end] every week."* — use those exact dates from the error message.

### Result Reference (2026-04-07 run)
| Metric | Value |
|---|---|
| Period | 1/7/2017 → 12/27/2025 (9 years) |
| Bucket 20 CAGR | 12.10% |
| Benchmark (SPY) CAGR | 15.02% |
| Spearman Rank Correlation | 0.88 |
| First Half B20 (2017–2021) | 21.83% |
| Second Half B20 (2021–2025) | 2.99% |
