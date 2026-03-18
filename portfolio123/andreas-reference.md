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

- **Window:** 2003-2020.06. Training beyond mid-2020 "spoils" LightGBM (2020-2021 not representative). Representative data beats recent data every time.
- **Uninterrupted:** Use Basic Holdout. Avoid walk-forward optimization so model learns regime-dependent behavior.
- **No immediate retraining:** Models frozen after training. Validate through pseudo-OOS before live.

## OOS Validation Rigor

- **OOS Pseudo:** Test on unseen data (mid-2020 onward) with realistic slippage (0.5 cents/share) in Portfolio Strategy.
- **OOS Live:** Actual live performance.
- **Rule:** OOS Live must replicate OOS Pseudo. If not, do not go live.
- **Representative training:** 99% of models replicate when setup is correct.

## Buy Rules Alignment

Align with strongest factors and FactSet/P123 Point-in-Time data. Buy rules activate relevant trees without deleting broader knowledge.

## Full 6-Phase Workflow: Probe → Sense → Respond → Verify → Deploy → Confirm

| Phase | Action | Key Constraint |
|-------|--------|---------------|
| **Probe** | Train once on 2003–June 2020 | One window only; never chase last 3 years |
| **Sense** | Test across 15+ hyperparameter sets | ALL must perform — if signal is real, hyperparameters don't matter |
| **Respond** | Retrain using exact same setup that passed Sense | No peeking at future; deploy the setup that worked in validation |
| **Verify** | Embed in Portfolio Strategy; test 5 years pseudo-OOS | Realistic slippage, fills, trading constraints; kill if curve breaks |
| **Deploy** | Go live with real money | Watch only; no tinkering |
| **Confirm** | Does OOS Live track OOS Pseudo? | Not to the decimal, but fingerprint must hold |

**Robustness test (Sense phase rule):** If a signal only works under one specific hyperparameter configuration, it is fragile and should not be deployed. All presets must produce positive lift.

## OOS Health Check — Tracking Test

Run monthly once live:
- Market up → does the strategy go up harder (higher beta to upside)?
- Market down → does the strategy go down less (lower beta to downside)?

If the fingerprint holds → stay. If it breaks → kill immediately. No calendar, no committee, no feeling. The model runs until the market proves it is broken.

## Model Complexity & Interpretability

Top models contain up to **65,000 decision rules trained on up to 1 billion data points.** No human can fully interpret this. No committee can approve it. That is fine — we validate, not explain.

- Each tree is a "mini ranking system": each split captures a conditional relationship, each leaf is a historically-working pattern.
- OOS Live is the compass, not intuition, not backtest confidence, not code review.

## Outlier Limit Philosophy

- **Default:** 5 sigma outlier cap (not the common 2.5 sigma).
- **Testing range:** Validate up to 10 sigma to confirm optimality.
- **Why not 2.5 sigma:** Clipping at 2.5 sigma collapses the signal gradient — all strong momentum/value stocks look identical above the cap. The model loses the ability to distinguish "strong" from "extreme."
- **Fat tails are signal, not noise.** A 10-sigma momentum breakout is information; a 2008-style volatility spike is regime data. Preserve it.

## Complex vs. Complicated (Core Mindset)

- **Complicated** (e.g., a watch): Can be disassembled, understood gear-by-gear. Cause and effect are stable. Linear models work.
- **Complex** (e.g., a rainforest / markets): Cause and effect shift. Relationships change. You cannot understand by disassembly. You can only adapt.

High-IQ bias ("Complexity Aversion"): intelligent people build elaborate models, overfit, and fall in love with their own logic. The market doesn't reward understanding — it rewards robustness and adaptation. Probe, Sense, Respond beats predict-and-hold.

## Live Deployment Checklist

1. Train 2003-2020.06
2. Test across 15+ hyperparameter sets — all must perform
3. Retrain with the exact same setup
4. Validate pseudo-OOS with realistic slippage (5-year window)
5. If equity curve breaks → kill and restart
6. If OOS Live ≠ OOS Pseudo fingerprint → kill immediately
7. Use homogeneous universes
8. Basic Holdout, no walk-forward
9. Enable Save Predictions for AIFactorValidation
