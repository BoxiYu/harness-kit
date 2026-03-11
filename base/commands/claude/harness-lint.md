---
description: "Run harness lint, fix violations, and re-run until clean."
arguments:
  - name: path
    description: "Optional path filter to lint specific files or directories."
    required: false
---

# /harness-lint

Enforce all architectural constraints. Fix violations at the root cause.

## Pre-checks

1. Verify `.harness/` directory exists in the project root.
   - If missing: STOP. Tell the user to run `harness init` first.
2. Verify `harness` CLI is available on PATH.
   - If missing: STOP. Tell the user to install harness-kit.
3. Load `.harness/AGENTS.md` to understand project rules.
4. Load `.harness/constraints/` to understand what is enforced.

## Execution

### Step 1 — Run lint with agent-friendly output

```bash
harness lint --fix-instructions $ARGUMENTS
```

- If `$ARGUMENTS` is provided, pass it as a path filter.
- If `$ARGUMENTS` is empty, lint the entire project.

### Step 2 — Parse the output

For each violation reported:

1. Read the **constraint name** and **severity** (error vs warning).
2. Read the **file path** and **line number**.
3. Read the **fix message** — this is the authoritative instruction for how to fix.
4. Read the **rule rationale** to understand why this constraint exists.

### Step 3 — Apply fixes

For each violation, ordered by severity (errors first):

1. Open the file at the reported location.
2. Read surrounding context (at least 20 lines above and below).
3. Apply the fix described in the fix message.
4. MUST: Fix the root cause, not the symptom.
   - If a layer violation says "Service must not import UI", move the dependency — do NOT suppress the check.
   - If a naming violation says "use snake_case", rename the identifier everywhere — do NOT rename just the flagged location.
5. MUST: Respect layer boundaries. Never "fix" a violation by moving code to a layer it doesn't belong in.
6. NEVER: Disable, weaken, or remove a constraint to make lint pass.
7. NEVER: Add inline suppressions or ignore comments unless explicitly told to by the user.

### Step 4 — Re-run lint

```bash
harness lint --fix-instructions $ARGUMENTS
```

- If violations remain, go back to Step 3.
- Maximum 3 iterations. If violations persist after 3 rounds:
  - STOP applying fixes.
  - Report the remaining violations to the user.
  - Explain what you tried and why it didn't work.
  - Ask the user for guidance.

### Step 5 — Verify no regressions

After all violations are fixed:

1. Run `harness lint` one final time (without `--fix-instructions`) to confirm clean output.
2. If the project has tests, run them to ensure fixes didn't break functionality.
3. If the project has type-checking, run it to ensure type safety.

## Operating Principles

- **Fix root cause, not symptoms.** A lint violation is a signal that something is structurally wrong. Trace it back to the design decision that caused it.
- **Respect layer boundaries.** The dependency model (`Types -> Config -> Repo -> Service -> Runtime -> UI`) is load-bearing. Never break it to silence a warning.
- **Never disable constraints.** Constraints exist for a reason. If you disagree with one, tell the user — don't silently remove it.
- **Minimal blast radius.** Fix exactly what is violated. Don't refactor surrounding code unless the fix requires it.
- **Preserve existing patterns.** Match the coding style already present in the file. Don't introduce new patterns as part of a lint fix.
- **Three-strike rule.** If you edit the same file 3+ times for the same violation and it still fails, something is fundamentally wrong. Stop and ask.

## Output Format

When complete, provide a summary table:

```
## Lint Summary

| Status  | Count |
|---------|-------|
| Found   | N     |
| Fixed   | N     |
| Remaining | N   |

### Violations Fixed
- `path/to/file.py:42` — [constraint-name]: description of fix applied

### Remaining (if any)
- `path/to/file.py:99` — [constraint-name]: why this could not be auto-fixed
```

If all violations are fixed, end with:

```
All constraints pass. Ready to commit.
```
