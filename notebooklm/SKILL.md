---
name: notebooklm
description: >
  Unified NotebookLM workflows: (A) curated research notebooks via `nlm` CLI, (B) vault
  markdown → Studio artifacts via `notebooklm` CLI (notebooklm-py). Triggers: /notebooklm,
  /notebooklm-enrichment, podcast or audio overview from notes, study guide, quiz, mind map,
  "ask my notebooks", "check my research", "what does my [notebook] say about", add PDF/URL
  to NotebookLM, query stored macro/quant/equities/academic/fixed-income research. Agents
  must run the auth preflight in this skill before the first CLI call (and retry after login
  when a command fails with auth errors). Always use the terminal — never NotebookLM MCP.
---

# NotebookLM (unified CLI skill)

**Location of truth:** `C:\Users\Eddy\.claude\skills\notebooklm\SKILL.md`

## Non-negotiables

- **No MCP.** Do not call `user-notebooklm-mcp`, `refresh_auth`, or any NotebookLM MCP tool.
- **Two separate CLIs and two auth flows:** `nlm` (notebooklm-mcp-cli) and `notebooklm` (notebooklm-py). Logging into one does not log you into the other.
- **Use Shell** to run commands; paste outputs into the conversation when summarizing for the user.
- **Auth preflight:** On `/notebooklm` (or any invocation of this skill), follow **Automatic authentication** below before relying on either CLI.

## Automatic authentication (agents — mandatory for `/notebooklm`)

Goal: **never assume** a session is valid. Restore auth **proactively** (probe) and **reactively** (retry after login when a command fails with an auth error).

### When to run

1. **Proactive:** Before the **first** `nlm` command in this chat/task, and before the **first** Part B `notebooklm` command (`create`, `source`, `generate`, `download`, etc.).
2. **Reactive:** If any `nlm` or `notebooklm` output says authentication expired, not logged in, or invalid session — run the matching **Login recovery** once, then **retry the failed command** once (not a tight loop).

### `nlm` (notebooklm-mcp-cli)

| Step | Action |
|------|--------|
| **Probe** | `nlm notebook list -q` (fast; IDs only). Success ⇒ `nlm` session OK for this task. |
| **Login recovery** | Run `nlm login` (browser/Chrome). Use a **long** agent wait (e.g. 180s) so the user can finish the flow. |
| **Retry** | Re-run **`nlm notebook list -q`**. If still broken: `nlm doctor`, then `nlm login` again, then probe once more. |
| **Stop** | After **one** full recovery cycle, if the probe still fails, stop and tell the user what `nlm doctor` / stderr reported — do not spam `login`. |

Treat stderr containing “Authentication”, “expired”, or “re-authenticate” the same as a failed probe.

### `notebooklm` (notebooklm-py) — Part B only

| Step | Action |
|------|--------|
| **Probe** | `notebooklm list` (or `notebooklm list --json` if you need structured output). **Do not** use `notebooklm status` alone as the auth check — it can print context even when `list` would say “Not logged in.” |
| **Login recovery** | `notebooklm login` (browser). Same long wait as `nlm login`. |
| **Retry** | `notebooklm list` again. If Chromium errors appear, run the Playwright install one-liner in **Shared: installs** once, then retry login. |
| **CI / headless** | If there is no browser, rely on **`NOTEBOOKLM_AUTH_JSON`** (see `notebooklm` help) or stop and explain — do not pretend login worked. |

### User messaging

When launching `nlm login` or `notebooklm login`, briefly tell the user a browser window may open and they should complete Google/NotebookLM sign-in if prompted.

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
| `nlm` | `uv tool install "notebooklm-mcp-cli>=0.6"` | `C:\Users\Eddy\.local\bin\nlm.exe` |
| `notebooklm` | `uv tool install "notebooklm-py[browser]"` | `C:\Users\Eddy\.local\bin\notebooklm.exe` |

**Fallback:** `uv tool run --from notebooklm-mcp-cli nlm ...` or `uv tool run --from notebooklm-py notebooklm ...`

If **`notebooklm login`** fails with missing Chromium, run once:

`& "$env:APPDATA\uv\tools\notebooklm-py\Scripts\python.exe" -m playwright install chromium`

---

# Part A — `nlm` (curated notebooks)

## Auth (`nlm`)

**Agents:** use **Automatic authentication** (probe + recovery) on every `/notebooklm` run.

**Manual:** `nlm login` (browser). On errors: `nlm doctor` then `nlm login` again.

## Notebook directory

IDs are cached for fast routing. If a command says invalid ID, run **`nlm notebook list`** and update this table.

*Last refreshed from `nlm notebook list`: **2026-05-12**.*

