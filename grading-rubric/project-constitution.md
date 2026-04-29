# Project Constitution

## Technology Stack
- Markdown — primary skill definition (`SKILL.md`) and all generated user-facing artifacts (`RUBRIC.md`, `PROGRAM.fragment.md`)
- Python 3.11+ — `assets/scorer.py.template` and `scripts/validate_rubric.py`
- YAML — frontmatter in `SKILL.md` and inside `PROGRAM.fragment.md`
- `uv` — runner for the validator script
- **No external runtime dependencies in `scorer.py.template`** (Python stdlib only) so user projects do not need extra installs

## Project Structure
- `C:\Users\Eddy\.claude\skills\grading-rubric\SKILL.md` — main skill file (workflow, frontmatter, trigger description)
- `C:\Users\Eddy\.claude\skills\grading-rubric\references\` — anchor rubric examples
  - `references\trading-strategy.md`
  - `references\code-quality.md`
  - `references\writing.md`
  - `references\ml-eval.md`
  - `references\generic-task.md`
- `C:\Users\Eddy\.claude\skills\grading-rubric\assets\scorer.py.template` — parameterized Python scorer template
- `C:\Users\Eddy\.claude\skills\grading-rubric\assets\PROGRAM.fragment.md.template` — `/auto-researcher` PROGRAM.md fragment template
- `C:\Users\Eddy\.claude\skills\grading-rubric\scripts\validate_rubric.py` — self-validation CLI
- `C:\Users\Eddy\.claude\skills\grading-rubric\evals\evals.json` — test prompts for the `/skill-creator` iteration loop
- `C:\Users\Eddy\.claude\skills\grading-rubric\project-spec.md` — full specification (XML)
- `C:\Users\Eddy\.claude\skills\grading-rubric\project-constitution.md` — this file

## Executable Commands
- Validate a generated rubric: `uv run python C:\Users\Eddy\.claude\skills\grading-rubric\scripts\validate_rubric.py <path-to-RUBRIC.md>`
- Run a generated scorer (from the user's project root after the skill has written `scorer.py` there): `python scorer.py`
- Run skill evals (from `C:\Users\Eddy\.claude\skills\skill-creator\`): `uv run python -m scripts.aggregate_benchmark <workspace>/iteration-N --skill-name grading-rubric`

## Hard Boundaries
- NEVER hardcode domain-specific defaults that override the user's task description (no implicit trading, code, or writing bias).
- NEVER emit a composite scoring formula whose direction varies per rubric — the composite is **always** in `[0, 1]` with **higher is better**.
- NEVER overwrite an existing `RUBRIC.md`, `scorer.py`, or `PROGRAM.fragment.md` without explicit user confirmation; offer overwrite, versioned filename (`RUBRIC.v2.md`, `scorer.v2.py`), or cancel.
- NEVER skip self-validation (`scripts/validate_rubric.py`) or the synthetic best/worst dry-run before declaring a rubric complete.
- NEVER ship a rubric without an Adversarial Reviewer Persona section (used or not) and a Domain-Confidence banner.
- NEVER ship a generated `scorer.py` that hides hard-gate failures behind a silent `composite: 0.0` — the scorer must exit non-zero AND print `GATE_FAILED: <gate_name>: <reason>` to stderr so `/auto-researcher` records it as a `crashed` row.
- NEVER omit the auto-included `regression_trip_wire` criterion from a generated rubric unless the user has explicitly disabled it for that invocation.
- NEVER emit `PROGRAM.fragment.md` without the `# Compatible with auto-researcher SKILL.md §3 as of <ISO date>` header.
- The skill MUST read `C:\Users\Eddy\.claude\skills\auto-researcher\references\program-template.md` at runtime when present and emit a warning if the auto-researcher schema appears to have drifted from the fragment's expectations.
- NEVER commit secrets, API keys, or local file paths beyond the user's project root into any generated artifact.
