---
name: strategy-extractor
description: "Transform academic finance research papers into actionable trading strategies with complete Bloomberg xbbg data mapping. Output is a documented specification note only — no live data is fetched, no code is executed. Only use when explicitly called with /strategy-extractor."
---

# Trading Strategy Extractor

Transform academic finance research papers into actionable, documented trading strategy specifications with complete Bloomberg xbbg field mapping. **No live data is fetched and no code is executed during this skill.** The output is a pure documentation artifact — a specification note a quant can hand to an implementer.

**Usage:** `/strategy-extractor [attach PDF | paste text | provide URL]`

---

## PREREQUISITES — Read These Files First

Before executing any step, read the following file using the Read tool:

| File | Why |
|------|-----|
| `c:\Users\Eddy\.cursor\plugins\cache\cursor-public\firecrawl\80ce444eb020b5f41b34836c553f162d6113cd6f\skills\firecrawl\SKILL.md` | Required for all URL inputs |

**If unreadable**, proceed without it and note the limitation. Do not block execution.

---

### Inlined: Exact MCP Tool Call Syntax (this env)

**Platform:** Windows 10/11, PowerShell. Workspace: `C:\Users\Eddy\Documents\Obsidian Vault\`

**Windows path → MCP URI:** Replace `\` with `/`, prepend `file:///`, encode spaces as `%20`.
Example: `C:\Users\Eddy\Documents\Obsidian Vault\file dump\paper.pdf` → `file:///C:/Users/Eddy/Documents/Obsidian%20Vault/file%20dump/paper.pdf`

**PDF conversion tool calls (use exactly as shown):**

```
Priority 1 — fastest, searchable PDFs:
  CallMcpTool(server="user-pdf-reader", toolName="read_pdf",
              arguments={"path": "C:\\Users\\Eddy\\..."})

Priority 2 — scanned/image PDFs:
  CallMcpTool(server="user-pdf-reader", toolName="smart_extract_pdf",
              arguments={"path": "C:\\Users\\Eddy\\..."})

Priority 3 — fallback:
  CallMcpTool(server="user-markitdown", toolName="convert_to_markdown",
              arguments={"url": "file:///C:/Users/Eddy/..."})

Batch (3+ PDFs) — delegate to subagent:
  Task(description="Extract PDFs", subagent_type="pdf-extractor",
       prompt="Convert these PDFs and return full markdown:\n- path1\n- path2")
```

**URL inputs:** Use Firecrawl SKILL (read it first, see Prerequisites). Primary tool: `firecrawl_scrape`. For SSRN abstract pages, scrape for the PDF link, then convert the PDF.

---

### Inlined: Critical Vault Rules (from vault-standards.mdc)

These rules govern the output file `file dump/Academic Research/strategiesextracted.md`:

1. **Frontmatter required fields:** `tags`, `created`, `updated`, `description` — update `updated` to today (`YYYY-MM-DD`) on every append
2. **Dual tagging:** Tags appear in both the YAML frontmatter list AND in a `## Tags` section at the bottom of each strategy, using `#tag` format
3. **Tag format:** lowercase, hyphens for spaces, no camelCase, no underscores — e.g., `algo-trading/backtesting` not `AlgoTrading`
4. **Indentation:** 2 spaces in YAML, never tabs
5. **Before adding new tags:** Check existing tags in the frontmatter — consolidate rather than proliferate

---

## Part I: Extraction Principles

### 1. Implementable Rules vs. Theory

Extract **only** implementable rules: exact entry/exit conditions, numerical thresholds, rebalancing frequency, position sizing. Ignore: literature reviews, academic jargon, non-actionable concepts.

Each rule must be precise enough that a quant could code it without asking a question.

### 2. Missing Information Protocol

- Write **"Not mentioned"** for any unstated parameter — never infer
- **For dates:** Use exact dates if stated. Years only → `YYYY-01-01` / `YYYY-12-31`. Unclear → "Not explicitly stated" with notes
- **NEVER assume** — unstated values are gaps, not opportunities to fill

### 3. Bloomberg xbbg Reference

| Asset Class | Ticker Format | Example |
|-------------|---------------|---------|
| Equities | `TICKER US Equity` | `AAPL US Equity` |
| Indices | `INDEX Index` | `SPX Index` |
| Fixed Income | `T 4.5 02/15/36 Govt` | CUSIP/ISIN |
| Currencies | `FX Curncy` | `EURUSD Curncy` |
| Commodities | `TICKER Comdty` | `CL1 Comdty` |
| Futures | `ES1 Index`, `CL1 Comdty` | Generic front-month |

