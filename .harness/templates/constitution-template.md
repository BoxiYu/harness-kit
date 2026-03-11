# Project Constitution

> Governing principles for AI-assisted development in this project.
> This document is loaded into every agent session. Keep it concise and actionable.

## Identity

- **Project**: harness-kit
- **Created**: 2026-03-11
- **Last Updated**: 2026-03-11

## Core Principles

### 1. Constraints Are Law

- Architectural constraints defined in `.harness/constraints/` are **mechanically enforced**.
- No agent may bypass a constraint. If a constraint blocks progress, the correct action is to **propose a constraint amendment**, not to work around it.
- Constraint violation messages contain remediation instructions — follow them.

### 2. Feedback Before Commit

- All code must pass the full feedback pipeline before submission: `lint → type-check → test → build → security scan`.
- A failing check is information, not an obstacle. Read the error, apply the fix, re-run.
- If the same file is edited more than 3 times for the same issue, stop and re-evaluate the approach.

### 3. Context Discipline

- Do not load context you do not need. Use tiered disclosure: start with `AGENTS.md`, load domain docs only when working in that domain.
- Keep context utilization under 40% of your window.
- When in doubt about a convention, check `.harness/context/` before guessing.

### 4. Entropy Resistance

- Every PR should leave the codebase **at least as clean** as it found it.
- Do not introduce dead code, unused imports, or orphaned files.
- Documentation must be updated in the same PR as the code it describes.
- If you notice drift from established patterns, flag it — do not silently perpetuate it.

### 5. Boundary Validation

- Validate data at system boundaries (user input, external APIs, database queries).
- Trust internal code and framework guarantees. Do not add redundant validation in business logic.
- Never trust data that crosses a trust boundary without validation.

## Anti-Patterns to Avoid

- **Monolithic context**: Do not dump entire codebases or docs into a single prompt.
- **Retry loops**: Do not retry the same failing action. Diagnose the root cause.
- **Implicit conventions**: If a convention exists, it must be documented in `.harness/context/` or enforced via a constraint.
- **Over-engineering**: Solve the current problem. Do not design for hypothetical future requirements.

## Quality Standards

- [NEEDS CLARIFICATION: Define your testing requirements — e.g., minimum coverage, required test types]
- [NEEDS CLARIFICATION: Define your performance requirements — e.g., response time SLAs, resource limits]
- [NEEDS CLARIFICATION: Define your security requirements — e.g., OWASP compliance, auth standards]

## Review & Acceptance

- [ ] All constraints pass (`harness lint`)
- [ ] All tests pass
- [ ] Documentation updated
- [ ] No new constraint violations introduced
- [ ] GC report shows no regressions (`harness gc --report`)
