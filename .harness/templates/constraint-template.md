# Constraint: [CONSTRAINT_NAME]

> A constraint is a mechanically enforced rule. Its error message IS the remediation instruction.

## Metadata

- **ID**: [SHORT_ID, e.g., "api-auth"]
- **Severity**: error | warning
- **Created**: 2026-03-11
- **Rationale**: [Why does this constraint exist? What problem does it prevent?]

## Rule Definition

**Plain English**: [Describe the rule in one sentence]

**Applies to**: [File patterns, e.g., "src/routes/**/*.py"]

**Check logic**: [How to verify — regex, AST check, import analysis, file structure check]

## Fix Message

> This is what the AI agent sees when it violates this constraint.
> Write it as a direct, actionable remediation instruction.

```
VIOLATION [{SHORT_ID}] at {file}:{line}
  Rule: [One-line rule description]
  Fix: [Exact action the agent should take]
  Context: [Why this specific code is in violation]
  Example:
    [Show the correct pattern]
```

## Examples

### Passing

```
[Show code that satisfies this constraint]
```

### Failing

```
[Show code that violates this constraint]
```

## YAML Definition

```yaml
name: [SHORT_ID]
description: [One-line description]
severity: error
file_patterns:
  - "src/**/*.py"
  - "!src/**/tests/**"
check:
  type: [regex | import | structure | custom]
  pattern: [Check-specific configuration]
fix_message: |
  [The fix message template with {file}, {line}, {detail} placeholders]
```
