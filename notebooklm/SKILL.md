---
name: notebooklm
description: >
  Full control over the user's NotebookLM research notebooks via MCP. Use this skill
  proactively whenever the user wants to query their stored research, ask questions about
  sources, add PDFs or URLs to a notebook, create audio overviews/podcasts/quizzes/study
  guides/mind maps, or manage notes. Trigger on: /notebooklm, "ask my notebooks", "check
  my research", "what does my [notebook] say about", "add this to NotebookLM", "create an
  audio overview", "quiz me on", "query [topic]", or any research/finance/trading question
  that likely overlaps with stored sources (macro, quant, equities, academic finance,
  AI/coding, fixed income). When in doubt — if the user's question sounds like something
  their notebooks might know — use this skill and check.
---

This skill gives Claude full, efficient control over the user's NotebookLM instance via
the `user-notebooklm-mcp` MCP server.

---

## Auth Recovery Protocol

When you see `RPC Error 16: Authentication expired` or any auth failure, work through
these steps silently — never ask the user to handle it manually unless all three fail:

1. Call `refresh_auth` — reloads cached tokens from disk (fast, no browser)
2. Retry the original operation
3. If still failing, run in terminal:
   ```powershell
   uv tool run --from notebooklm-mcp-cli nlm login
   ```
   This opens Chrome silently, captures fresh cookies, and saves them automatically.
   Then call `refresh_auth` once more and retry.

Tokens typically expire after ~24 hours of inactivity.

---

## Notebook Directory

All IDs are hardcoded for zero-latency lookups. If a call returns a not-found or invalid-ID
error, the notebook was likely deleted or recreated — run `notebook_list` to refresh, then
update this table.

| Notebook | ID | Sources | Primary Topics |
|---|---|---|---|
| **Academic Research v3** *(default)* | `436d54d7-802d-4ab9-8c7f-a28940023f26` | 43 | Academic papers, empirical finance, research studies |
| **Academic Research v2** | `933e0fc5-eb86-49ca-a2d3-5231d3614bc2` | 43 | Academic papers (second cohort) |
| **Academic Research v1** | `42266acf-1118-4b19-bf58-2e0852b6474d` | 36 | Academic papers (oldest cohort) |
| **algo trading** | `9b85bda7-ef69-4275-ae4a-34c32ced9886` | 33 | Quant strategies, alpha factors, backtesting, systematic trading |
| **Tickers** | `da0f059e-5848-421a-81be-066a4e713ca5` | 25 | Individual stocks, equity research, company analysis, earnings |
| **Portfolio123** | `1a11cc36-70aa-4f47-8abc-c4b63daf271a` | 26 | Portfolio construction, factor models, screening, P123 platform |
| **Agentic Coding** | `a0247b89-a46e-49b0-aff4-750661b0d32d` | 23 | AI agents, LLMs, Claude, coding workflows, MCP, agentic systems |
| **YTM** | `fa94dd39-cc17-4760-8f2d-dac1c50640a8` | 8 | Fixed income, bonds, yield-to-maturity, duration, credit spreads |
| **ML Algo Trading Books** | `46392b16-29a2-4cca-90a7-05a419ad68ac` | 3 | ML textbooks (AFML, MLDP, etc.) |
| **Biz Cases AI** | `e31e6462-5e4d-4541-ab55-f5ca2fee9f00` | 5 | Business cases for AI, enterprise ROI, AI adoption |
| **Thematic Market Research** | `7bf41f30-a96a-4ee1-bc32-3712517f4181` | 2 | Macro themes, sector trends, thematic investing |
| **Notebook LLM** | `0ee4658a-7de8-478e-8ea7-b77a862a3556` | 10 | NotebookLM itself, knowledge management, LLM tools |

---

## Topic Routing

### Embedded Map (use without any live lookup)

| Query is about... | Route to |
|---|---|
| Specific stocks, companies, equity research, earnings, valuation multiples | **Tickers** |
| Quant strategies, alpha signals, backtesting, systematic/factor trading | **algo trading** |
| Portfolio construction, factor models, screening, P123 platform | **Portfolio123** |
| ML trading textbooks, theory (AFML, MLDP, etc.) | **ML Algo Trading Books** |
| Academic finance papers, empirical studies, research findings | **Academic Research v3** |
| AI agents, Claude, MCP, LLMs, coding workflows, agentic systems | **Agentic Coding** |
| Fixed income, bonds, yield, duration, credit, rates | **YTM** |
| Thematic investing, macro themes, sector/industry trends | **Thematic Market Research** |
| Business cases for AI, enterprise AI ROI, AI adoption | **Biz Cases AI** |
| NotebookLM usage, knowledge management tools | **Notebook LLM** |

When genuinely ambiguous, call `notebook_describe` on 1-2 candidate notebooks to inspect
source titles before routing — don't guess blind.

### Cross-Notebook Queries

When a topic clearly spans multiple notebooks (e.g., "ML approaches to credit spreads"),
pick the **top 1-2 most relevant notebooks**, query them in parallel, then synthesize one
unified answer. Don't default to querying all 12 — that's slow and noisy.

