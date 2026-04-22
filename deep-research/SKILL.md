---
name: deep-research
description: >
  Use this skill whenever the user wants **cited, multi-step, or long-horizon research**—even if
  they only say "look this up," "compare," "what does the market say," "due diligence," "lit
  review," "macro view," "competitive landscape," "ticker background," or paste a research question
  for Obsidian. Primary path: run `scripts/research.py` (Perplexity HTTP API, same
  `PERPLEXITY_API_KEY` as the Perplexity MCP in `mcp.json`), then documented free fallbacks. Use
  Shell to execute the CLI; prepend **Research source:** in the final note. Triggers: /deep
  research, deep research, Sonar deep research, Perplexity research API.
---

# Deep research (Perplexity API–first)

**Source of truth:** `C:\Users\Eddy\.claude\skills\deep-research\SKILL.md`

## Where your API key comes from (one key, no second copy)

This skill is built around the **Perplexity HTTP API** (`POST https://api.perplexity.ai/chat/completions` in `scripts/research.py`).

**Use the same key as your Cursor Perplexity MCP** — you already wire it in global config:

- **File:** `C:\Users\Eddy\.cursor\mcp.json` → block **`"perplexity"`** uses  
  `"PERPLEXITY_API_KEY": "${env:PERPLEXITY_API_KEY}"`