**Common fields:**
- Price: `PX_LAST`, `PX_SETTLE`, `PX_OPEN`, `PX_HIGH`, `PX_LOW`
- Total return: `TOT_RETURN_INDEX_GROSS_DVDS`
- Volume: `VOLUME`, `TURNOVER_SHARES`
- Fundamentals: `PE_RATIO`, `BOOK_VAL_PER_SH`, `CUR_MKT_CAP`, `EV_EBITDA`, `RETURN_ON_EQUITY`
- Risk: `VOLATILITY_30D`, `VOLATILITY_90D`
- Rates: `USGG2YR Index`, `USGG10YR Index`, `USGG30YR Index`
- Macro: `GDP_YOY`, `CPI_YOY`

**Document three dictionaries per strategy:** `STRATEGY_UNIVERSE`, `BLOOMBERG_FIELDS`, `FACTOR_DEFINITIONS`

> These dictionaries are specification artifacts for a future implementer — document them based on what the paper requires. Do not call Bloomberg or execute any code.

### 4. Testability Scoring (1–10)

| Score | Meaning |
|-------|---------|
| 9–10 | Fully replicable with xbbg, ready to implement |
| 7–8 | Implementable with minor adjustments |
| 4–6 | Possible with significant modifications |
| 1–3 | Theoretical only, major barriers exist |

**Dimensions:** Data Availability (40%), Implementation Complexity (30%), Capital Requirements (15%), Research Clarity (15%).

---

## Part II: Step-by-Step Workflow

### Step 0: Classify Input → Route to Correct Tool

**Decision tree (execute exactly one branch):**

```
Input is pasted text or markdown?
  └─ Yes → Skip to Step 1 immediately

Input is a file path ending in .pdf?
  └─ 1–2 files → Use CallMcpTool directly (see Priority chain in Prerequisites)
  └─ 3+ files  → Use Task(subagent_type="pdf-extractor", ...)
                   Await response starting with "=== PDF EXTRACTION RESULTS ==="
                   Parse per-file STATUS / CONTENT / SANITIZED_PATH blocks

Input is a URL?
  └─ Read Firecrawl SKILL first (path in Prerequisites)
  └─ Call firecrawl_scrape on the URL
  └─ If content contains a PDF link → download PDF → treat as 1-file path above
  └─ If content is the paper text   → treat as pasted text, skip to Step 1
```

**For all PDF paths:** sanitize the filename first if it contains unsafe characters (keep only `A-Z a-z 0-9 space - _ .`). Rename via Shell before converting.

**On any conversion failure:** log `FAILED: [filename] — [reason]`, request text input from user, continue with successful files.

---

### Step 1: Strategy Logic Extraction

Extract only the following — in order:

1. Backtest start and end dates (CRITICAL — exact from paper)
2. Entry conditions with exact numerical thresholds
3. Exit rules and timing
4. Signal generation methodology
5. Portfolio construction rules (long-only / long-short, weighting)
6. Position sizing
7. Rebalancing frequency and timing
8. Market / regime filters

**If multiple strategies in one paper:** list all strategy names, ask the user which to extract (or 'all') before continuing.

---

### Step 2: Bloomberg xbbg Data Mapping

For each data requirement in the paper:

1. Match to a Bloomberg ticker format (Part I Section 3)
2. Map to specific Bloomberg fields
3. Build `STRATEGY_UNIVERSE` (all tickers as a dict by asset class)
4. Build `BLOOMBERG_FIELDS` (all required fields grouped by type)
5. Flag any data **not** available in Bloomberg — note alternatives and score impact

**Version note (for the implementer):** Default to xbbg v0.8.x-compatible fields (`bdh`, `bdp`, `bds`, `beqs`). If the strategy requires v1.x-only data (`yas` for bond analytics, `fieldSearch`), note this explicitly in Data Limitations.

---

### Step 3: Factor Construction

For each factor, signal, or derived variable:

```python
FACTOR_DEFINITIONS = {
    'momentum_12_1': {
        'calculation': 'Cumulative return months t-12 to t-2 (skip last month)',
        'bloomberg_fields': ['PX_LAST'],   # field name per xbbg convention
        'periodicity':  'bdh() Per="M"',   # how implementer should pull
        'adjust':       'adjust="all"',    # split + dividend adjustment required
        'lookback_period': 252,            # trading days
        'skip_period': 21,                 # trading days
        'frequency': 'monthly',
        'rebalance': 'End of month'
    },
    # one entry per factor — never infer calculation if not stated in paper
}
```

---

### Step 4: Testability Assessment

Score 1–10 on all four dimensions:

