---
name: recursive-refine
description: "Take any generated content and recursively evaluate, diagnose, and improve it against a dynamically generated, domain-specific scoring rubric until every criterion passes a defined threshold. Includes adversarial stress-testing. Only use when explicitly called with /recursive-refine."
---

# Recursive Self-Improvement Refiner

This skill takes any generated content and recursively evaluates, diagnoses, and improves it against a dynamically generated, domain-specific scoring rubric until every criterion passes its threshold. It includes adversarial stress-testing and will never ship output that scores below threshold on any criterion.

## Workflow

### Step 0: Input Parsing

- **Content**: The draft text to refine (from attached file, pasted text, or previous tool output).
- **Optional Overrides**: User can provide a custom rubric, adversarial persona, threshold, or max iterations.

### Step 1: Dynamic Rubric & Persona Generation

This step replaces a static lookup with a 3-stage reasoning protocol to create a bespoke rubric and adversarial persona for the specific content provided.

#### Stage A: Content Analysis

The agent first analyzes the content to answer three questions:

1.  **What is the primary domain?** (e.g., Software Engineering, Finance, Design, Data Science, Marketing, Legal, Operations)
2.  **What is the specific sub-type within that domain?** (e.g., within Software Engineering → Backend API, Frontend UI, DevOps Config, ML Pipeline, CLI Tool, Database Schema)
3.  **Who is the intended audience and what is their goal?** (e.g., "a senior engineer reviewing a PR for correctness" vs. "a non-technical stakeholder reading a product spec for understanding")

*If confidence in classification is <70%, the skill falls back to the `General Content` rubric.* 

#### Stage B: Rubric Generation

Using the analysis from Stage A, the agent generates a custom rubric of 6–10 criteria. Each criterion includes:

-   **Name**: A short, specific label (e.g., "Idempotency", "Data Density", "Visual Hierarchy").
-   **What It Measures**: A one-sentence definition of the criterion.
-   **What 9/10 Looks Like**: A concrete benchmark describing an excellent implementation of the criterion.
-   **Threshold**: A pass/fail score from 7-9, derived from the criterion's importance to the domain.

#### Stage C: Adversarial Persona Derivation

The agent derives the most demanding, expert critic for the specific content sub-type. Examples:

| Content Sub-type | Derived Adversarial Persona |
|---|---|
| React UI component | Accessibility auditor + senior UX engineer |
| REST API design | API consumer who has to integrate this in production |
| ML pipeline | Peer reviewer checking for data leakage and reproducibility |
| Credit research note | Portfolio manager deciding whether to put on a trade |
| Landing page copy | Skeptical first-time visitor with 3 seconds of attention |

### Step 2: Evaluate (Score Each Criterion)

For each criterion in the newly generated rubric, the agent reads the content, assigns a score with justification, and marks it as PASS or FAIL.

### Step 3: Diagnose Failures

For each FAILING criterion, the agent provides:
1.  **What's wrong**: Specific examples from the text.
2.  **Root cause**: Why it fails the criterion.
3.  **How to fix**: Concrete, actionable rewrite instructions.

### Step 4: Adversarial Stress Test

The agent attacks the content from the perspective of the derived adversarial persona, identifying weaknesses that a demanding expert would exploit. These findings are merged into the diagnosis from Step 3.

### Step 5: Improve (Targeted Rewrite)

The agent applies the fixes from the diagnosis and adversarial review. **It only rewrites what failed**, preserving all passing sections.

### Step 6: Loop or Terminate

After the rewrite, the agent returns to **Step 2: Evaluate**. The loop terminates when:
1.  **All criteria pass**.
2.  **Max iterations** are reached (default: 5).
3.  The **score plateaus** with no improvement across 2 iterations.

### Step 7: Output Delivery

The final, refined content is delivered, along with a scorecard showing the initial scores, final scores, and total improvement for each criterion.

---

### Appendix: Example Generated Rubrics

*The following are examples of what the dynamic rubric generator might produce. They are not fixed and will be adapted based on the specific content.*

#### Example: Backend API (Python/FastAPI)

| # | Criterion | What It Measures | What 9/10 Looks Like | Threshold |
|---|---|---|---|---|
| 1 | **Correctness** | The code runs without errors and produces the expected output. | All endpoints function as documented, handle edge cases, and return correct status codes. | 9/10 |
| 2 | **Idempotency** | Endpoints intended to be idempotent (e.g., PUT, DELETE) can be called multiple times without changing the result beyond the initial application. | A `DELETE` request, if called twice on the same resource, returns a `404` on the second call, not a `500`. | 9/10 |
| 3 | **Security** | The code is free from common vulnerabilities (e.g., injection, improper auth). | Inputs are validated and sanitized; authentication and authorization are correctly implemented on all protected endpoints. | 9/10 |
| 4 | **Readability** | The code is clean, well-formatted, and uses clear naming conventions. | A new developer can understand the purpose of a function or class without needing to read extensive comments. | 8/10 |
| 5 | **Error Handling** | The API gracefully handles bad inputs and internal errors, returning informative error messages. | A request with a missing required field returns a `422 Unprocessable Entity` with a clear message, not a `500 Internal Server Error`. | 8/10 |

#### Example: UI Design (Figma Component)

| # | Criterion | What It Measures | What 9/10 Looks Like | Threshold |
|---|---|---|---|---|
| 1 | **Visual Hierarchy** | The arrangement of elements clearly guides the user's eye to the most important information. | The primary action is immediately obvious; secondary and tertiary elements are visually distinct and subordinate. | 9/10 |
| 2 | **Accessibility** | The design meets WCAG 2.1 AA standards for color contrast, touch target size, and focus states. | All text has a contrast ratio of at least 4.5:1; all interactive elements have clear focus indicators. | 9/10 |
| 3 | **Consistency** | The component adheres to the established design system (spacing, typography, color, iconography). | The component uses the same spacing tokens, font styles, and interactive patterns as other components in the system. | 8/10 |
| 4 | **Statefulness** | All interactive states (hover, focused, active, disabled) are visually distinct and clearly defined. | A disabled button is visually non-interactive and has a `not-allowed` cursor on hover. | 8/10 |
| 5 | **Clarity** | The purpose and function of the component are immediately understandable without explanation. | An icon-only button has a clear tooltip on hover explaining its function. | 8/10 |

---

## Windows/Cursor Compatibility Notes

- No environment-specific changes required � this skill is fully tool and OS agnostic.
- Works in Cursor without modification.
