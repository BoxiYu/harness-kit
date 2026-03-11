# harness-kit

**Constraints, feedback loops, and lifecycle systems that make AI coding agents reliable at scale.**

harness-kit is a framework for [Harness Engineering](https://openai.com/index/harness-engineering/) — the discipline of designing the environment, constraints, and feedback systems that surround an AI coding agent so it produces reliable, maintainable code.

## Why Harness Engineering?

AI coding agents can write a lot of code fast. But without guardrails, that code drifts from your architecture, accumulates entropy, and becomes unmaintainable. Harness Engineering fixes this by:

- **Enforcing architectural constraints mechanically** — not via instructions the agent might ignore, but via linters that block violations
- **Making error messages actionable** — when a constraint is violated, the error message tells the agent exactly how to fix it
- **Fighting entropy continuously** — periodic garbage collection agents scan for stale docs, pattern drift, and constraint bypasses
- **Managing context budgets** — tiered context disclosure keeps agents focused, not overwhelmed

## How It Relates to spec-kit

| | [spec-kit](https://github.com/github/spec-kit) | harness-kit |
|---|---|---|
| **Focus** | What to build | How to keep the agent on track while building |
| **Phase** | Before coding (specs → plans → tasks) | During coding (constraints → feedback → cleanup) |
| **Output** | Specifications, plans, task lists | Linter rules, pre-commit hooks, health reports |

They are **complementary**. Use spec-kit to define what to build, then harness-kit to ensure quality during implementation.

## Get Started

### Install

```bash
uv tool install harness-kit --from git+https://github.com/YOUR_ORG/harness-kit.git
```

### Initialize in your project

```bash
cd your-project
harness init --ai claude
```

This creates a `.harness/` directory with:
- **Constraint definitions** (YAML) — architectural rules the agent must follow
- **Context templates** — tiered documentation for agent context management
- **Constitution** — project-level principles for AI-assisted development
- **Pre-commit hooks** — automated constraint enforcement on every commit

### Define constraints

```bash
# Add a constraint with an agent-friendly fix message
harness constraint add \
  --name "api-auth" \
  --rule "All API route handlers must use auth middleware" \
  --fix "Wrap the handler with @require_auth decorator"
```

The `--fix` message is what the AI agent sees when it violates the constraint. This is the core harness engineering insight: **error messages ARE remediation instructions**.

### Run constraint checks

```bash
harness lint                    # Check all constraints
harness lint --fix-instructions # Agent-friendly output with fix messages
```

Example output:
```
VIOLATION [api-auth] at src/routes/users.py:42
  Rule: All API route handlers must use auth middleware
  Fix: Wrap the handler with @require_auth decorator
  Context: The handler `get_user()` is missing authentication.
```

### Fight entropy

```bash
harness gc                      # Run garbage collection checks
harness gc --report             # Report only, no fixes
harness audit                   # Full health report
```

## CLI Reference

| Command | Description |
|---------|-------------|
| `harness init` | Bootstrap `.harness/` directory in a project |
| `harness check` | Verify harness infrastructure setup |
| `harness constraint list` | List all active constraints |
| `harness constraint add` | Add a new constraint |
| `harness constraint check` | Run constraint checks |
| `harness lint` | Run all constraint checks |
| `harness gc` | Run garbage collection (entropy detection) |
| `harness audit` | Generate codebase health report |

## The Four Pillars

### 1. Architectural Constraints
Mechanically enforced rules defined in YAML. Each constraint includes a `fix_message` that doubles as a remediation instruction for AI agents.

### 2. Feedback Loops
Every code change flows through: `lint → type-check → test → build → security scan`. Pre-commit hooks ensure no code bypasses the pipeline.

### 3. Context Architecture
Tiered, progressive context disclosure. An `AGENTS.md` entry point links to domain-specific docs loaded on demand. Target: keep context utilization under 40%.

### 4. Garbage Collection
Periodic checks for documentation freshness, pattern drift, constraint bypasses, and stale artifacts. Continuous entropy resistance.

## Supported AI Agents

| Agent | Support | Context File |
|-------|---------|-------------|
| Claude Code | Yes | `CLAUDE.md` + `.claude/commands/` |
| GitHub Copilot | Yes | `.github/copilot-instructions.md` |
| Cursor | Yes | `.cursorrules` |
| Gemini CLI | Yes | `GEMINI.md` |
| Codex CLI | Yes | `AGENTS.md` |

## Prerequisites

- Python 3.11+
- [uv](https://docs.astral.sh/uv/)
- Git

## License

MIT
