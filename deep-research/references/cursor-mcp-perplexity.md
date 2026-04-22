# One API key for MCP and for `research.py`

**Primary use for the deep-research skill:** the **Perplexity HTTP API** in `scripts/research.py` (not MCP tool calls).  
**This note tells you where the key is defined so you do not create a second key.**

## Where the key is defined

`C:\Users\Eddy\.cursor\mcp.json` registers the Perplexity MCP with:

```json
"perplexity": {
  "command": "npx",
  "args": ["-y", "@perplexity-ai/mcp-server"],
  "env": {
    "PERPLEXITY_API_KEY": "${env:PERPLEXITY_API_KEY}"
  }
}
```

So the **only** name the skill and Cursor agree on is **`PERPLEXITY_API_KEY`**, read from the **user/system environment** (Windows: Environment Variables UI, or your profile script).

- **`@perplexity-ai/mcp-server`:** receives only `PERPLEXITY_API_KEY` from **`mcp.json` → `${env:…}`** — it does **not** read `deep-research\.env`.
- **`research.py`:** also reads optional `C:\Users\Eddy\.claude\skills\deep-research\.env` via `python-dotenv` (in addition to the environment). A key **only** in `skill\.env` enables the **script** in the terminal but **not** the MCP in Cursor.
- **Do not** commit `.env` or put keys in the repo.

## MCP (optional)

- **Server key in JSON:** `perplexity` (Cursor may show tools with a prefix, e.g. `mcp_perplexity_…`).
- NPM: [`@perplexity-ai/mcp-server`](https://www.npmjs.com/package/@perplexity-ai/mcp-server).

Vendored **MCP** tool **JSON** (for chat-only use): `references/mcp-tools/`.
