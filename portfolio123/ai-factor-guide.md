# Portfolio123 AI Factor Guide

Full ML workflow, 16 hyperparameter presets, 4 validation methods, evaluation diagnostics. Source presets from vault: file dump/Portfolio123/Portfolio123 AI Factor Reference.md

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
- **Target:** 3M or 12M total/relative return
- **Period:** 2003-2020.06 recommended (avoid 2020-2021 for training — not representative)
- **Gap:** 52-week gap between training and validation

## Preprocessing

- **Scaling:** Rank (percentile) or Z-Score. Rank maintains order, Z-Score normalizes.
- **NA handling:** Replace with median
- **Trim:** 7.5% each side (15% total omitted for distribution stats)
- **Outlier limit:** Cap extreme values

## Validation Methods

| Method | When to Use |
|--------|-------------|
| **Basic Holdout** | Default. Single train/validation split. Avoids walk-forward overfitting. |
| **Time Series CV** | Multiple validation periods, expanding training. More robust. |
| **Rolling Time Series CV** | Fixed training window, sliding. |
| **K-Fold Blocked** | Maximizes data use. Temporal order not respected. |

## Algorithms

- **LightGBM** — High performance, directional targets. Risk: overfitting, high turnover.
- **ExtraTrees** — Robust, lower turnover. Good for noisy horizons.
- **XGBoost** — Alternative gradient boosting.

**Ensemble (Small Cap Alpha):** LightGBM (ranking) + ExtraTrees (buy filter). LightGBM finds patterns; ExtraTrees gates quality.

## Key Hyperparameter Presets

**Small Cap Alpha Engine (Andreas):**
- LightGBM: n_estimators=1000, learning_rate=0.01, max_depth=7, min_child_samples=100
- ExtraTrees: n_estimators=600, max_features=0.3

**Maestro (P123 default):** Balanced, professional-grade. Use when unsure.

**13 Meeting Types:** FastFire, DeepThinker, RuleMaster, ComplianceCore, SharpShooter, RiskBalancer, BigBrain, EarlyStopper, OverfitArtist, ZenMinimalist — see vault AI Factor Reference for full configs.

**3 P123 Presets:** Maestro, ComplianceLite, FieldScout.

## AIFactorValidation vs AIFactor

- **AIFactorValidation()** — Backtesting. Uses saved validation predictions. No backtest limit.
- **AIFactor()** — Live only. Backtest max 5 years. Real-time prediction server.

**Always** enable "Save Validation Predictions" during validation. Backtest start > training end + gap.

## Evaluation Diagnostics Checklist

1. **Monotonicity:** Bar chart rises Bucket 1 → 50?
2. **Edge sharpness:** Bucket 1 and 50 clearly separated?
3. **Noise:** Random spikes between adjacent buckets?
4. **Time shift:** First Half vs Second Half — do extremes stay consistent?
5. **H-L spread:** Top vs bottom quantile return gap
6. **Turnover:** High bucket turnover — practical to implement?
7. **Time resilience:** Structural (shape stable) vs Semantic (does Bucket1 stay "bad"?)

## Ranking System with AI Factor

```xml
<Formula>FRank(AIFactorValidation("Exact AI Factor Name", "Exact Model Name"))</Formula>
```

Case-sensitive. Get exact names from Predictors page fx button after training.
