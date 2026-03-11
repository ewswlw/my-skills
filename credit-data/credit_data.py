"""
Credit Data — Bloomberg Credit Market Data Fetcher

Standalone credit market data module. Provides natural-language-driven access
to OAS spreads, CDX instruments, and excess return (ER) indices for CAD IG,
US IG, US HY, and CDX markets via Bloomberg Terminal (xbbg).

Key capabilities:
  - 80+ natural language aliases for 26 credit instruments
  - Automatic Bloomberg field selection per instrument
    (OAS → INDEX_OAS_TSY_BP, CDX → ROLL_ADJUSTED_MID_PRICE,
     ER → INDEX_EXCESS_RETURN_YTD → auto-converted to chain-linked index)
  - Bad-date corrections matching fetch_data.py DataPipeline behaviour
  - Multi-series outer-join merge with forward fill
  - Spread context: percentile, Z-score, 52-week range, regime label
  - CLI entry point for ad-hoc fetches

Prerequisites:
  Bloomberg Terminal must be open and connected.
  Install deps: uv add xbbg pandas numpy

Reference implementation: Market Data Pipeline/fetch_data.py (DataPipeline)

Usage
-----
    from credit_data import CreditData

    cd = CreditData()

    # OAS spreads
    df = cd.fetch("cad ig")
    df = cd.fetch("us ig and us hy", start_date="2020-01-01")

    # ER → cumulative index (auto-converted)
    df = cd.fetch("cad ig er")
    df = cd.fetch("us ig er", start_date="2015-01-01", periodicity="W")

    # Multiple series merged
    df = cd.fetch("cad ig, us ig, cdx ig")

    # Fetch everything
    df = cd.fetch_all()

    # Spread intelligence
    print(cd.context("cad ig"))

    # Save
    cd.save(df, "output/credit_data.csv")
"""

from __future__ import annotations

import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

import numpy as np
import pandas as pd

try:
    from xbbg import blp

    BLOOMBERG_AVAILABLE = True
except ImportError:
    BLOOMBERG_AVAILABLE = False
    logging.getLogger(__name__).warning(
        "xbbg not installed. Run: uv add xbbg  |  Bloomberg Terminal must be open."
    )

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

# ── Bloomberg field constants ──────────────────────────────────────────────────
OAS_FIELD = "INDEX_OAS_TSY_BP"
ER_FIELD = "INDEX_EXCESS_RETURN_YTD"
CDX_FIELD = "ROLL_ADJUSTED_MID_PRICE"
PX_LAST = "PX_LAST"

# ── Defaults ───────────────────────────────────────────────────────────────────
DEFAULT_START_DATE = "2002-11-01"
DEFAULT_END_DATE = datetime.now().strftime("%Y-%m-%d")
DEFAULT_PERIODICITY = "D"
DEFAULT_FILL = "ffill"