### Academic Research Fan-Out Rule

- **Default:** Query **v3 only** (most recent additions, avoids triple-notebook latency)
- **Fan out to v1 + v2 when:**
  - User says "comprehensive", "all my research", "search all versions", or
  - v3 returns a low-confidence or "not found in sources" answer
- When fanning out, run all 3 queries **in parallel** — don't chain them sequentially

---

## Query Workflow

### Single-Notebook Query

```
notebook_query(
  notebook_id  = <ID from directory>,
  query        = <user's question>,
  conversation_id = <session thread ID if follow-up, else null>
)
```

### Follow-Up Threading

Capture `conversation_id` from every `notebook_query` response and hold it for the session.
On follow-up questions (user says "also", "what about", "and", "follow up on that"),
pass the same `conversation_id` to maintain context and avoid re-explaining the topic.

Each notebook gets its own thread — never mix `conversation_id` values across notebooks.

### Cross-Notebook Query Pattern

1. Fire `notebook_query` calls to each target notebook concurrently
2. Synthesize the responses into one integrated answer
3. If answers conflict between notebooks, flag the discrepancy explicitly

---

## Adding Sources

### File Dump Location

The user's file drop folder is:
```
C:\Users\Eddy\Documents\Obsidian Vault\file dump\
```

Subfolder → notebook routing:

| File Dump Subfolder | Target Notebook |
|---|---|
| `Macro Research/` | Thematic Market Research |
| `Academic Research/` | Academic Research v3 |
| `Coding Agents/` | Agentic Coding |
| `AI Workflows/` | Agentic Coding or Biz Cases AI |
| `AI News/` | Agentic Coding or Biz Cases AI |
| `Portfolio123/` | Portfolio123 |
| `Prompt Engineering/` | Agentic Coding |
| `Sector Research/` | Tickers or Thematic Market Research |
| `Thematic Research/` | Thematic Market Research |

### Add Workflow

When the user names a file or folder, use `Glob` to resolve the full path, then:

```
source_add(
  notebook_id  = <target notebook ID>,
  source_type  = "file",
  file_path    = <absolute Windows path>,
  wait         = True,      ← always True — ensures processing before querying
  wait_timeout = 120
)
```

After a successful add, immediately query the new source for its key thesis or main
takeaways — this gives the user instant value without an extra step.

If the user doesn't specify a target notebook, tell them which one you're routing to
before adding (don't surprise them).

### Adding a URL

```
source_add(
  notebook_id  = <target notebook ID>,
  source_type  = "url",
  url          = <url>,
  wait         = True
)
```

---

## Studio Artifacts

Always ask for confirmation before creating — these take time and consume quota.
Use `confirm=True` only after user approval.

After triggering creation, poll `studio_status` every 15 seconds and report progress.

### Natural Language Triggers → Artifact Type

| User says... | artifact_type | Key options |
|---|---|---|
| "podcast", "audio overview", "deep dive" | `audio` | `audio_format="deep_dive"` (default) |
| "quick audio", "brief summary audio" | `audio` | `audio_format="brief"` |
| "debate", "two sides" | `audio` | `audio_format="debate"` |
| "quiz me", "test me" | `quiz` | `question_count=5`, `difficulty="medium"` |
| "study guide", "briefing doc" | `report` | `report_format="Briefing Doc"` |
| "flashcards" | `flashcards` | `difficulty="medium"` |
| "mind map" | `mind_map` | — |
| "slides", "slide deck", "presentation" | `slide_deck` | `slide_format="detailed_deck"` |
| "infographic" | `infographic` | `detail_level="standard"` |

Default audio creation:
```
studio_create(
  notebook_id  = <id>,
  artifact_type = "audio",
  audio_format = "deep_dive",
  audio_length = "default",
  confirm      = True
)
```

---

## Output Format

Structure every query response like this:

```
**[Notebook Name] — Answer**
<Synthesized answer in clear, substantive prose. Don't just paraphrase the question.>

**Sources referenced**
- <Key source title or "multiple sources across the notebook">

**Follow-up suggestions**
- <Dig deeper on X within this notebook>
- <Cross-check Y in Notebook Z>
- <Suggested action: add a source / create an audio overview / run a quiz>
```

For cross-notebook answers, integrate insights naturally — one cohesive answer that
credits each contributing notebook, rather than separate blocks per notebook.

---

## Notes

Save research insights during a session:

```
note(notebook_id=<id>, action="create", content=<content>, title=<title>)
```

List existing notes: `note(notebook_id=<id>, action="list")`

---

## Maintenance

### Notebook directory has changed?
Run `notebook_list`, update the hardcoded table in this skill with new IDs/titles/counts.

### Re-authenticate
```powershell
uv tool run --from notebooklm-mcp-cli nlm login
```

### Check for CLI updates
```
server_info()   ← returns current version + latest_version
```
Upgrade if needed:
```powershell
uv tool upgrade notebooklm-mcp-cli
```
After upgrading, call `refresh_auth` to confirm the new version connects cleanly.
