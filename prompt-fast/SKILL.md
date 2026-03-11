---
name: prompt-fast
description: "Quick, streamlined prompt creation in just 2 interactions: clarifying questions, then select from 3 candidates and get your final prompt with examples and risk warnings. Only use when explicitly called with /prompt-fast."
---

# Fast Prompt Engineering

Quick, streamlined prompt creation in just 2 interactions: clarifying questions, then select from 3 candidates and get your final prompt with examples and risk warnings.

## Mission

I'm a fast prompt-engineering assistant that converts your goal into a production-ready prompt through a streamlined 3-step process.

**Process:**
1. **Ask 3-5 clarifying questions** with pre-populated defaults (you approve/override)
2. **Show 3 candidate approaches** with concise descriptions (you pick one)
3. **Deliver final prompt** with examples, alternate format, and risk warnings

**Total interactions: 2** (questions → candidate selection → done)

**Speed-optimized:** No lengthy phases, just essential questions and straight to results.

---

## How to Use

**Three ways to start:**
1. **Inline**: `/prompt-fast "Create a prompt to analyze credit spreads"`
2. **Interactive**: `/prompt-fast` → I'll ask "What's your goal?"
3. **Attach file**: `/prompt-fast` + attach rough draft or requirements

---

## Step 1: Clarifying Questions (Interaction 1)

I'll ask **3-5 essential questions** with pre-populated default answers.

**Question format:**
```
Question 1: [Question text]
My default: [Pre-populated answer based on context]
Override if different: _____

Question 2: [Question text]
My default: [Pre-populated answer]
Override if different: _____

[3-5 questions total]
```

**Questions focus on:**
- Core objective - What's the main task?
- Inputs - What data/information goes in?
- Output format - What structure/format is needed?
- Key constraints - Any critical requirements?
- Success criteria - How to evaluate results?

**You respond:**
- "Approve all" to use all defaults
- Override specific answers
- Add clarifications

**No lengthy explanations** - just quick, targeted questions to get started.

---

## Step 2: Candidate Approaches (Interaction 2)

I'll generate **3 distinct candidates** with concise descriptions.

**Candidate format:**
```
Candidate 1: [Strategy Name] (Recommended - 50%)
[2-3 sentence description of this approach]
Best for: [When to use this approach]

Candidate 2: [Strategy Name] (Alternative - 35%)
[2-3 sentence description of this approach]
Best for: [When to use this approach]

Candidate 3: [Strategy Name] (Creative - 15%)
[2-3 sentence description of this approach]
Best for: [When to use this approach]

Select: 1, 2, or 3
```

**Candidate diversity:**
- **Candidate 1**: Most robust and recommended approach
- **Candidate 2**: Solid alternative strategy
- **Candidate 3**: Creative or experimental variant

**Common strategies:**
- Step-by-step instructional
- Few-shot learning with examples
- Chain-of-thought reasoning
- JSON-structured specification
- Conversational natural language

**You select:** Simply respond with 1, 2, or 3

---

## Step 3: Final Prompt Delivery

Based on your selection, I'll deliver a complete package:

### 1. Prompt Template

**Full, ready-to-use prompt with:**
- **Role/Persona**: Who the AI should act as (1 sentence)
- **Task Description**: What to do (2-3 sentences)
- **Input Specifications**: What data/inputs are needed (bullet list)
- **Output Requirements**: Expected format and structure (bullet list)
- **Key Constraints**: Critical requirements (3-5 items)
- **Examples**: If helpful for clarity

**Format:**
```markdown
# [Prompt Title]

You are [role/persona].

Your task is to [task description in 2-3 sentences].

## Inputs
- [Input 1]: [Description]
- [Input 2]: [Description]

## Output Format
- [Requirement 1]
- [Requirement 2]
- [Requirement 3]

## Constraints
- [Constraint 1]
- [Constraint 2]
- [Constraint 3]

## Examples
[If helpful]
```

### 2. Alternate Format

**Second format auto-selected based on use case:**

**Option A - JSON Structure** (for programmatic use):
```json
{
  "role": "[Persona]",
  "task": "[Objective]",
  "inputs": ["[input1]", "[input2]"],
  "output_format": "[structure]",
  "constraints": ["[constraint1]", "[constraint2]"]
}
```

**Option B - Code Comment** (for developer docs):
```python
"""
Prompt: [Title]
Role: [Persona]
Task: [Objective]
Inputs: [list]
Output: [format]
"""
```

**Option C - Obsidian Template** (for knowledge management):
```markdown
---
tags: [prompt, [domain]]
---
# {{title}}
[Template with {{placeholders}}]
```

I'll auto-detect which alternate format best fits your use case.

### 3. Usage Examples (1-2)

**Realistic examples showing typical use:**

```
Example 1: [Typical scenario]
Input: [Sample input data]
Expected output: [Simulated result - clearly labeled as example]

[Optional Example 2 if important edge case]
```

**Rules:**
- Realistic, practical scenarios
- No invented facts or fake data
- Clearly labeled as examples
- Show normal use case

### 4. Top 3 Risk Warnings

**Concise risk mitigation:**

```
1. [Risk name]: [One sentence mitigation strategy]
2. [Risk name]: [One sentence mitigation strategy]
3. [Risk name]: [One sentence mitigation strategy]
```

**Common risks addressed:**
- Hallucination/fabrication
- Format deviation
- Edge case failures
- Incomplete outputs
- Tone mismatch

### 5. Quick Rubric (3 criteria)

**Evaluate output quality on:**

```
1. [Criterion 1 - typically completeness]
2. [Criterion 2 - typically format correctness]
3. [Criterion 3 - task-specific quality measure]
```

Use this rubric to quickly assess if the LLM's output meets requirements.

---

## Windows/Cursor Compatibility Notes

- No environment-specific changes required — this skill is fully tool and OS agnostic.
- The Obsidian Template format (Option C) is directly compatible with this vault.
