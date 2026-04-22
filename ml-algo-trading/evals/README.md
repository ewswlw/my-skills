# Evals for `ml-algo-trading`

| File | Purpose |
|------|---------|
| [`evals.json`](evals.json) | Three **task** evals with `expectations` for qualitative or automated grading. |
| [`trigger_queries.json`](trigger_queries.json) | **20** queries (`should_trigger` true/false) for **description optimization** or trigger-rate testing in Claude Code (`run_loop.py` — not available in Cursor IDE). |
| [`manual_run_outputs/reference_responses.md`](manual_run_outputs/reference_responses.md) | **Reference answers** to the three `evals.json` prompts (synthetic hand-run for comparison). |

**Skill-creator:** For full benchmark flow (parallel runs, `generate_review.py`, grading), see `C:\Users\Eddy\.claude\skills\skill-creator\SKILL.md`.

**Completed run (synthetic, iteration 1):** `C:\Users\Eddy\.claude\skills\ml-algo-trading-workspace\` — contains `benchmark.json`, `benchmark.md`, and `review.html` (open in browser). Responses are hand-written stand-ins for with-skill vs without-skill; re-run with real subagents in Claude Code if you need token/timing stats.
