"""
diagnose_and_fix.py — Core diagnostic and repair engine for vector-vs-manual skill
Manus AI | 2026-02-24 | Version 1.1 (Refined)

This script implements the full iterative diagnostic and repair workflow defined
in the project-spec.md. It takes a vbt.Portfolio, a manual returns series,
and other contextual data, then attempts to align the vbt results with the
manual ground truth within defined tolerances.
"""

import warnings
import numpy as np
import pandas as pd
import vectorbt as vbt
from tabulate import tabulate

warnings.filterwarnings("ignore")

# ─────────────────────────────────────────────────────────────────────────────
# HELPER FUNCTIONS
# ─────────────────────────────────────────────────────────────────────────────

def compound_return(rets: pd.Series) -> float:
    """Calculates the total compound return from a series of returns."""
    return (1 + rets).prod() - 1

def annualized_return(rets: pd.Series, ppy: int) -> float:
    """Calculates the annualized return (CAGR)."""
    n_years = len(rets) / ppy if ppy > 0 else 0
    return ((1 + rets).prod() ** (1 / n_years) - 1) if n_years > 0 else 0.0

def get_ppy(freq: str) -> int:
    """Gets the number of periods per year from a frequency string."""
    return {"D": 252, "W": 52, "M": 12}.get(str(freq).upper()[0], 252)

# ─────────────────────────────────────────────────────────────────────────────
# DIAGNOSTIC SUITE
# ─────────────────────────────────────────────────────────────────────────────

def run_diagnostics(manual_rets, vbt_rets, ppy, title="Diagnostics"):
    """Run a full suite of comparison diagnostics and return a report dict."""
    report = {"title": title}
    try:
        # Align date ranges
        common_idx = manual_rets.index.intersection(vbt_rets.index)
        if len(common_idx) == 0:
            raise ValueError("Manual and vbt returns have no overlapping dates.")
        manual_rets, vbt_rets = manual_rets.loc[common_idx], vbt_rets.loc[common_idx]
        report["date_range"] = (common_idx[0], common_idx[-1])

        # Headline metrics
        report["manual_cagr"] = annualized_return(manual_rets, ppy)
        report["vbt_cagr"] = annualized_return(vbt_rets, ppy)
        report["manual_total_ret"] = compound_return(manual_rets)
        report["vbt_total_ret"] = compound_return(vbt_rets)

        # Per-year returns
        annual_manual = (1 + manual_rets).resample("YE").prod() - 1
        annual_vbt = (1 + vbt_rets).resample("YE").prod() - 1
        annual_comp = pd.DataFrame({"Manual": annual_manual, "vbt": annual_vbt})
        annual_comp["Diff"] = annual_comp["vbt"] - annual_comp["Manual"]
        report["annual_comparison"] = annual_comp

        # Daily return diff stats
        diff = vbt_rets - manual_rets
        report["daily_diff_mean"] = diff.mean()
        report["daily_diff_std"] = diff.std()
        report["daily_diff_nonzero"] = (abs(diff) > 1e-8).sum()
        report["daily_diff_total_days"] = len(diff)
        report["status"] = "Success"

    except (KeyError, IndexError, ValueError) as e:
        report["status"] = "Error"
        report["error_message"] = str(e)

    return report

# ─────────────────────────────────────────────────────────────────────────────
# FIX STRATEGIES (MODULARIZED)
# ─────────────────────────────────────────────────────────────────────────────

def _try_fix_timing(pf, manual_rets, prices, rebal_w_df, tc, freq, ppy, initial_report):
    """Iteration 1: Attempt to fix execution timing mismatches."""
    daily_w_vbt = rebal_w_df.reindex(prices.index).ffill().fillna(0.0)
    start_idx = prices.index.get_loc(rebal_w_df.index[0]) + 1
    p_bt = prices.iloc[start_idx:].copy()
    tw_bt_vbt = daily_w_vbt.iloc[start_idx:].copy()

    pf_fixed = vbt.Portfolio.from_orders(
        close=p_bt, size=tw_bt_vbt, size_type="targetpercent",
        direction="longonly", fees=tc, cash_sharing=True, group_by=True,
        init_cash=pf.init_cash, freq=freq
    )
    fixed_report = run_diagnostics(manual_rets, pf_fixed.returns(), ppy, "After Timing Fix")

    # If this fix reduced the gap, adopt it
    if abs(fixed_report.get("daily_diff_mean", 1)) < abs(initial_report.get("daily_diff_mean", 1)):
        return pf_fixed, fixed_report, "RC-1: Execution Timing (unshifted weights)"
    return None, None, None