| Notebook | ID | Sources | Primary Topics |
|---|---|---|---|
| ai workflows | `8014f2bc-3314-4b04-a31f-ea00ccd4f5d1` | 51 | AI workflows, agent tooling, MCP, coding assistants |
| Ai workflows v2 | `cea498a4-8c42-4eb7-8851-02c3dc1cb261` | 51 | Parallel corpus to ai workflows — prefer one as default |
| Tickers | `596d3877-a33a-487c-87c1-d4881b8fb1bd` | 21 | Stocks, equity research, earnings, company analysis |
| Biz Githubs | `1684a9d9-0966-43fe-999f-16209ae2bc08` | 6 | Business / engineering repos, case-oriented GitHub |
| ai workflows v3 | `f72f4265-b970-41cf-9042-38d13d8b43ae` | 0 | Empty staging notebook |
| ai githubs | `e3193a2c-bc5d-49e9-b126-9faff6723f43` | 49 | AI-related GitHub repos, libraries, tooling |
| NotebookLLM | `df72a17b-0f7a-4e70-8ffc-5d06a57b657a` | 16 | NotebookLM product, knowledge-management tooling |
| Obsidian | `bcb24da7-6e65-46bc-9f1c-d2e8861cf2cb` | 5 | Obsidian PKM and vault workflows |
| AI Models | `d0e6a3f8-fe96-4a37-a3af-c1579186acd7` | 6 | LLM model releases, evaluations, benchmarks |
| ai tools v2 | `032fb4b2-5094-4658-b61e-c97a1bb2a708` | 30 | AI tools landscape (newer cohort) |
| algo trading v2 | `f3d2a8b7-363d-493b-b4b1-c21176b178c4` | 50 | Quant strategies, systematic trading (primary large corpus) |
| GitHub Knowledge | `c8c7fc8c-c59e-4436-9f98-407d75fa93b1` | 3 | Curated GitHub knowledge snippets |
| AI NEWS | `348490ff-f119-4475-9f87-215e0aeac603` | 32 | AI industry news, product launches |
| Macro | `320ef58b-0aa2-4570-8c6d-21b84076935a` | 11 | Macro economy, rates, cycles |
| **Academic Research v4** *(default)* | `155d46ea-c4ae-4c4f-a2bb-0f54c0e7efad` | 29 | Academic finance / empirical papers (newest cohort) |
| Portfolio123 v2 | `1a11cc36-70aa-4f47-8abc-c4b63daf271a` | 49 | Portfolio123 screens, factors, platform (large corpus) |
| Algo Trading Githubs | `b28341b6-a398-422b-b787-5c1bb66677b4` | 5 | Algo-trading repos and tooling on GitHub |
| AI Skills | `b013ec27-76eb-45f0-84f7-c65447f655d5` | 16 | Skills, prompts, reusable agent recipes |
| Plug Ins and Tools | `f7264fca-f84a-49d8-9ffd-68b953576d8d` | 16 | IDE plugins, extensions, dev tooling |
| Portfolio123 | `06f1bd5d-cb97-456a-a051-52032da9a4f9` | 22 | P123 core / alternate corpus vs v2 |
| industry research | `89f8e9db-c8c7-44b6-9f82-84ceeb56e668` | 1 | Industry / sector one-offs |
| credit global | `2edf1aff-95b6-4712-a86a-bf61d1c598ed` | 3 | Global credit markets |
| credit cad | `708ced28-e5fa-44cc-84e7-0879e54749a0` | 1 | Canadian credit |
| Algo Trading Tools | `971beff7-f338-48ae-8771-4d18f7c9b872` | 18 | Trading utilities, libraries, infra |
| algo trading v1 | `9b85bda7-ef69-4275-ae4a-34c32ced9886` | 46 | Systematic trading (prior cohort vs v2) |
| ai tools v1 | `3842e644-891c-48f4-9719-ccc0242f828e` | 43 | AI tools catalog (prior cohort vs v2) |
| AI Everything | `0f81aa87-04f1-4bf2-9f95-6bded6501a04` | 42 | Broad AI catch-all |
| Biz Cases AI | `e31e6462-5e4d-4541-ab55-f5ca2fee9f00` | 40 | Enterprise AI ROI, adoption, business cases |
| Market Learnings | `349ab63b-2e72-47e2-83e2-13a2e29828e5` | 5 | Markets / trading qualitative notes |
| YTM | `fa94dd39-cc17-4760-8f2d-dac1c50640a8` | 24 | Fixed income, FI, spreads, institutional credit |
| Thematic | `9ac81175-180b-457e-b04e-c45aaafbb87d` | 1 | Thematic investing (minimal sources) |
| Learnings from Academia | `433eec00-384f-49c6-84d1-2f0c1d0ed0bf` | 13 | Academic takeaways synthesis |
| Personal Interest | `4e8b2d35-acae-4cfa-9e66-0fcf72aad699` | 2 | Personal/non-work topics |
| Academic Research v3 | `436d54d7-802d-4ab9-8c7f-a28940023f26` | 45 | Academic papers (prior cohort vs v4) |
| Academic Research v2 | `933e0fc5-eb86-49ca-a2d3-5231d3614bc2` | 43 | Academic papers (second cohort) |
| Academic Research v1 | `42266acf-1118-4b19-bf58-2e0852b6474d` | 36 | Academic papers (oldest cohort) |
| ML Algo Trading Books | `46392b16-29a2-4cca-90a7-05a419ad68ac` | 3 | ML-for-trading textbooks (AFML, MLDP-style) |

