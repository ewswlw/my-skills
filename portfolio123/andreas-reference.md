# Andreas Himmelreich — AI Factor Methodology

Robustness-first philosophy, ensemble design, universe selection, training rigor. Source: Substack, LinkedIn, Portfolio123 Resources.

## Robustness First

Market durability over backtest elegance. A strategy that fails live is worse than one that performs modestly but consistently. P123's percentile ranking (0-100) reflects this: outlier-resistant, NA-handling, comparable across factors.

## Ensemble Design: Arrow + Shield

- **LightGBM (Arrow):** Idea generator. Wins by amplifying top-ranked stocks. Use for long signals.
- **ExtraTrees (Shield):** Quality control. Wins by suppressing weak stocks. Use as buy filter.

**Small Cap Alpha Engine:** LightGBM for ranking + ExtraTrees as gatekeeper. Division of labor: LightGBM explores; ExtraTrees prevents overfitting to noise.

## Universe Selection

**Path 1 — Homogeneous:** Clean, focused (e.g., EU Small Caps, US Small Caps filtered by liquidity). AI learns specific "dialect."

**Path 2 — Massive:** North Atlantic, Global Developed. So large that dominant signals emerge. AI gravitates toward strongest cluster.

**Death Zone:** Avoid universes too big to be homogeneous AND too small for dominant cross-regime signals.

**Rule:** "Your job is to curate the character of the universe—liquidity, region, size band—then get out of the way." Fewest opinions perform best.

## Training Philosophy

- **Window:** 2003-2020.06. Training beyond mid-2020 "spoils" LightGBM (2020-2021 not representative).
- **Uninterrupted:** Use Basic Holdout. Avoid walk-forward optimization so model learns regime-dependent behavior.
- **No immediate retraining:** Models frozen after training. Validate through pseudo-OOS before live.

## OOS Validation Rigor

- **OOS Pseudo:** Test on unseen data (mid-2020 onward) with realistic slippage (0.5 cents/share) in Portfolio Strategy.
- **OOS Live:** Actual live performance.
- **Rule:** OOS Live must replicate OOS Pseudo. If not, do not go live.
- **Representative training:** 99% of models replicate when setup is correct.

## Buy Rules Alignment

Align with strongest factors and FactSet/P123 Point-in-Time data. Buy rules activate relevant trees without deleting broader knowledge.

## Live Deployment Checklist

1. Train 2003-2020.06
2. Validate pseudo-OOS with realistic slippage
3. If OOS Live ≠ OOS Pseudo → do not go live
4. Use homogeneous universes
5. Basic Holdout, no walk-forward
6. Enable Save Predictions for AIFactorValidation
