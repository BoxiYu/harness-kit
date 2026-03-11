---
description: "Create a new constraint through a guided workflow."
arguments:
  - name: description
    description: "Natural language description of the constraint you want to create."
    required: true
---

# /harness-constraint

Create a new architectural constraint through a guided workflow.

**Input**: `$ARGUMENTS` — a natural language description of what you want to constrain.

## Pre-checks

1. Verify `.harness/` directory exists in the project root.
   - If missing: STOP. Tell the user to run `harness init` first.
2. Verify `harness` CLI is available on PATH.
3. Read `.harness/constraints/` to understand existing constraints and avoid duplicates.
4. Read `.harness/memory/constitution.md` to ensure the new constraint aligns with project principles.

## Execution

### Step 1 — Analyze the request

Parse `$ARGUMENTS` to understand what the user wants to constrain.

Determine:
1. **What behavior to prevent** — the violation pattern.
2. **What behavior to enforce** — the correct pattern.
3. **Where it applies** — file patterns, directories, or language constructs.
4. **Why it matters** — the architectural principle being protected.

If the request is ambiguous, ask clarifying questions BEFORE proceeding:
- "Should this apply to all files or just specific directories?"
- "Should this be an error (blocks commit) or a warning (advisory)?"
- "Are there exceptions that should be allowed?"

### Step 2 — Choose the constraint type

Match the request to a constraint type:

| Type | Use when | Example |
|------|----------|---------|
| **naming** | Enforcing naming conventions | "All React components must use PascalCase" |
| **layers** | Enforcing dependency direction | "Services must not import from UI" |
| **boundaries** | Enforcing data validation at trust boundaries | "All API inputs must be validated" |
| **pattern** | Requiring or forbidding code patterns | "Never use `console.log` in production code" |
| **structure** | Enforcing file/directory organization | "Tests must mirror source structure" |

If the request doesn't fit any type, explain the available types and ask the user to refine.

### Step 3 — Generate the constraint YAML

Use the constraint template from `.harness/templates/constraint-template.md` as a reference.

Create a constraint YAML file with these required fields:

```yaml
name: constraint-name
description: >
  One-line description of what this constraint enforces.
type: [naming|layers|boundaries|pattern|structure]
severity: [error|warning]
enabled: true

# What to check
rule:
  # Pattern-specific fields vary by type
  pattern: "regex or glob pattern"
  scope: "file glob defining where this applies"

# Human-readable fix instructions
fix_message: >
  Clear, actionable instructions for how to fix a violation.
  Include: what is wrong, why it's wrong, and exactly how to fix it.

# Optional: examples of correct and incorrect code
examples:
  correct:
    - description: "Good example"
      code: |
        # code that follows the constraint
  incorrect:
    - description: "Bad example"
      code: |
        # code that violates the constraint
```

### Step 4 — Validate the constraint

Before installing, validate:

1. **Name is unique**: No existing constraint has the same name.
2. **Severity is appropriate**:
   - Use `error` for violations that should block commits. Prefer this for new constraints.
   - Use `warning` only for advisory rules during migration periods.
3. **fix_message is actionable**: It MUST tell the developer exactly what to do. Test: could someone who has never seen this codebase follow the fix message?
4. **Pattern is correct**: If the constraint uses regex/glob patterns, test them mentally against known files in the project.
5. **Scope is appropriate**: Not too broad (catches unrelated files) or too narrow (misses violations).
6. **No conflicts**: The new constraint doesn't contradict existing constraints.

### Step 5 — Preview and confirm

Present the constraint to the user for review:

```
## New Constraint Preview

**Name**: constraint-name
**Type**: [type]
**Severity**: [error|warning]
**Scope**: [where it applies]

### Rule
[Description of what it checks]

### Fix Message
[The fix message that will be shown on violations]

### Examples
**Correct**:
[code example]

**Incorrect**:
[code example]
```

Ask the user: **"Does this look right? I'll install it to `.harness/constraints/` when you confirm."**

MUST: Wait for user confirmation before proceeding to Step 6.

### Step 6 — Install the constraint

1. Write the YAML file to `.harness/constraints/{constraint-name}.yml`.
2. Run validation:

```bash
harness lint
```

3. Check the output:
   - If the new constraint produces **expected violations**: Report them. This is normal for a new constraint on an existing codebase.
   - If the new constraint produces **no findings**: Verify the pattern is correct. A constraint that matches nothing may be misconfigured.
   - If the new constraint causes **errors in other constraints**: Something is wrong. Revert and investigate.

### Step 7 — Report results

Summarize what was created and its immediate impact on the codebase.

## Operating Principles

- **Prefer error over warning.** Warnings get ignored. If something is important enough to constrain, it's important enough to enforce. Use `warning` only during migration periods.
- **Always include fix_message.** A constraint without a fix message causes doom loops. The fix message is not optional — it's the most important field.
- **Test before committing.** Run lint after installing to see the constraint in action. A constraint that immediately flags 500 violations may need a narrower scope or a migration plan.
- **One constraint, one concern.** Don't create a mega-constraint that checks multiple unrelated things. Split them.
- **Align with the constitution.** Every constraint should trace back to a principle in the constitution. If it doesn't, either the constitution needs updating or the constraint doesn't belong.
- **Examples are documentation.** The correct/incorrect examples in the YAML serve as living documentation. Make them realistic and representative.
- **Don't duplicate existing constraints.** Check `.harness/constraints/` before creating. If an existing constraint is close, consider extending it instead.

## Output Format

After installation:

```
## Constraint Created

**File**: `.harness/constraints/{name}.yml`
**Type**: [type]
**Severity**: [error|warning]

### Immediate Impact
- **Violations found**: N files affected
- **Action needed**: [none — codebase complies | list of files to fix]

### Next Steps
1. Review the violations (if any) and fix them, or adjust the constraint scope.
2. Run `harness lint` to verify the constraint works as expected.
3. Commit the new constraint file alongside any fixes.
```
