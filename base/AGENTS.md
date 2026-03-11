# AGENTS.md

> Entry point for AI coding agents. This file is auto-loaded at session start.
> Keep it under 100 lines. Use links to deeper docs for details.

## Project Overview

- **Project**: [PROJECT_NAME]
- **Harness Kit**: v0.1.0
- **Constitution**: `.harness/memory/constitution.md`

## Quick Rules

1. **Run `harness lint` before submitting any code.** Violations block commits.
2. **Read constraint fix messages carefully.** They tell you exactly how to fix the violation.
3. **Don't load context you don't need.** Check the domain docs below only when working in that area.
4. **If you edit the same file 3+ times for the same issue, stop and re-think.**

## Architecture

See `.harness/context/ARCHITECTURE.md` for the full system architecture.

**Dependency layers** (import only leftward):
```
Types → Config → Repo → Service → Runtime → UI
```

## Domain Context (load on demand)

| Domain | Doc | When to load |
|--------|-----|-------------|
| Architecture | `.harness/context/ARCHITECTURE.md` | System design decisions |
| Frontend | `.harness/context/FRONTEND.md` | UI components, styling |
| Backend | `.harness/context/BACKEND.md` | API routes, services |
| Security | `.harness/context/SECURITY.md` | Auth, permissions, data handling |
| Database | `.harness/context/DATABASE.md` | Schema, migrations, queries |

## Active Constraints

Run `harness constraint list` to see all active constraints.

Constraint definitions: `.harness/constraints/`

## Feedback Pipeline

Every change must pass:
```
harness lint → type-check → test → build → security scan
```

## Useful Commands

```bash
harness lint                    # Run all constraint checks
harness lint --fix-instructions # Agent-friendly violation output
harness gc --report             # Check for entropy/drift
harness audit                   # Full health report
harness constraint list         # Show active constraints
```