```
Data Availability     (40%): Can all required data be pulled via xbbg? Any proprietary series?
Implementation Complexity (30%): How many moving parts? ML models? Custom data pipelines?
Capital Requirements  (15%): Minimum AUM for the strategy to work economically?
Research Clarity      (15%): Are all rules stated precisely enough to implement?

Composite score = weighted sum. List specific xbbg barriers for each dimension.
```

If score < 9, list the top 3 barriers and propose workarounds.

---

### Step 5: Write Output

**Active target file:** `file dump/Academic Research/strategies extracted.md`
**Full path:** `C:\Users\Eddy\Documents\Obsidian Vault\file dump\Academic Research\strategies extracted.md`

If the active target does not exist, fall back to `file dump/Academic Research/strategiesextracted.md`. If neither exists, create the active target with Obsidian frontmatter and all required master sections.

**Before writing:**
1. Read the file (Read tool) — note current strategy count N in Part A table (new strategy = N+1)
2. Note current `updated` date in frontmatter — will be replaced with today
3. Note existing tags list — check before adding new tags

**Write sequence (do all of the following for every successful extraction):**
1. Update frontmatter: bump `updated` to today, append any new strategy-specific tags to the `tags` list (2-space indented YAML)
2. **Master summary sentence:** Update the opening paragraph under `## Master Strategy Summary` with the batch date, number of PDFs processed, number of strategies added, failures, duplicates, and any routing outcome that matters later.
3. **Study links (master list):** In the top `## Master Strategy Summary` area, maintain a numbered `### Study links (primary sources)` subsection listing every strategy’s canonical URL(s): arXiv/SSRN/journal DOI, QuantPedia/blog primary article, or — if none exists — an Obsidian `[[vault path]]` wikilink to the extracted PDF/text note. Use full `https://` markdown links with descriptive anchor text.
4. **Part A source column:** Add or update the **Primary source** column on the Part A table so each row points to the same link(s) as the master list (compact: `[arXiv](url)`, `[SSRN](url)`, `[DOI](url)`, or `[[wikilink]]`).
5. Add a new row to **Part A** (with **Primary source** filled per step 4), **Part B**, and **Part C**.
6. **Cross-Strategy Insights:** Update every subsection under `## Cross-Strategy Insights` so it reflects the full strategy set, not just the new paper. Refresh data-requirements bullets, implementation-priority groupings, and any cross-strategy conclusions affected by the new extraction.
7. **Papers Not Extracted or Skipped:** If a paper fails conversion, has no implementable strategy, is a duplicate, or is merged into an existing strategy, update this section with paper name, status, and reason. Do not leave duplicates only in chat.
8. Add new entry to Table of Contents using **Obsidian wiki links** for same-file navigation: `[[#Strategy N: Full Heading Text|Strategy N: Short label]] - **Testability: X/10**` — the `#` means "current file"; use the exact H1 heading text for the link target.
9. Add new row to Overview Matrix (if present).
10. Append new strategy section (template below) at the end of the file — **including `## Study links`** immediately after the opening `> **Core Concept**:` block and before `## Strategy Summary`.
11. After writing, audit section coverage: the strategy number must appear in Study links, Part A, Part B, Part C, TOC, Overview Matrix, the appended strategy body, and any relevant Cross-Strategy Insights / skipped-tracking rows.
12. **Candidates companion note:** Maintain `file dump/Academic Research/candidates for replication.md` as a strict filtered mirror of the active target. Include a strategy only if **both** gates pass: Testability score > 6/10 **and** at least one numeric performance target passes (reported CAGR > 15% or reported Sharpe > 1.5). Use the same values written into the strategy's `Performance Metrics` and `Testability Assessment` sections; do not use metrics that only appear in chat. Renumber the companion note's qualifying strategies sequentially from 1..N across frontmatter summary text, Study links, Part A/B/C rows, Cross-Strategy Insights, TOC, Overview Matrix, and full strategy headings. Do **not** preserve source/master strategy numbers in the candidate note. Do **not** include non-qualifying strategies anywhere in the companion note, including exclusion tables.

**Never skip a strategy** based on testability score. Every extracted strategy is appended.

---

#### Output Template

Append exactly the following structure. Do NOT wrap it in a code fence — paste it directly as markdown. Replace all `[...]` placeholders; use "Not mentioned" for anything unstated.