# ── Instrument Registry ────────────────────────────────────────────────────────
# col_name → (bloomberg_ticker, bloomberg_field, description, category)
# category: 'cad_oas' | 'us_oas' | 'cdx' | 'cdx_er' | 'cad_er' | 'us_er'
INSTRUMENT_REGISTRY: dict[str, tuple[str, str, str, str]] = {
    # ── CAD IG OAS ─────────────────────────────────────────────────────────────
    "cad_oas": (
        "I05510CA Index", OAS_FIELD, "CAD IG All Sectors", "cad_oas",
    ),
    "cad_short_oas": (
        "I34227CA Index", OAS_FIELD, "CAD IG Short (1-5Y)", "cad_oas",
    ),
    "cad_long_oas": (
        "I34229CA Index", OAS_FIELD, "CAD IG Long (10Y+)", "cad_oas",
    ),
    "cad_credit_spreads_fins": (
        "I05523CA Index", OAS_FIELD, "CAD IG Financials", "cad_oas",
    ),
    "cad_credit_spreads_non_fins_ex_uts": (
        "I05520CA Index", OAS_FIELD, "CAD IG Non-Fins ex Utilities", "cad_oas",
    ),
    "cad_credit_spreads_uts": (
        "I05517CA Index", OAS_FIELD, "CAD IG Utilities", "cad_oas",
    ),
    "cad_credit_spreads_a_credits": (
        "I05515CA Index", OAS_FIELD, "CAD IG A-rated", "cad_oas",
    ),
    "cad_credit_spreads_bbb_credits": (
        "I05516CA Index", OAS_FIELD, "CAD IG BBB-rated", "cad_oas",
    ),
    "cad_credit_spreads_provs": (
        "I34069CA Index", OAS_FIELD, "CAD Provinces", "cad_oas",
    ),
    "cad_credit_spreads_provs_longs": (
        "I34336CA Index", OAS_FIELD, "CAD Provinces Long", "cad_oas",
    ),
    # ── US OAS ─────────────────────────────────────────────────────────────────
    "us_ig_oas": (
        "LUACTRUU Index", OAS_FIELD, "US IG (Bloomberg US Agg Corp)", "us_oas",
    ),
    "us_hy_oas": (
        "LF98TRUU Index", OAS_FIELD, "US HY (Bloomberg US HY)", "us_oas",
    ),
    # ── CDX spreads (roll-adjusted mid price) ──────────────────────────────────
    "cdx_ig": (
        "IBOXUMAE MKIT Curncy", CDX_FIELD, "CDX IG (roll-adjusted)", "cdx",
    ),
    "cdx_hy": (
        "IBOXHYSE MKIT Curncy", CDX_FIELD, "CDX HY (roll-adjusted)", "cdx",
    ),
    # ── CDX total return indices (PX_LAST — already a cumulative index) ────────
    "cdx_ig_er": (
        "ERIXCDIG Index", PX_LAST, "CDX IG Excess Return Index", "cdx_er",
    ),
    "cdx_hy_er": (
        "UISYMH5S Index", PX_LAST, "CDX HY Excess Return Index", "cdx_er",
    ),
    # ── CAD ER YTD → auto-converted to chain-linked index at fetch time ────────
    "cad_ig_er": (
        "I05510CA Index", ER_FIELD, "CAD IG Excess Return YTD", "cad_er",
    ),
    "cad_ig_short_er": (
        "I34227CA Index", ER_FIELD, "CAD IG Short Excess Return YTD", "cad_er",
    ),
    "cad_ig_long_er": (
        "I34229CA Index", ER_FIELD, "CAD IG Long Excess Return YTD", "cad_er",
    ),
    "cad_credit_spreads_provs_er": (
        "I34069CA Index", ER_FIELD, "CAD Provinces ER YTD", "cad_er",
    ),
    "cad_credit_spreads_provs_longs_er": (
        "I34336CA Index", ER_FIELD, "CAD Provinces Long ER YTD", "cad_er",
    ),
    # ── US ER YTD → auto-converted to chain-linked index at fetch time ─────────
    "us_ig_er": (
        "LUACTRUU Index", ER_FIELD, "US IG Excess Return YTD", "us_er",
    ),
    "us_hy_er": (
        "LF98TRUU Index", ER_FIELD, "US HY Excess Return YTD", "us_er",
    ),
}

# ── Known bad data dates ───────────────────────────────────────────────────────
# Mirrors DEFAULT_BAD_DATES in Market Data Pipeline/fetch_data.py.
# Actions: 'use_previous' | 'forward_fill' | 'interpolate'
BAD_DATES: dict[str, dict[str, str]] = {
    "2005-11-15": {
        "column": "cad_oas",
        "action": "use_previous",
    },
    "2005-11-15_non_fins": {
        "column": "cad_credit_spreads_non_fins_ex_uts",
        "action": "use_previous",
    },
    "2005-11-15_bbb": {
        "column": "cad_credit_spreads_bbb_credits",
        "action": "use_previous",
    },
    "2005-11-15_cad_ig_er": {
        "column": "cad_ig_er_index",
        "action": "use_previous",
    },
}

