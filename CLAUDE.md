# harness-kit

## Harness Engineering

This project uses harness-kit for constraint enforcement and quality management.

### Before Writing Code

1. Read `.harness/AGENTS.md` for project rules and architecture.
2. Check `.harness/constraints/` for active constraints.
3. Load domain docs from `.harness/context/` only when needed.

### Before Submitting Code

1. Run `harness lint` — all constraints must pass.
2. Run tests and type-checks.
3. If `harness lint` reports a violation, read the fix message and apply it.
4. If you edit the same file 3+ times for the same issue, stop and re-think.

### Key Commands

```bash
harness lint                    # Check all constraints
harness lint --fix-instructions # Agent-friendly output
harness gc --report             # Check for entropy
harness audit                   # Full health report
harness constraint list         # Show active constraints
```

### Architecture

See `.harness/context/ARCHITECTURE.md` for the dependency layer model.