**Format conventions (match `strategiesextracted.md`):**
- **TOC links**: Use Obsidian wiki links `[[#Strategy N: Full Heading|Display]]` for same-file navigation — `#` = current file, exact heading text = target
- Strategy heading: H1 (`# Strategy N:`)
- Section headings: H2 (`##`)
- Blockquote uses `**Core Concept**:`
- **`## Study links`**: Required after the blockquote and before `## Strategy Summary` — bullet list of primary publication URL(s) (arXiv, SSRN, journal DOI, official blog/research page) or vault `[[wikilink]]` when no public URL; note *URL TBD* if the paper is paywalled or not yet posted
- Sample period inline in Strategy Summary; no separate Backtest Period table
- Timeframe Specifications: bullet list, not table
- Edge Hypothesis: **What specific market inefficiency** + **Why the edge persists**
- Assets Universe: include `### Bloomberg Ticker Mapping` subheading

```
---

# Strategy [N]: [Strategy Name]

> **Core Concept**: [One paragraph: what the strategy does, what signal it uses, what it trades, how it rebalances]

## Study links

- **[Author (Year)]** — *[Paper title]*. [Primary URL](https://...) · [optional secondary: PDF/DOI]
- If no public URL: vault mirror `[[path/to/extracted/note]]` and/or *Primary URL not located — TBD*

## Strategy Summary

[2–4 sentences expanding on the overview: key mechanism, edge being exploited, asset class scope]

**Sample Period**: [Start Date] to [End Date] ([N years]) | [Sample description; or "Not explicitly stated" if absent]

---

## Entry Rules

[Numbered list of exact entry conditions with thresholds. "Not mentioned" if absent.]

1. ...
2. ...

---

## Exit Rules

[Numbered list of exit conditions and timing. "Not mentioned" if absent.]

---

## Market Filters

[Regime filters, volatility conditions, macro screens. "Not mentioned" if absent.]

---

## Assets Universe

### Bloomberg Ticker Mapping

[STRATEGY_UNIVERSE and BLOOMBERG_FIELDS as python code block; group BLOOMBERG_FIELDS by type: price_data, volume, fundamentals, macro, etc.]

---

## Timeframe Specifications

- **Data Frequency**: [Daily / Weekly / Monthly]
- **Sample Period**: [Start] to [End]
- **Rebalancing**: [Frequency and timing]
- **Lookback Windows**: [List all]
- **xbbg periodicity**: Per='D' / Per='W' / Per='M'

---

## Factor Construction

[FACTOR_DEFINITIONS dictionary as python code block — document calculation, bloomberg_fields, periodicity, adjust, lookback_period, frequency, rebalance for each factor]

---

## Edge Hypothesis

**What specific market inefficiency this strategy exploits:**

- [Bullet points: market inefficiency, behavioral bias, or edge source]

**Why the edge persists:**

- [Bullet points: barriers to arbitrage, implementation costs, etc.]

---

## Performance Metrics

[Only metrics explicitly reported in the paper. "Not reported" for any missing metric.]

| Metric | Value | Notes |
|--------|-------|-------|
| CAGR | | |
| Sharpe | | |
| Max Drawdown | | |
| Volatility | | |
| Sortino | | |
| Other | | |

---

## Data Limitations

[Any required data unavailable in Bloomberg, alternative sources, and score impact]

---

## Implementation Constraints

[Transaction costs, market impact, minimum capital, regime dependencies, short-selling requirements]

---

## Testability Assessment

**Score: [X/10]**

| Dimension | Weight | Score | Notes |
|-----------|--------|-------|-------|
| Data Availability | 40% | | |
| Implementation Complexity | 30% | | |
| Capital Requirements | 15% | | |
| Research Clarity | 15% | | |

**xbbg barriers:** [Specific Bloomberg/xbbg limitations]
**Suggested workarounds:** [If score < 9]

---

## Tags

#algo-trading/backtesting #research/strategies [add 2–4 specific tags from vault taxonomy]
```

---

## Part III: Edge Cases & Error Handling