# ── Alias Map ──────────────────────────────────────────────────────────────────
# Natural language phrase (lowercase) → column name in INSTRUMENT_REGISTRY.
# Matched longest-first at runtime to prevent short-phrase collisions.
ALIAS_MAP: dict[str, str] = {
    # CAD IG broad
    "cad investment grade":             "cad_oas",
    "canadian investment grade":        "cad_oas",
    "canadian ig":                      "cad_oas",
    "canadian credit":                  "cad_oas",
    "canada credit":                    "cad_oas",
    "canada ig":                        "cad_oas",
    "cad credit":                       "cad_oas",
    "cad spreads":                      "cad_oas",
    "cad ig oas":                       "cad_oas",
    "cad oas":                          "cad_oas",
    "i05510ca":                         "cad_oas",
    "cad ig":                           "cad_oas",
    # CAD Short
    "cad short ig":                     "cad_short_oas",
    "cad short spreads":                "cad_short_oas",
    "cad short oas":                    "cad_short_oas",
    "cad 1-5":                          "cad_short_oas",
    "i34227ca":                         "cad_short_oas",
    "cad short":                        "cad_short_oas",
    # CAD Long
    "cad long ig":                      "cad_long_oas",
    "cad long spreads":                 "cad_long_oas",
    "cad long oas":                     "cad_long_oas",
    "cad 10+":                          "cad_long_oas",
    "i34229ca":                         "cad_long_oas",
    "cad long":                         "cad_long_oas",
    # CAD Financials
    "cad financial spreads":            "cad_credit_spreads_fins",
    "canadian financials":              "cad_credit_spreads_fins",
    "cad financials":                   "cad_credit_spreads_fins",
    "cad fins spreads":                 "cad_credit_spreads_fins",
    "i05523ca":                         "cad_credit_spreads_fins",
    "cad fins":                         "cad_credit_spreads_fins",
    # CAD Non-Fins
    "non fins ex utilities":            "cad_credit_spreads_non_fins_ex_uts",
    "non fins ex utils":                "cad_credit_spreads_non_fins_ex_uts",
    "cad non financials":               "cad_credit_spreads_non_fins_ex_uts",
    "cad industrials":                  "cad_credit_spreads_non_fins_ex_uts",
    "cad non-fins":                     "cad_credit_spreads_non_fins_ex_uts",
    "cad non fins":                     "cad_credit_spreads_non_fins_ex_uts",
    "i05520ca":                         "cad_credit_spreads_non_fins_ex_uts",
    # CAD Utilities
    "canadian utilities":               "cad_credit_spreads_uts",
    "cad utilities":                    "cad_credit_spreads_uts",
    "i05517ca":                         "cad_credit_spreads_uts",
    "cad uts":                          "cad_credit_spreads_uts",
    # CAD A Credits
    "cad a credits":                    "cad_credit_spreads_a_credits",
    "cad single a":                     "cad_credit_spreads_a_credits",
    "cad a rated":                      "cad_credit_spreads_a_credits",
    "cad a-rated":                      "cad_credit_spreads_a_credits",
    "i05515ca":                         "cad_credit_spreads_a_credits",
    "a credits":                        "cad_credit_spreads_a_credits",
    "cad a":                            "cad_credit_spreads_a_credits",
    # CAD BBB Credits
    "cad bbb credits":                  "cad_credit_spreads_bbb_credits",
    "cad triple b":                     "cad_credit_spreads_bbb_credits",
    "cad bbb rated":                    "cad_credit_spreads_bbb_credits",
    "cad bbb-rated":                    "cad_credit_spreads_bbb_credits",
    "i05516ca":                         "cad_credit_spreads_bbb_credits",
    "bbb credits":                      "cad_credit_spreads_bbb_credits",
    "cad bbb":                          "cad_credit_spreads_bbb_credits",
    # CAD Provinces
    "canadian provinces":               "cad_credit_spreads_provs",
    "provincial spreads":               "cad_credit_spreads_provs",
    "cad provinces":                    "cad_credit_spreads_provs",
    "cad provs spreads":                "cad_credit_spreads_provs",
    "i34069ca":                         "cad_credit_spreads_provs",
    "cad provs":                        "cad_credit_spreads_provs",
    "provs":                            "cad_credit_spreads_provs",
    # CAD Provinces Long
    "cad long provinces":               "cad_credit_spreads_provs_longs",
    "cad provs long":                   "cad_credit_spreads_provs_longs",
    "long provincials":                 "cad_credit_spreads_provs_longs",
    "long provs":                       "cad_credit_spreads_provs_longs",
    "i34336ca":                         "cad_credit_spreads_provs_longs",
    # US IG
    "us investment grade":              "us_ig_oas",
    "us ig spreads":                    "us_ig_oas",
    "us ig oas":                        "us_ig_oas",
    "american ig":                      "us_ig_oas",
    "luactruu":                         "us_ig_oas",
    "luac":                             "us_ig_oas",
    "us ig":                            "us_ig_oas",
    # US HY
    "us high yield":                    "us_hy_oas",
    "us hy spreads":                    "us_hy_oas",
    "us hy oas":                        "us_hy_oas",
    "junk spreads":                     "us_hy_oas",
    "junk bonds":                       "us_hy_oas",
    "lf98truu":                         "us_hy_oas",
    "lf98":                             "us_hy_oas",
    "us hy":                            "us_hy_oas",
    # CDX IG spread
    "cdx investment grade":             "cdx_ig",
    "cdx ig spread":                    "cdx_ig",
    "iboxumae":                         "cdx_ig",
    "ibox ig":                          "cdx_ig",
    "cdx ig":                           "cdx_ig",
    # CDX HY spread
    "cdx high yield":                   "cdx_hy",
    "cdx hy spread":                    "cdx_hy",
    "iboxhyse":                         "cdx_hy",
    "ibox hy":                          "cdx_hy",
    "cdx hy":                           "cdx_hy",
    # CDX IG ER index
    "cdx ig excess return":             "cdx_ig_er",
    "cdx ig er index":                  "cdx_ig_er",
    "erixcdig":                         "cdx_ig_er",
    "erix":                             "cdx_ig_er",
    "cdx ig er":                        "cdx_ig_er",
    # CDX HY ER index
    "cdx hy excess return":             "cdx_hy_er",
    "cdx hy er index":                  "cdx_hy_er",
    "uisymh5s":                         "cdx_hy_er",
    "cdx hy er":                        "cdx_hy_er",
    # CAD IG ER
    "cad ig excess return":             "cad_ig_er",
    "cad ig er index":                  "cad_ig_er",
    "cad excess return":                "cad_ig_er",
    "cad er index":                     "cad_ig_er",
    "cad ig er":                        "cad_ig_er",
    "cad er":                           "cad_ig_er",
    # CAD Short ER
    "cad short excess return":          "cad_ig_short_er",
    "cad short er index":               "cad_ig_short_er",
    "cad short er":                     "cad_ig_short_er",
    # CAD Long ER
    "cad long excess return":           "cad_ig_long_er",
    "cad long er index":                "cad_ig_long_er",
    "cad long er":                      "cad_ig_long_er",
    # CAD Provs ER
    "cad provs excess return":          "cad_credit_spreads_provs_er",
    "provincial er":                    "cad_credit_spreads_provs_er",
    "cad provs er":                     "cad_credit_spreads_provs_er",
    # CAD Provs Long ER
    "cad provs long er":                "cad_credit_spreads_provs_longs_er",
    "long provs er":                    "cad_credit_spreads_provs_longs_er",
    # US IG ER
    "us investment grade excess return": "us_ig_er",
    "us ig excess return":              "us_ig_er",
    "us ig er index":                   "us_ig_er",
    "us ig er":                         "us_ig_er",
    # US HY ER
    "us high yield excess return":      "us_hy_er",
    "us hy excess return":              "us_hy_er",
    "us hy er index":                   "us_hy_er",
    "us hy er":                         "us_hy_er",
}

