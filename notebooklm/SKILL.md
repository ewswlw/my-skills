---
name: notebooklm
description: >
  Unified NotebookLM workflows: (A) curated research notebooks via `nlm` CLI, (B) vault
  markdown → Studio artifacts via `notebooklm` CLI (notebooklm-py). Triggers: /notebooklm,
  /notebooklm-enrichment, podcast or audio overview from notes, study guide, quiz, mind map,
  "ask my notebooks", "check my research", "what does my [notebook] say about", add PDF/URL
  to NotebookLM, query stored macro/quant/equities/academic/fixed-income research. Always
  use the terminal — never NotebookLM MCP.
---

# NotebookLM (unified CLI skill)

**Location of truth:** `C:\Users\Eddy\.claude\skills\notebooklm\SKILL.md`

## Non-negotiables

- **No MCP.** Do not call `user-notebooklm-mcp`, `refresh_auth`, or any NotebookLM MCP tool.
- **Two separate CLIs and two auth flows:** `nlm` (notebooklm-mcp-cli) and `notebooklm` (notebooklm-py). Logging into one does not log you into the other.
- **Use Shell** to run commands; paste outputs into the conversation when summarizing for the user.

## Which CLI?

| Goal | CLI | Package |
|------|-----|---------|
| Query **existing** notebooks by ID, cross-notebook query, add sources to a known notebook, `nlm` Studio (audio/quiz/slides), notes | **`nlm`** | `notebooklm-mcp-cli` |
| **Create** a fresh notebook from vault `.md`, generate/download artifacts with `notebooklm generate` / `download` | **`notebooklm`** | `notebooklm-py` |

**Anti-patterns:** Using **`nlm`** for the `notebooklm create` → `generate` → `download` flow, or **`notebooklm`** for the hardcoded notebook ID table below (possible, but the skill optimizes **`nlm`** for that corpus).

---

## Shared: installs and PATH (Windows)

| CLI | Install | Shims (typical) |
|-----|---------|-----------------|
| `nlm` | `uv tool install "notebooklm-mcp-cli>=0.4.6"` | `C:\Users\Eddy\.local\bin\nlm.exe` |
| `notebooklm` | `uv tool install "notebooklm-py[browser]"` | `C:\Users\Eddy\.local\bin\notebooklm.exe` |

**Fallback:** `uv tool run --from notebooklm-mcp-cli nlm ...` or `uv tool run --from notebooklm-py notebooklm ...`

If **`notebooklm login`** fails with missing Chromium, run once:

`& "$env:APPDATA\uv\tools\notebooklm-py\Scripts\python.exe" -m playwright install chromium`

---

# Part A — `nlm` (curated notebooks)

## Auth (`nlm`)

1. `nlm login` (browser).
2. On errors: `nlm doctor` then `nlm login` again.

## Notebook directory

IDs are cached for fast routing. If a command says invalid ID, run **`nlm notebook list`** and update this table.

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

## Topic routing

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

If ambiguous: **`nlm notebook describe <NOTEBOOK_ID>`** on 1–2 candidates before choosing.

### Cross-notebook

Prefer **1–2** notebooks. Either:

- `nlm cross query "Question" -n <id1>,<id2>`, or
- Two parallel **`nlm notebook query`** calls, then synthesize.

Use **`-a` / `--all`** only when the user explicitly wants every notebook.

### Academic Research fan-out

- Default: **v3** only.
- Fan out to **v1 + v2** when the user asks for comprehensive / all versions, or v3 returns weak coverage.
- Fan-out queries should run **in parallel**, not serially.

## Query workflow (`nlm`)

```powershell
nlm notebook query <NOTEBOOK_ID> "Your question"
nlm notebook query <NOTEBOOK_ID> "Follow-up" -c <conversation_id>
nlm cross query "Your question" -n <id1>,<id2>
```

Use **`--json`** when you need structured output (e.g. `conversation_id`).

## Adding sources (`nlm`)

**File dump root:** `C:\Users\Eddy\Documents\Obsidian Vault\file dump\`

| File dump subfolder | Target notebook |
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

```powershell
nlm source add <NOTEBOOK_ID> --file "C:\absolute\path\to\file.pdf" --wait --wait-timeout 600
nlm source add <NOTEBOOK_ID> --url "https://example.com" --wait
```

Use **`--youtube`** for YouTube URLs (repeat flags for bulk). After adding, run a short **`nlm notebook query`** for takeaways. Tell the user which notebook you targeted if they did not specify.

## Studio artifacts (`nlm`)

Confirm with the user before creating (quota/latency). Many commands accept **`-y` / `--confirm`** after approval.

```powershell
nlm studio status
```

| User intent | Pattern |
|-------------|---------|
| Deep-dive audio | `nlm audio create <ID> --format deep_dive` |
| Brief audio | `nlm audio create <ID> --format brief` |
| Debate audio | `nlm audio create <ID> --format debate` |
| Quiz / report / flashcards / mind map / slides / infographic | `nlm quiz create`, `nlm report create`, etc. (see `--help`) |

Example:

```powershell
nlm audio create <NOTEBOOK_ID> --format deep_dive --length default -y
```

Use **`nlm download`** per `--help` to fetch files locally.

## Notes (`nlm`)

```powershell
nlm note list <NOTEBOOK_ID>
nlm note create <NOTEBOOK_ID> -c "Content..." -t "Title"
```

## Output format (for `nlm` Q&A)

```
**[Notebook Name] — Answer**
<Substantive prose>

**Sources referenced**
- <Title or "multiple sources">

**Follow-up suggestions**
- <Next step in this notebook>
- <Optional cross-notebook check>
```

---

# Part B — `notebooklm` (vault → NotebookLM artifacts)

Use for **new** notebooks built from vault markdown and for **`generate` / `download`** flows.

## Auth (`notebooklm`)

`notebooklm login` (separate from `nlm login`). Storage default: `C:\Users\Eddy\.notebooklm\storage_state.json`.

**Preferred invocation:** `notebooklm` on PATH after global install. **Fallback:** `uv run --project "C:\Users\Eddy\Documents\Obsidian Vault" notebooklm ...`

## Workflow

1. `notebooklm create "Title from file"`
2. `notebooklm source add "<absolute_path_to_md>"`
3. `notebooklm generate audio "make it engaging" --wait` (or video, quiz, flashcards, study-guide, mind-map)
4. `notebooklm download audio .\output.mp3` → move to **`file dump\Notebook LLM\`**

## Paths

- **Input:** any `.md` under the vault (e.g. macro, knowledge, ticker notes).
- **Output:** `C:\Users\Eddy\Documents\Obsidian Vault\file dump\Notebook LLM\` with descriptive filenames.

## Command table

| Artifact | Generate | Download |
|----------|----------|----------|
| Audio / podcast | `notebooklm generate audio "make it engaging" --wait` | `notebooklm download audio .\name.mp3` |
| Study guide | `notebooklm generate report --template study-guide --wait` | `notebooklm download report .\guide.md` |
| Quiz | `notebooklm generate quiz --wait` | `notebooklm download quiz --format markdown .\quiz.md` |
| Mind map | `notebooklm generate mind-map --wait` | `notebooklm download mind-map .\mindmap.json` |

Markdown, PDF, URL, and YouTube are supported as sources where the CLI allows. **`--wait`** blocks until generation finishes.

---

## Maintenance

```powershell
nlm notebook list
uv tool upgrade notebooklm-mcp-cli
uv tool upgrade notebooklm-py
```

Refresh the notebook ID table when titles/counts change.
