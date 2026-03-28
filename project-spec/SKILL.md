---
name: project-spec
description: "Interview the user in-depth about their project, asking detailed questions to create a comprehensive project specification and implementation roadmap. Spec-only — stops after writing project-spec.md and project-constitution.md; does not execute implementation. Only use when explicitly called with /project-spec."
---

# Create Project Specification

## Phase 1: Project Analysis & Domain Detection

1. Check if a `project-spec.md` or `project-constitution.md` file already exists in the workspace. If yes, use the `message` tool to ask the user if they want to update the existing spec or start a new one. Wait for their reply before proceeding.
2. Analyze the user's project description (`$ARGUMENTS`). Identify the core components, goals, and project archetype (e.g., SaaS, e-commerce, data pipeline, mobile app, AI product, internal tool). 
3. Read the file at `references/domain-templates.md` in this skill's folder (`C:\Users\Eddy\.claude\skills\project-spec\references\domain-templates.md`) to load archetype-specific questions. Inject these into your dynamically generated interview categories.
4. Generate 4-6 high-level interview categories specific to the project, ordered from highest architectural impact to lowest (e.g., core data model before deployment).

## Phase 2: In-Depth Interview (with Progress Tracking)

Conduct the interview using the `message` tool. At the start of every message, display a progress indicator:

> **[Phase X of Y: Category Name — ████░░░░░░ Z%]**

### CRITICAL: Question Format Rules

Every single question MUST follow this exact format:

1. **Always list options as a), b), c), d), etc.** — never ask open-ended questions without providing concrete options to choose from.
2. **Always pre-select your best-guess answer** — mark it clearly with **[RECOMMENDED]** so the user can instantly accept it or override with a different choice.
3. **Allow the user to quickly accept or override** — phrase each question so the user can simply reply with the letter (e.g., "1: a, 2: c, 3: b") or say "all defaults" to accept every recommendation at once.
4. **Group questions into numbered batches** of 4-6 questions per round for efficient review.

At the end of each batch, include this prompt:

> **Quick reply:** Accept all defaults for *this batch* by saying "all good", or override specific ones like "1: c, 3: a". You can also add notes to any answer.

*Note: If the user provides a custom text answer that doesn't match an option, acknowledge it, record it, and proceed to the next batch. "All good" applies to the current batch only — not all remaining phases.*

## Phase 3: Devil's Advocate Review

After the user answers the final batch of questions, generate an initial requirements summary using the `message` tool. 

Immediately following the summary in the same message, conduct an adversarial review. Adopt the perspective of a skeptical senior architect and identify 3-5 potential risks across these categories: Security, Scalability, Integration Complexity, Edge Cases, or Timeline Realism. 

Use the "5 Whys" technique (probing the root cause of a requirement) to challenge at least one major architectural choice. Present these as numbered challenges.

**Exit Condition:** End the message by explicitly asking the user: "How would you like to address these risks? We can adjust the architecture, or accept the risks and proceed to planning." **Wait for the user's reply.** Update the requirements based on their answer.

## Phase 4: Plan Validation Checkpoint

Once risks are resolved, use the `message` tool to generate a high-level implementation roadmap with 8-10 numbered phases. Each phase must include a title, key tasks, and dependencies. 

**Exit Condition:** End the message by asking: "Does this roadmap look correct? Reply 'approved' or suggest changes." **Wait for the user's explicit approval.** If they suggest changes, update the roadmap and ask for approval again.

## Phase 5: Radical Innovation Step

After the roadmap is approved, answer the following question internally: "What is the single smartest, most radically innovative, and most compelling addition I could make to this project right now?"

If the idea can be implemented without adding new external dependencies or extending the timeline by more than 10% (this is the definition of "actionable and within scope"), propose it to the user using the `message` tool. If they approve, update the spec. Otherwise, proceed to Phase 6 (Recursive Refinement).

## Phase 6: Recursive Refinement (via /recursive-refine)

Before writing any files, draft both `project-constitution.md` and `project-spec.md` **in memory** using the templates from Phase 7. Then run the full `/recursive-refine` workflow (from `C:\Users\Eddy\.claude\skills\recursive-refine\SKILL.md`) on each draft:

1. **Draft both documents** internally using all gathered requirements, the approved roadmap, and any innovation additions.
2. **Run /recursive-refine on `project-spec.md` draft first.** Follow every step of the recursive-refine skill:
   - Step 1: Generate a domain-specific rubric (the domain is "Project Specification / Software Architecture"; the audience is "a developer or AI agent who must implement this spec without further clarification").
   - Steps 2–6: Evaluate → Diagnose → Adversarial Stress Test → Improve → Loop until all criteria pass, max iterations reached, or score plateaus.
   - Step 7: Capture the final refined content and scorecard.
3. **Run /recursive-refine on `project-constitution.md` draft.** Same process — the audience is "a developer who needs unambiguous hard constraints at a glance."
4. **Present the final scorecards** for both documents to the user. Show initial vs. final scores and total improvement per criterion.
5. Proceed to Phase 7 to write the refined versions to disk.

**Exit Condition:** Both documents must have all rubric criteria at PASS before proceeding to Phase 7. If max iterations are reached with failures remaining, present the remaining issues to the user and ask whether to proceed anyway or manually address them.

## Phase 7: Write the Final Specification

Use the `file` tool to write the **refined** specification to two files in the project root:

**File 1: `project-constitution.md`** — The immutable core. Must be formatted exactly like this:
```markdown
# Project Constitution
## Technology Stack
- [Framework/Language + Version]
- [Database + Version]
## Project Structure
- `src/` - [purpose]
- `tests/` - [purpose]
## Executable Commands
- Build: `[exact command with flags]`
- Test: `[exact command with flags]`
## Hard Boundaries
- [What the AI must never modify or create, e.g., "Never commit secrets"]
```

**File 2: `project-spec.md`** — The full specification. Must be formatted exactly like this:
```xml
<project_specification>
  <project_name>[Concise project title]</project_name>
  <overview>[4-5 sentence summary: what, why, who, and how success is measured]</overview>
  <technology_stack>[Exact frameworks, libraries, and versions used]</technology_stack>
  <assumptions>[List of things treated as true without verification]</assumptions>
  <out_of_scope>[Features explicitly deferred or excluded]</out_of_scope>
  <core_features>
    <feature name="[Name]">[User story format with acceptance criteria]</feature>
  </core_features>
  <database_schema>
    <table name="[Name]">[field_name] [TYPE] [constraints]</table >
  </database_schema>
  <api_endpoints_summary>
    <endpoint>[HTTP_VERB] [path] — [Description]</endpoint>
  </api_endpoints_summary>
  <implementation_steps>[The approved 8-10 phase roadmap]</implementation_steps>
  <success_criteria>
    <functional>[What must work]</functional>
    <ux>[User experience requirements]</ux>
    <technical>[Code quality and performance requirements]</technical>
  </success_criteria>
</project_specification>
```

**Exit Condition:** After writing both files, use the `shell` tool to run `ls -la` to verify they exist. Then use the `message` tool to tell the user the spec is complete. **STOP HERE.** Do not offer or execute Phase 8. The workflow ends with the delivered specification.

---

**Project Description**: $ARGUMENTS

---

## Windows/Cursor Compatibility Notes

- Phase 1 Step 3: domain-templates.md path changed from Manus absolute path to: `C:\Users\Eddy\.claude\skills\project-spec\references\domain-templates.md`.