# ── "Fetch all" trigger phrases ────────────────────────────────────────────────
FETCH_ALL_TRIGGERS: set[str] = {
    "all credit data", "all credit", "full dataset", "pull everything",
    "fetch everything", "everything", "all spreads", "all oas", "all series",
    "complete dataset", "all indices", "all indexes", "fetch all",
}

# ── Regime thresholds (percentile of full history) ────────────────────────────
REGIME_THRESHOLDS = {"DISTRESSED": 85, "WIDE": 65, "FAIR": 35}


# ══════════════════════════════════════════════════════════════════════════════
class CreditData:
    """
    Standalone Bloomberg credit market data fetcher.

    Covers all major CAD IG, US IG, US HY, and CDX instruments.

    - Natural language alias resolution (26 instruments, 80+ phrase aliases)
    - Automatic Bloomberg field selection per instrument
    - ER YTD → chain-linked cumulative index (exact algorithm from fetch_data.py)
    - Known bad-date correction
    - Multi-series merge: outer join + configurable fill
    - Spread context: percentile / Z-score / 52-week range / regime label

    Requires active Bloomberg Terminal + xbbg installed.
    """

    def __init__(
        self,
        start_date: str = DEFAULT_START_DATE,
        end_date: Optional[str] = None,
        periodicity: str = DEFAULT_PERIODICITY,
        fill: str = DEFAULT_FILL,
        bad_dates: Optional[dict] = None,
    ) -> None:
        """
        Args:
            start_date: History start date. Defaults to '2002-11-01'.
            end_date: History end date. Defaults to today.
            periodicity: 'D' (daily), 'W' (weekly), or 'M' (monthly).
            fill: NaN fill method after merge: 'ffill', 'bfill', or None.
            bad_dates: Override default bad-date correction map.
        """
        self.start_date = start_date
        self.end_date = end_date or DEFAULT_END_DATE
        self.periodicity = periodicity
        self.fill = fill
        self.bad_dates = bad_dates if bad_dates is not None else BAD_DATES.copy()

    # ── Public API ─────────────────────────────────────────────────────────────

    def fetch(
        self,
        query: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        periodicity: Optional[str] = None,
    ) -> pd.DataFrame:
        """
        Resolve a natural language query and fetch data from Bloomberg.

        Args:
            query: e.g. "cad ig", "us hy er", "cad ig and us ig", "all spreads".
            start_date: Override instance start_date for this call.
            end_date: Override instance end_date for this call.
            periodicity: Override periodicity ('D', 'W', 'M') for this call.

        Returns:
            DataFrame with DatetimeIndex. One column per instrument.
            ER YTD columns are auto-converted to chain-linked cumulative indices
            and renamed '<col>_index'.

        Raises:
            ImportError: If xbbg is not installed or Bloomberg Terminal is closed.
        """
        self._require_bloomberg()

        q = query.lower().strip()
        if q in FETCH_ALL_TRIGGERS:
            return self.fetch_all(
                start_date=start_date,
                end_date=end_date,
                periodicity=periodicity,
            )

        col_names = self.resolve(query)
        if not col_names:
            logger.warning("No instruments resolved for query: '%s'", query)
            return pd.DataFrame()

        return self._fetch_columns(
            col_names,
            start_date=start_date or self.start_date,
            end_date=end_date or self.end_date,
            periodicity=periodicity or self.periodicity,
        )

    def fetch_all(
        self,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        periodicity: Optional[str] = None,
    ) -> pd.DataFrame:
        """
        Fetch every instrument in the registry and merge into one DataFrame.

        Returns:
            DataFrame with all 26 credit instruments as columns.
            ER columns are returned as chain-linked cumulative indices.
        """
        self._require_bloomberg()
        return self._fetch_columns(
            list(INSTRUMENT_REGISTRY.keys()),
            start_date=start_date or self.start_date,
            end_date=end_date or self.end_date,
            periodicity=periodicity or self.periodicity,
        )

    def resolve(self, query: str) -> list[str]:
        """
        Map a natural language query to a list of INSTRUMENT_REGISTRY column names.

        Uses longest-first alias matching with phrase consumption to prevent
        shorter sub-phrase collisions. After "cad ig er" is matched and consumed,
        "cad ig" cannot re-match the same characters, ensuring "cad ig er" never
        also returns cad_oas as a side-effect.

        Args:
            query: Natural language query string (case-insensitive). Multiple
                instruments can be combined: "cad ig and us hy", "cad ig, cad bbb".

        Returns:
            Ordered list of column names from INSTRUMENT_REGISTRY.
            Empty list if nothing matched.

        Examples:
            resolve("cad ig er")           → ['cad_ig_er']   (not also 'cad_oas')
            resolve("cad ig and us hy")    → ['cad_oas', 'us_hy_oas']
            resolve("all credit data")     → all registry keys (handled in fetch)
        """
        q = query.lower().strip()

        # Direct column name lookup (e.g. "cad_oas")
        normalised = q.replace(" ", "_")
        if normalised in INSTRUMENT_REGISTRY:
            return [normalised]

        found: list[str] = []
        # 'remaining' tracks unmatched characters. After each match, the matched
        # characters are replaced with spaces so shorter sub-phrases cannot re-fire
        # on the same region. Equal-length replacement preserves offsets for any
        # subsequent matches in other parts of the query.
        remaining = q
        for alias in sorted(ALIAS_MAP, key=len, reverse=True):
            if alias in remaining:
                col = ALIAS_MAP[alias]
                if col not in found:
                    found.append(col)
                remaining = remaining.replace(alias, " " * len(alias), 1)

        return found

    def context(self, query: str) -> str:
        """
        Generate a spread intelligence summary for the given query.

        Computes for each resolved OAS/CDX instrument:
          - Current level (bps)
          - Full-history percentile rank
          - 5-year percentile rank
          - Z-score vs. 5-year window
          - 52-week range bar
          - Regime label: TIGHT / FAIR / WIDE / DISTRESSED

        Args:
            query: Natural language query for one or more OAS/CDX instruments.

        Returns:
            Formatted multi-line string. Pipe to print() for display.
        """
        self._require_bloomberg()

        col_names = self.resolve(query)
        if not col_names:
            return f"No instrument resolved for '{query}'"

        spread_cols = [
            c for c in col_names
            if INSTRUMENT_REGISTRY.get(c, (None, None))[1] in (OAS_FIELD, CDX_FIELD)
        ]
        if not spread_cols:
            return (
                f"context() supports OAS/CDX instruments only.\n"
                f"'{query}' resolved to: {col_names}\n"
                "Use fetch() to retrieve ER data."
            )

        df = self._fetch_columns(
            spread_cols,
            start_date=self.start_date,
            end_date=self.end_date,
            periodicity=self.periodicity,
        )
        if df is None or df.empty:
            return "No data returned from Bloomberg."

        lines: list[str] = []
        for col in spread_cols:
            if col not in df.columns:
                continue
            _, _, desc, _ = INSTRUMENT_REGISTRY[col]
            ticker = INSTRUMENT_REGISTRY[col][0]
            series = df[col].dropna()
            if series.empty:
                continue

            current = float(series.iloc[-1])

            # Full-history percentile
            full_pctile = float((series < current).mean() * 100)

            # 5-year percentile + Z-score
            cutoff_5y = series.index[-1] - pd.DateOffset(years=5)
            s5y = series[series.index >= cutoff_5y]
            pctile_5y = float((s5y < current).mean() * 100) if not s5y.empty else float("nan")
            zscore_5y = (
                float((current - s5y.mean()) / s5y.std())
                if not s5y.empty and s5y.std() > 0
                else 0.0
            )

            # 52-week range bar
            cutoff_52w = series.index[-1] - pd.DateOffset(weeks=52)
            s52w = series[series.index >= cutoff_52w]
            w52_low = float(s52w.min())
            w52_high = float(s52w.max())
            w52_rng = w52_high - w52_low
            w52_pos = (current - w52_low) / w52_rng if w52_rng > 0 else 0.5
            bar_fill = max(0, min(10, int(w52_pos * 10)))
            bar = "█" * bar_fill + "░" * (10 - bar_fill)

            # Regime label
            if full_pctile >= REGIME_THRESHOLDS["DISTRESSED"]:
                regime = "DISTRESSED"
            elif full_pctile >= REGIME_THRESHOLDS["WIDE"]:
                regime = "WIDE"
            elif full_pctile >= REGIME_THRESHOLDS["FAIR"]:
                regime = "FAIR"
            else:
                regime = "TIGHT"

            header = f"{desc}  ({ticker})"
            sep = "─" * max(len(header) + 4, 58)
            lines += [
                "",
                header,
                sep,
                f"  Current:             {current:>8.1f} bps",
                f"  Full-History Pctile: {full_pctile:>5.0f}th",
                f"  5-Year Pctile:       {pctile_5y:>5.0f}th",
                f"  Z-Score (5Y):        {zscore_5y:>+8.2f}",
                f"  52-Week Range:  {w52_low:.0f}–{w52_high:.0f} bps   {bar} {w52_pos * 100:.0f}%",
                f"  Regime:              {regime}",
            ]

        return "\n".join(lines).strip() if lines else f"No context available for '{query}'"

    def save(self, df: pd.DataFrame, path: str) -> None:
        """
        Save a DataFrame to CSV (UTF-8).

        Args:
            df: DataFrame returned by fetch() or fetch_all().
            path: Destination file path. Parent directories are created if needed.
        """
        out = Path(path)
        out.parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(out, encoding="utf-8")
        logger.info("Saved %d rows × %d cols → %s", len(df), len(df.columns), out)

    # ── Internal helpers ───────────────────────────────────────────────────────

    def _require_bloomberg(self) -> None:
        """Raise a clear ImportError if xbbg is unavailable."""
        if not BLOOMBERG_AVAILABLE:
            raise ImportError(
                "xbbg is not installed. Run: uv add xbbg\n"
                "Bloomberg Terminal must be open and connected before fetching data."
            )

    def _get_periodicity(self, per: str) -> str:
        """Normalise periodicity string to Bloomberg format."""
        mapping = {
            "D": "DAILY",   "DAILY":   "DAILY",
            "W": "WEEKLY",  "WEEKLY":  "WEEKLY",
            "M": "MONTHLY", "MONTHLY": "MONTHLY",
        }
        return mapping.get(per.upper(), "DAILY")

    def _fetch_columns(
        self,
        col_names: list[str],
        start_date: str,
        end_date: str,
        periodicity: str,
    ) -> pd.DataFrame:
        """
        Batch-fetch a list of registry column names from Bloomberg.

        Groups by Bloomberg field to minimise API round-trips:
          - All OAS tickers → one blp.bdh() call with INDEX_OAS_TSY_BP
          - All CDX tickers → one call with ROLL_ADJUSTED_MID_PRICE
          - All PX_LAST tickers → one call with PX_LAST
          - All ER tickers  → one call with INDEX_EXCESS_RETURN_YTD, then
                              auto-converted via _convert_er_to_index()

        Returns merged DataFrame with bad-date corrections applied.
        """
        per = self._get_periodicity(periodicity)

        # Group: field → [(ticker, col_name), ...]
        field_groups: dict[str, list[tuple[str, str]]] = {}
        for col in col_names:
            spec = INSTRUMENT_REGISTRY.get(col)
            if spec is None:
                logger.warning("'%s' not in INSTRUMENT_REGISTRY — skipped.", col)
                continue
            ticker, field, _, _ = spec
            field_groups.setdefault(field, []).append((ticker, col))

        frames: list[pd.DataFrame] = []
        for field, pairs in field_groups.items():
            # Guard: deduplicate on (ticker) within a field group. If two col_names
            # share the exact same (ticker, field), only the first is kept to avoid
            # silent overwrite in t2col. This should never happen in a well-formed
            # INSTRUMENT_REGISTRY but is a safety net for future extensions.
            seen_tickers: set[str] = set()
            deduped_pairs: list[tuple[str, str]] = []
            for ticker, col_name in pairs:
                if ticker not in seen_tickers:
                    deduped_pairs.append((ticker, col_name))
                    seen_tickers.add(ticker)
                else:
                    logger.warning(
                        "Duplicate ticker '%s' for field '%s' — '%s' skipped.",
                        ticker, field, col_name,
                    )
            pairs = deduped_pairs
            tickers = [t for t, _ in pairs]
            t2col = {t: c for t, c in pairs}

            logger.info(
                "Bloomberg fetch: %d ticker(s), field=%s, %s→%s, per=%s",
                len(tickers), field, start_date, end_date, per,
            )

            try:
                raw = blp.bdh(
                    tickers=tickers,
                    flds=field,
                    start_date=start_date,
                    end_date=end_date,
                    Per=per,
                )
            except Exception as exc:
                logger.error(
                    "Bloomberg fetch failed for field '%s': %s\n"
                    "  ↳ Ensure Bloomberg Terminal is open and connected.",
                    field, exc,
                )
                continue

            if raw is None or raw.empty:
                logger.warning("Empty response for field '%s'.", field)
                continue

            # Flatten MultiIndex (ticker, field) → column name
            chunk = pd.DataFrame(index=raw.index)
            for ticker in tickers:
                col_name = t2col[ticker]
                key_multi = (ticker, field)
                if key_multi in raw.columns:
                    chunk[col_name] = raw[key_multi]
                elif ticker in raw.columns:
                    # Single-ticker fallback (flat columns)
                    chunk[col_name] = raw[ticker]
                else:
                    logger.warning(
                        "(%s, %s) not found in Bloomberg response.", ticker, field
                    )

            # ER YTD → chain-linked cumulative index
            if field == ER_FIELD:
                chunk = self._convert_er_to_index(chunk)

            frames.append(chunk)

        if not frames:
            return pd.DataFrame()

        # Outer-join merge
        result = frames[0]
        for frame in frames[1:]:
            result = result.join(frame, how="outer")

        # Apply fill (post-first-valid-index only)
        if self.fill in ("ffill", "bfill"):
            for col in result.columns:
                fvi = result[col].first_valid_index()
                if fvi is not None:
                    mask = result.index >= fvi
                    if self.fill == "ffill":
                        result.loc[mask, col] = result.loc[mask, col].ffill()
                    else:
                        result.loc[mask, col] = result.loc[mask, col].bfill()

        result = self._apply_bad_dates(result)
        return result

    def _convert_er_to_index(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Convert Bloomberg INDEX_EXCESS_RETURN_YTD columns to chain-linked
        cumulative indices starting at 100.

        Algorithm (identical to DataPipeline.convert_er_ytd_to_index in
        Market Data Pipeline/fetch_data.py — kept in sync to prevent drift):

          For each calendar year:
            index_value(date) = prev_year_end_value × (1 + YTD_return(date) / 100)

          At year-end the closing index value becomes the next year's base.

        Returns a new DataFrame; columns renamed '<original>_index'.
        """
        result = pd.DataFrame(index=df.index)
        years = [d.year for d in df.index]

        for col in df.columns:
            idx_vals = pd.Series(np.nan, index=df.index, dtype=float)
            prev_year_end = 100.0

            for year in sorted(set(years)):
                year_dates = df.index[[i for i, y in enumerate(years) if y == year]]
                if len(year_dates) == 0:
                    continue

                for date in year_dates:
                    raw_val = df.loc[date, col]
                    if pd.notna(raw_val):
                        idx_vals.loc[date] = prev_year_end * (1.0 + float(raw_val) / 100.0)

                last_date = year_dates[-1]
                if pd.notna(idx_vals.loc[last_date]):
                    prev_year_end = float(idx_vals.loc[last_date])

            # Fill residual NaNs
            idx_vals = idx_vals.ffill() if self.fill == "ffill" else idx_vals.bfill()
            result[f"{col}_index"] = idx_vals

        return result

    def _apply_bad_dates(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Apply known bad-date corrections.

        Mirrors DataPipeline.clean_data() in Market Data Pipeline/fetch_data.py.
        Supported actions: 'use_previous', 'forward_fill', 'interpolate'.
        """
        cleaned = df.copy()

        for date_key, info in self.bad_dates.items():
            column = info.get("column")
            action = info.get("action")

            if not column or column not in cleaned.columns:
                continue

            # Key format may be '2005-11-15' or '2005-11-15_non_fins'
            raw_date = date_key.split("_")[0] if "_" in date_key else date_key
            try:
                date = pd.to_datetime(raw_date)
            except Exception:
                logger.warning("Cannot parse date from bad_dates key: '%s'", date_key)
                continue

            if date not in cleaned.index:
                continue

            if action == "use_previous":
                prev = cleaned.loc[cleaned.index < date, column]
                if not prev.empty:
                    cleaned.loc[date, column] = prev.iloc[-1]

            elif action == "forward_fill":
                cleaned[column] = cleaned[column].ffill()

            elif action == "interpolate":
                before_idx = cleaned.index.get_indexer([date], method="pad")[0]
                after_idx = cleaned.index.get_indexer([date], method="backfill")[0]
                if (
                    before_idx >= 0
                    and after_idx < len(cleaned)
                    and before_idx != after_idx
                ):
                    b_date = cleaned.index[before_idx]
                    a_date = cleaned.index[after_idx]
                    b_val = cleaned.loc[b_date, column]
                    a_val = cleaned.loc[a_date, column]
                    days = (a_date - b_date).days
                    ratio = (date - b_date).days / days if days else 0.0
                    cleaned.loc[date, column] = b_val + (a_val - b_val) * ratio

        return cleaned


# ── CLI Entry Point ────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Fetch credit market data from Bloomberg.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  uv run python credit_data.py "cad ig"
  uv run python credit_data.py "us ig and us hy" --start 2020-01-01
  uv run python credit_data.py "cad ig er" --out output.csv
  uv run python credit_data.py --context "cad ig"
  uv run python credit_data.py --context "us hy"
  uv run python credit_data.py --all --out full_credit.csv
  uv run python credit_data.py "cad bbb" --freq W --start 2018-01-01
        """,
    )
    parser.add_argument("query", nargs="?", default="", help="Natural language query")
    parser.add_argument("--start",   default=DEFAULT_START_DATE, help="Start date YYYY-MM-DD")
    parser.add_argument("--end",     default=None,               help="End date YYYY-MM-DD")
    parser.add_argument("--freq",    default="D",                help="Periodicity: D | W | M")
    parser.add_argument("--out",     default=None,               help="Output CSV path")
    parser.add_argument("--all",     action="store_true",        help="Fetch all instruments")
    parser.add_argument("--context", action="store_true",        help="Print spread context")
    args = parser.parse_args()

    cd = CreditData(
        start_date=args.start,
        end_date=args.end,
        periodicity=args.freq,
    )

    if args.context:
        if not args.query:
            print("Error: --context requires a query. Example: --context \"cad ig\"")
            sys.exit(1)
        print(cd.context(args.query))
        sys.exit(0)

    df = cd.fetch_all() if args.all else cd.fetch(args.query)

    if df.empty:
        print("No data returned. Check query or Bloomberg connection.")
        sys.exit(1)

    print(f"\nFetched: {len(df)} rows × {len(df.columns)} columns")
    print(f"Date range: {df.index[0].date()} → {df.index[-1].date()}")
    print(f"Columns: {', '.join(df.columns.tolist())}")
    print(df.tail(5).to_string())

    if args.out:
        cd.save(df, args.out)