## Topic routing

| Query is about... | Route to |
|---|---|
| Specific stocks, companies, equity research, earnings, valuation multiples | **Tickers** |
| Quant strategies, alpha signals, backtesting, systematic/factor trading | **algo trading v2** (default corpus); **algo trading v1** for older parallel set |
| Portfolio construction, factor models, screening, P123 platform | **Portfolio123 v2** (default); **Portfolio123** for alternate/smaller corpus |
| ML trading textbooks, theory (AFML, MLDP, etc.) | **ML Algo Trading Books** |
| Academic finance papers, empirical studies, research findings | **Academic Research v4** *(default)*; fan-out per **Academic Research fan-out** below |
| AI agents, Claude, MCP, LLMs, coding workflows, agentic systems | **Ai workflows v2** or **ai workflows** (same footprint — pick one per task); **ai githubs** for repo-heavy asks; **AI Skills** / **Plug Ins and Tools** for skills vs IDE tooling |
| GitHub repos, libraries (business vs AI vs trading) | **Biz Githubs**, **ai githubs**, **Algo Trading Githubs**, **GitHub Knowledge** (match domain) |
| Fixed income, bonds, yield, duration, credit (general FI) | **YTM** |
| Geographic credit markets | **credit global** / **credit cad** |
| Macro economy, rates, broad cycle context | **Macro** |
| Thematic investing vs single-name sector/industry probes | **Thematic** vs **industry research** (**Tickers** for equity comps) |
| Business cases for AI, enterprise AI ROI, AI adoption | **Biz Cases AI** |
| NotebookLM usage, NotebookLM workflows, PKM tooling | **NotebookLLM** |
| AI product/news cycle | **AI NEWS** |
| Obsidian vault / PKM mechanics | **Obsidian** |
| Broad or unfocused “AI overview” | **AI Everything** or **Biz Cases AI** depending on enterprise vs tech slant |

If ambiguous: **`nlm notebook describe <NOTEBOOK_ID>`** on 1–2 candidates before choosing.

### Cross-notebook

Prefer **1–2** notebooks. Either:

- `nlm cross query "Question" -n <id1>,<id2>`, or
- Two parallel **`nlm notebook query`** calls, then synthesize.

Use **`-a` / `--all`** only when the user explicitly wants every notebook.

### Academic Research fan-out

- Default: **Academic Research v4** only.
- Fan out to **v1 + v2 + v3** when the user asks for comprehensive / all cohorts, or **v4** returns weak coverage.
- Optionally add **Learnings from Academia** for synthesized academic takeaways (different corpus shape).
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
| `Macro Research/` | **Macro** (default); **Thematic** for thematic-only drops |
| `Academic Research/` | **Academic Research v4** (default); **v3/v2/v1** only if user requests a specific cohort |
| `Coding Agents/` | **Ai workflows v2** or **ai workflows** |
| `AI Workflows/` | **ai workflows** / **Ai workflows v2**; **Biz Cases AI** when the content is enterprise ROI / adoption |
| `AI News/` | **AI NEWS**; **Biz Cases AI** for business-framed AI news |
| `Portfolio123/` | **Portfolio123 v2** (default); **Portfolio123** alternate |
| `Prompt Engineering/` | **AI Skills** or **Ai workflows v2** |
| `Sector Research/` | **Tickers** or **Macro** or **industry research** |
| `Thematic Research/` | **Macro** or **Thematic** |

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

**Agents:** before Part B commands, run the **`notebooklm` probe** in **Automatic authentication**.

`notebooklm login` (separate from `nlm login`). Storage default: `C:\Users\Eddy\.notebooklm\storage_state.json`.

**Preferred invocation:** `notebooklm` on PATH after global install. **Fallback:** `uv run --project "C:\Users\Eddy\Documents\Obsidian Vault" notebooklm ...`

## Workflow

1. `notebooklm create "Title from file"`
2. `notebooklm source add "<absolute_path_to_md>"`
3. `notebooklm generate audio "make it engaging" --wait` (or video, quiz, flashcards, study-guide, mind-map)
4. `notebooklm download audio .\output.mp3` → move to **`file dump\Notebook LLM\`** (keep folder name stable on disk); notebook target for ingest is **NotebookLLM** `df72a17b-0f7a-4e70-8ffc-5d06a57b657a`.

## Paths

- **Input:** any `.md` under the vault (e.g. macro, knowledge, ticker notes).
- **Output:** `C:\Users\Eddy\Documents\Obsidian Vault\file dump\Notebook LLM\` with descriptive filenames (maps to **NotebookLLM** in the directory table above).

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
uv tool upgrade "notebooklm-mcp-cli>=0.6"
uv tool upgrade notebooklm-py
```

Refresh the notebook ID table (`## Notebook directory`) when titles/counts change; bump the **Last refreshed** line when you reconcile from `nlm notebook list`.
