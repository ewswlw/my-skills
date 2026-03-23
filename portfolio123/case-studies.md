# Portfolio123 Case Studies (Vault Exemplars)

Condensed **worked examples** and **failure modes**. Full factor tables and long narratives stay in the Obsidian vault—do not duplicate them here.

## Where the deep content lives

| Topic | Vault file (relative to vault root) |
|-------|--------------------------------------|
| Exhaustive factor/function catalog | `file dump/Portfolio123/Portfolio123 Syntax Dictionary.md` |
| Platform architecture, XML, quirks | `file dump/Portfolio123/Portfolio123 Reference.md` |
| API hybrid workflows, pitfalls | `file dump/Portfolio123/Portfolio123 API Guide.md` |
| Browser runbooks | `file dump/Portfolio123/Portfolio123 Automation.md` |
| TAA, Core Combo Canada, Advisor Small Cap, ML notes | `file dump/Portfolio123/Portfolio123 Strategies.md` |
| Practitioner / Substack synthesis | `file dump/Portfolio123/Portfolio123 Resources.md` |
| Iteration scars (UI bugs, formula landmines) | `file dump/Portfolio123/Portfolio123 Notes.md` |

If the user’s workspace does not include the vault, treat the vault paths as **optional** extended reference.

---

## TAA — Tactical Asset Allocation (ETF)

**Goal:** Rotate among a **small ETF sleeve** with **absolute momentum** filter.

| Setting | Typical value |
|---------|----------------|
| Type | **ETF** |
| Rebalance | Every 4 Weeks |
| Positions | 1 @ 100% |
| Universe | `Ticker("SPY,EFA,AGG")` (comma-separated, no spaces) |
| Ranking | **Trend Measurement** (or custom momentum composite) |
| Buy rule | **`Ret1Y%Chg > 0`** — absolute momentum |
| Sell rules | **Blank** for simple monthly/4-week rotation |

**Critical pitfall:** `TotRet(252) > 0` may **fail** with syntax errors in some contexts. The validated pattern in vault workflows is **`Ret1Y%Chg > 0`**.

**Design principle:** Smaller ETF count (e.g. 3) often beats noisy large universes; single position maximizes conviction when the model is sound.

**Source:** Vault `Portfolio123 Strategies.md` § TAA; aligns with [strategy-templates.md](strategy-templates.md) Template 1.

---

## Small Cap Alpha (multi-factor + risk)

Representative settings appear in [strategy-templates.md](strategy-templates.md) Template 2—liquidity, market-cap band, short interest, FCF filters, and **Bollinger + rank** sell logic. For **full** rule text and evolution, read **`Portfolio123 Strategies.md`** and **`Portfolio123 Notes.md`**.

---

## Core Combo Canada (hierarchical multi-factor)

**Vault-only detail:** Six dimensions (Growth, Sales, Op Income, Sentiment, Momentum, Value) with **nested weights**. Too large for this skill file—agents should open **`Portfolio123 Strategies.md` → Core Combo Canada** when the user names that model.

---

## Validation discipline

Before treating any case study as “proof”:

1. Read [strategy-validation.md](strategy-validation.md) (screen vs simulation).
2. Read [api-reference.md](api-reference.md#ui-vs-platform-rebalancing) (UI vs API rebalance semantics).