| Scenario | Handling |
|----------|----------|
| No PDF conversion tool available | Try Priority 1→2→3 MCP chain (see Prerequisites). If all fail: request text input. |
| PDF conversion returns empty (<50 chars) | Retry with next priority tool. Warn user if OCR quality low. |
| Password-protected PDF | Request unlocked version. |
| Large PDF (100+ pages) | Delegate to pdf-extractor subagent via Task tool. |
| Multiple strategies in one PDF | List all; ask user which to extract (or 'all') before Step 1. |
| Entry/exit rules not stated | Use "Not mentioned". Flag in Testability Assessment. |
| Exact dates not stated | Write "Not explicitly stated". Note any surrounding clues. |
| Multiple test periods | List all periods separately, each with its own label. |
| Proprietary/unavailable data | Document in Data Limitations. Reduce testability score. |
| No implementable strategy found | Notify user. Offer to extract theoretical framework if desired. |
| Ambiguous Bloomberg field | List 2–3 alternatives with recommendation and justification. |
| URL is SSRN abstract page | Scrape with Firecrawl → find PDF download link → convert as 1-file PDF. |
| URL returns PDF directly | Use Firecrawl to download, then convert as PDF file. |
| Active target file does not exist | Use `strategies extracted.md` if present; otherwise fall back to `strategiesextracted.md`; if neither exists, create `strategies extracted.md` with Obsidian frontmatter (tags, created, updated, description), Master Summary (Study links + Part A/B/C), Cross-Strategy Insights, Papers Not Extracted or Skipped, Table of Contents, and Overview Matrix before first append. |
| `candidates for replication.md` does not exist or is empty | Create it as a filtered companion to the active target, with frontmatter, Candidate Filter, Study links, Part A/B/C, Cross-Strategy Insights, TOC, Overview Matrix, and full sections for qualifying strategies only. Renumber qualifying strategies sequentially from 1..N; do not list non-qualifying strategies. |
| Windows path with spaces | Encode as `%20` in file:/// URIs. Use double backslashes in Python strings. |

---

## Part IV: Quality Checklist

Run through every item before writing output.

**Extraction:**
- [ ] Backtest start and end dates extracted; date format is YYYY-MM-DD
- [ ] Date extraction method noted (exact / year-only / inferred)
- [ ] All numerical thresholds taken exactly as stated in paper
- [ ] "Not mentioned" used for every unstated parameter
- [ ] Multiple strategies identified and user asked which to extract

**Bloomberg/xbbg mapping (documentation only — no data is fetched):**
- [ ] All tickers follow Bloomberg conventions (`AAPL US Equity`, `SPX Index`, etc.)
- [ ] `STRATEGY_UNIVERSE` covers all tickers grouped by asset class
- [ ] `BLOOMBERG_FIELDS` covers all required fields grouped by type
- [ ] `FACTOR_DEFINITIONS` includes `calculation`, `bloomberg_fields`, `periodicity`, `adjust`, `lookback_period`
- [ ] Price fields requiring split/dividend adjustment noted with `adjust="all"`
- [ ] Any v1.x-only fields noted in Data Limitations

**Testability:**
- [ ] Score justified with specific reasoning per dimension
- [ ] xbbg barriers listed for any score < 9
- [ ] Data limitations documented with alternatives

**Vault output:**
- [ ] Master `### Study links (primary sources)` subsection lists every strategy with working links or explicit TBD/wikilink
- [ ] Part A table includes **Primary source** column (or equivalent) matching the master list
- [ ] Master summary opening paragraph updated for the current batch, including duplicates/failures
- [ ] Cross-Strategy Insights updated to reflect the full strategy set after the new extraction
- [ ] Papers Not Extracted or Skipped updated for failed, duplicate, merged, or no-strategy inputs
- [ ] `candidates for replication.md` updated only if the strategy meets Testability > 6/10 AND (CAGR > 15% OR Sharpe > 1.5)
- [ ] `candidates for replication.md` uses candidate-local numbering 1..N only, not source/master strategy numbers
- [ ] Non-qualifying strategies omitted entirely from `candidates for replication.md`
- [ ] Each strategy section includes `## Study links` after `> **Core Concept**:` and before `## Strategy Summary`
- [ ] Appended to `file dump/Academic Research/strategies extracted.md` (or the user’s batch file, e.g. `strategies extracted 03.10.26.md`, when specified)
- [ ] TOC uses Obsidian wiki links `[[#Strategy N: Full Heading|Display]]` for same-file navigation
- [ ] Overview Matrix updated with the new strategy row
- [ ] Strategy heading uses H1: `# Strategy N: [Name]`
- [ ] Blockquote uses `> **Core Concept**:`
- [ ] Section headings use H2 (`##`); Assets Universe includes `### Bloomberg Ticker Mapping`
- [ ] Sample period inline in Strategy Summary (no separate Backtest Period table)
- [ ] Timeframe Specifications as bullet list
- [ ] Edge Hypothesis has **What specific market inefficiency** and **Why the edge persists**
- [ ] Master Summary tables (Part A, B, C) updated with new row
- [ ] File frontmatter `updated` bumped to today (YYYY-MM-DD)
- [ ] New tags added to frontmatter YAML list (2-space indent, lowercase-hyphenated)
- [ ] Template pasted as raw markdown (NOT inside a code fence)
- [ ] `## Tags` section at end of strategy with 3–6 vault-taxonomy tags