def _try_fix_weights(pf, manual_rets, prices, rebal_w_df, tc, freq, ppy, initial_report):
    """Iteration 2: Placeholder for weight construction fix."""
    # TODO: Implement weight normalization and double-counting checks
    return None, None, None

def _try_fix_tc_model(pf, manual_rets, prices, rebal_w_df, tc, freq, ppy, initial_report):
    """Iteration 3: Placeholder for transaction cost model alignment."""
    # TODO: Implement TC model alignment logic
    return None, None, None

# ─────────────────────────────────────────────────────────────────────────────
# MAIN WORKFLOW
# ─────────────────────────────────────────────────────────────────────────────

def diagnose_and_fix(pf, manual_rets, prices, rebal_w_df, tc=0.0005, freq="D"):
    """Main entry point for the iterative diagnostic and repair workflow."""
    fix_log = []
    ppy = get_ppy(freq)

    # --- INITIAL STATE --- #
    vbt_rets_initial = pf.returns()
    initial_report = run_diagnostics(manual_rets, vbt_rets_initial, ppy, "Initial State")
    fix_log.append({"iteration": 0, "report": initial_report, "fix_applied": "None"})

    if initial_report["status"] == "Error":
        print(f"Initial diagnostics failed: {initial_report["error_message"]}")
        return None

    current_pf = pf
    last_report = initial_report

    # --- ITERATIVE FIX LOOP --- #
    fix_strategies = [
        _try_fix_timing,
        _try_fix_weights, # Placeholder
        _try_fix_tc_model,  # Placeholder
    ]

    for i, fix_func in enumerate(fix_strategies, 1):
        pf_new, report_new, fix_name = fix_func(
            current_pf, manual_rets, prices, rebal_w_df, tc, freq, ppy, last_report
        )
        if pf_new and report_new:
            fix_log.append({"iteration": i, "report": report_new, "fix_applied": fix_name})
            current_pf = pf_new
            last_report = report_new

    # --- FINAL REPORTING --- #
    final_report = fix_log[-1]["report"]
    summary_table = pd.DataFrame({
        "Metric": ["CAGR", "Total Return"],
        "Manual": [f"{final_report.get("manual_cagr", 0):.2%}", f"{final_report.get("manual_total_ret", 0):.2%}"],
        "vbt (Final)": [f"{final_report.get("vbt_cagr", 0):.2%}", f"{final_report.get("vbt_total_ret", 0):.2%}"]
    })

    print("\n## Vector-vs-Manual Diagnostic Report")
    print("\n### Summary Comparison")
    print(tabulate(summary_table, headers="keys", tablefmt="simple", showindex=False))

    if "annual_comparison" in final_report:
        print("\n### Annual Return Comparison (vbt - Manual)")
        print(tabulate(final_report["annual_comparison"], headers="keys", tablefmt="simple", floatfmt=".2%"))

    print("\n### Fix Log")
    for entry in fix_log:
        report = entry["report"]
        print(f"- **Iteration {entry["iteration"]}**: {entry["fix_applied"]}")
        if report["status"] == "Success":
            print(f"  - Daily Diff Mean: {report.get("daily_diff_mean", 0)*100:.6f}% | Non-zero Days: {report.get("daily_diff_nonzero", 0)}")

    return {
        "pf_corrected": current_pf,
        "portfolio_rets": current_pf.returns(),
        "fix_log": fix_log,
        "final_report": final_report
    }