- **Cursor’s MCP** only ever sees the **user/system** `PERPLEXITY_API_KEY` from the OS. It does **not** read the file `.env` in the skill folder.
- **`research.py`** calls `load_dotenv` on that `.env` file first, then the process environment. If the key exists **only** in **`.env` next to the skill**, the script works in the terminal, but **MCP in Cursor will not** until you also set the same variable in the user environment (or rely on user env for both and skip a local file).
- Set **`PERPLEXITY_API_KEY`** once in **Windows → Environment variables** (or your profile) so **both** MCP and the script use one source of truth; an optional per-skill **`.env`** is for the script only or for local overrides (see [python-dotenv](https://pypi.org/project/python-dotenv/) precedence).

**Do not** commit `.env` or paste keys into chat.

## Non-negotiables

1. **Research source line** — The first line of the final user-visible answer (and any report saved to disk) must be either:
   - `**Research source:** Perplexity`
   - `**Research source:** Fallback — <mechanism>` (e.g. `DuckDuckGo Instant Answer`, `Firecrawl`, `user paste only`).
2. **Perplexity API first (when a key is available)** — Run **`python scripts/research.py`** (or `uv run python …\scripts\research.py`) so the model hits the **official API** with `sonar-deep-research` (default). If there is no `PERPLEXITY_API_KEY` in the environment, apply **Fallback chain**; do not invent a key.
3. **In Cursor, prefer Shell for this skill** — Run the research script from a terminal (agent **Shell**), then summarize output for the user, unless the user only wants a chat answer synthesized without calling the API.
4. **This skill is read-only** — It does not delete, encrypt, or modify user files except when the user explicitly asked you to **write** an output file to a path they gave.

## Primary workflow (agent)

| Step | Action |
|------|--------|
| 1 | **API run** — From the skill directory (or with full path to `…\scripts\research.py` from any cwd), run `uv run python scripts\research.py -q "…"`. `sonar-deep-research` can take **tens of seconds to several minutes**; do not treat a slow run as failure until the HTTP timeout. Ensure the key is available (user env and/or a local **`.env`** in the skill folder for the script). |
| 2 | **On API failure** — At most two retries is built into the script; if still failing, go to **Fallback chain**. |
| 3 | **Format** — Prepend the **Research source** line, then the **Vault output skeleton** (below) when you paste into Obsidian. |
| 4 | **Advise** — If the source was a fallback, tell the user to **verify** citations. |

## Optional: Perplexity MCP in chat (not the primary path for this skill)

The MCP uses the **same** `PERPLEXITY_API_KEY` from the environment; it is not a different key. Vendored tool names/schemas (if you use MCP in chat): `references\cursor-mcp-perplexity.md` and `references\mcp-tools\`. For chat-native `perplexity_research` tool calls, see that reference.

## Fallback chain (after Perplexity API is exhausted or no key)

Use the **first** option that is available in this **environment** and allowed by the user:

1. **Firecrawl** — If the Firecrawl MCP (or `FIRECRAWL_API_KEY` in env for scripts) is available, use it for search/scrape as documented in that tool — label the banner `**Research source:** Fallback — Firecrawl`.
2. **DuckDuckGo Instant Answer (free, limited)** — The bundled `research.py` includes a no-key **DuckDuckGo** instant-answer pass when Perplexity fails. Label: `**Research source:** Fallback — DuckDuckGo Instant Answer`. Often **sparse** for complex questions.
3. **Wikipedia opensearch (free, snippets)** — If DDG is empty, the script can query **English Wikipedia** `opensearch` (snippets + URLs only; no full article fetch in v1). Label: `**Research source:** Fallback — Wikipedia opensearch (snippets)`. User must still **verify** at the linked page.
4. **Stop and ask** — If nothing above returns a usable body, state that limitation and offer: shorten the question, add URLs/PDFs to the chat, or set `PERPLEXITY_API_KEY` in the same place the MCP uses.

**Do not** use arbitrary shell `curl` to random hosts. Prefer the tools above.

## Cost

- **Perplexity** (MCP or API) is a **paid** capability for most accounts. Long, broad, or `sonar-deep-research` style runs can be **expensive** and take **minutes**.
- Prefer **narrow, scoped** questions. Check usage in your [Perplexity](https://www.perplexity.ai/) / API account and the [API docs](https://docs.perplexity.ai/).
- **Fallbacks** are “best effort” and may be free (e.g. DDG) or use **your** other API keys; they are not cost-equivalent to Perplexity.

## Safety and privacy

- **Do not** place secrets, credentials, bank/account numbers, or non-public PII in research prompts.
- **Read-only** research: do not instruct exfiltration or bypassing paywalls; only public or user-supplied material.
- **Verify** citations, especially for **Fallback** answers.

## Vault output skeleton (for Obsidian)

Use this by default so notes paste cleanly:

```markdown
**Research source:** Perplexity

## Question

[One paragraph — what you were asked.]

## Findings

[Structured sections, bullets, and citations.]

## Limitations

[Model/tool limits, data gaps, or what was not verified.]
```

## CLI (Perplexity API — `research.py`)

**Location:** `C:\Users\Eddy\.claude\skills\deep-research\`

**Key:** set **`PERPLEXITY_API_KEY`** in the **user/system environment** (the same place `mcp.json` reads for the Perplexity MCP). No `.env` file is required if that is already set. Optional: copy `.env.example` → `.env` in this folder for a key **only** here.

```powershell
cd C:\Users\Eddy\.claude\skills\deep-research
uv pip install -r requirements.txt
# or: python -m pip install -r requirements.txt
uv run python scripts\research.py -q "Your question here"
uv run python scripts\research.py -q "Your question" --json
uv run python scripts\research.py -q "Your question" --out D:\out\run.md
```

- **v1 flags:** `--query` / `-q`, `--json`, `--out` only. No `--stream` / task IDs (reserved for a future spec).
- **Env:** `PERPLEXITY_API_KEY` (required for Perplexity; **identical** to the MCP’s `PERPLEXITY_API_KEY`). Optional `PERPLEXITY_MODEL` (default `sonar-deep-research`), optional `PERPLEXITY_REASONING_EFFORT` (`low` \| `medium` \| `high`, for `sonar-deep-research`). Optional `DEEP_RESEARCH_PERPLEXITY_TIMEOUT` (default 120) and `DEEP_RESEARCH_FALLBACK_TIMEOUT` (default 60).
- **`--json`:** Includes `raw` (full API or fallback payload). **Do not** paste that block into public tickets if it may contain sensitive query text. Prefer the markdown view or a redacted `content` only.

## Troubleshooting

| Symptom | Likely cause | What to do |
|--------|----------------|------------|
| `research_source` is a **Fallback** but you have a key | Key not visible to this process | Set **user env** and/or a **local `.env`** in the skill folder for the process running `research.py`. Open a **new** shell after `setx` / env changes. |
| `401` / “Unauthorized” from API | Revoked, wrong, or typo’d key | Regenerate the key in the Perplexity API UI, update env or `skill\.env`, never commit. |
| `402` / payment or quota errors | Billing / usage limits | Perplexity account / API [billing & usage](https://www.perplexity.ai/). |
| `Python` / `encodings` error when `cd` into the skill folder | Broken or nested `pyvenv` / `pyvenv.cfg` in that directory | Run `uv run python "C:\…\full\path\scripts\research.py"` from **another** directory (e.g. your vault) instead of `cd` to the skill. |
| Perplexity works but output still has internal thinking | Rare edge | `research.py` strips `<think>…</think>`; re-run; if a new tag appears, open an issue or extend the strip regex. |
| Slow run (2–10+ min) on the deep model | Normal for `sonar-deep-research` | Wait or set `PERPLEXITY_MODEL` to `sonar` or `sonar-pro` for a faster, cheaper run (trades off depth). |

## Manual QA (before relying on the skill)

- [ ] **API (user env)** — `uv run python scripts\research.py -q "test"` with `PERPLEXITY_API_KEY` in **user env only** (no local `.env` in the skill folder); first line is `**Research source:** Perplexity` when the key is valid.
- [ ] **API (local `.env` only)** — Unset the variable in the shell, keep the key only in **`.env`** in the skill folder, run the same; the script should still return Perplexity; note **MCP in Cursor** still needs **user** env if you use both.
- [ ] **Same name as MCP** — `C:\Users\Eddy\.cursor\mcp.json` uses `${env:PERPLEXITY_API_KEY}`.
- [ ] **Fallback** — Remove key from env **and** move/rename the local **`.env`**; run the same; confirm a **Fallback** banner.

## Reference

- **API key + MCP in one place:** `references\cursor-mcp-perplexity.md` (MCP is optional; key source is the same)
- Vendored MCP tool JSON (only if you use MCP in chat): `references\mcp-tools\`
- NPM MCP server: [`@perplexity-ai/mcp-server`](https://www.npmjs.com/package/@perplexity-ai/mcp-server)
- Inspiration (Gemini-based CLI): [sanjay3290/ai-skills `deep-research`](https://github.com/sanjay3290/ai-skills/tree/main/skills/deep-research)
- Perplexity HTTP API (used by `research.py`): [POST /chat/completions](https://docs.perplexity.ai/api-reference/chat-completions-post)

## Limitations (v1)

- No guarantee of **Gemini** feature parity (streaming, job IDs, long-running async jobs).
- **DuckDuckGo** instant answers are not a full web search; many complex queries return little text.
- If you use **MCP** in chat, tool shapes may differ from the vendored `references\mcp-tools\` — compare to your Cursor `mcps` cache if something breaks.
