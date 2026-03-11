---
name: internet-skill-finder
description: Search and recommend Agent Skills from verified GitHub repositories. Use when users ask to find, discover, search for, or recommend skills/plugins for specific tasks, domains, or workflows.
---

# Internet Skill Finder

Search 7 verified GitHub repositories for Agent Skills.

## Workflow

### 1. Fetch Skill List

```powershell
# Run from the skill folder: C:\Users\Eddy\.claude\skills\internet-skill-finder\
uv run python scripts/fetch_skills.py --search "keyword"
```

Options: `--list` (all skills), `--online` (real-time fetch), `--json` (structured output)

### 2. Deep Dive (if needed)

```powershell
uv run python scripts/fetch_skills.py --deep-dive REPO SKILL
```

### 3. Present Results

When using cached data, prepend:

> ℹ️ Using cached data. For real-time results, set `GITHUB_TOKEN` and re-run with `--online`.

Format each match:

```markdown
### [Skill Name]
**Source**: [Repository] | ⭐ [Stars]
**Description**: [From SKILL.md]
👉 **[Import](import_url)**
```

### 4. No Matches

Suggest `/skill-creator` for custom skill creation.

## Data Access

Script auto-detects and uses best available method:

| Priority | Method | Rate Limit | Behavior |
|----------|--------|------------|----------|
| 1 | `GITHUB_TOKEN` env var | 5000/hr | Set in shell: `$env:GITHUB_TOKEN = "ghp_..."` then use `--online` |
| 2 | Offline cache | Unlimited | Default fallback — no token needed |

```powershell
# Real-time fetch with GitHub token
$env:GITHUB_TOKEN = "ghp_your_token_here"
uv run python scripts/fetch_skills.py --search "keyword" --online
```

JSON output includes `"using_cache": true/false` to indicate data source.

When cache is used, inform user: "Using cached skill data. Set `$env:GITHUB_TOKEN` and use `--online` for real-time GitHub results."

## Sources

7 repositories: anthropics/skills, obra/superpowers, vercel-labs/agent-skills, K-Dense-AI/claude-scientific-skills, ComposioHQ/awesome-claude-skills, travisvn/awesome-claude-skills, BehiSecc/awesome-claude-skills

---

## Windows/Cursor Compatibility Notes

- Script calls changed from `python3 /home/ubuntu/skills/.../fetch_skills.py` to `uv run python scripts/fetch_skills.py` (run from the skill folder).
- "GitHub Connector" (Manus MCP) removed — replaced with `GITHUB_TOKEN` env var approach: `$env:GITHUB_TOKEN = "ghp_..."` then `--online` flag.
- "Enable GitHub Connector" messaging replaced with GITHUB_TOKEN instructions.
