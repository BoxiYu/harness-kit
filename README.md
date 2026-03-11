# harness-kit

**Constraints, feedback loops, and lifecycle systems that make AI coding agents reliable at scale.**

harness-kit is a framework for [Harness Engineering](https://openai.com/index/harness-engineering/) — the discipline of designing the environment, constraints, and feedback systems that surround an AI coding agent so it produces reliable, maintainable code.

## Try It (30 seconds)

```bash
# Install
uvx --from git+https://github.com/BoxiYu/harness-kit.git harness init my-app --ai claude

# Enter the project
cd my-app

# See what constraints are active
harness constraint list

# Add your own constraint
harness constraint add \
  --name "no-print" \
  --rule "Do not use print() in production code" \
  --fix "Replace print() with logger.info() or logger.debug()"

# Check your codebase
harness lint --fix-instructions

# Run garbage collection
harness gc

# Full health report
harness audit
```

That's it. Your project now has:
- Architectural constraints that **block** violations at commit time
- Error messages written for AI agents (not humans) — they tell the agent **exactly how to fix it**
- Entropy detection that catches stale docs, dead code, and pattern drift
- A doom loop detector that warns when an agent is stuck editing the same file

## Why Harness Engineering?

AI coding agents can write a lot of code fast. But without guardrails, that code drifts from your architecture, accumulates entropy, and becomes unmaintainable. Harness Engineering fixes this by:

- **Enforcing architectural constraints mechanically** — not via instructions the agent might ignore, but via linters that block violations
- **Making error messages actionable** — when a constraint is violated, the error message tells the agent exactly how to fix it
- **Fighting entropy continuously** — periodic garbage collection scans for stale docs, pattern drift, and constraint bypasses
- **Detecting doom loops** — if an agent edits the same file 3+ times in 5 minutes, it gets an advisory to stop and re-think

Read the full rationale: [Why Harness Engineering?](./docs/why-harness-engineering.md)

## How It Relates to spec-kit

| | [spec-kit](https://github.com/github/spec-kit) | harness-kit |
|---|---|---|
| **Focus** | What to build | How to keep the agent on track while building |
| **Phase** | Before coding (specs → plans → tasks) | During coding (constraints → feedback → cleanup) |
| **Output** | Specifications, plans, task lists | Linter rules, pre-commit hooks, health reports |

They are **complementary**. Use spec-kit to define what to build, then harness-kit to ensure quality during implementation.

## The Core Insight

Traditional approach — the agent might ignore it:
```markdown
# CLAUDE.md
Please follow the layered architecture. Each layer should only import from lower layers.
```

Harness approach — the agent **cannot** ignore it:
```yaml
# .harness/constraints/layers.yml
name: dependency-layers
severity: error
fix_message: |
  VIOLATION at {file}:{line}
    Rule: {source_layer} must not import from {target_layer}.
    Fix: Move shared logic to a lower layer, or use a Provider interface.
```

The first is a suggestion. The second is a wall — with a door marked "here's how to do it right."

## Get Started

### Install (persistent)

```bash
uv tool install harness-kit --from git+https://github.com/BoxiYu/harness-kit.git
```

### Initialize in an existing project

```bash
cd your-project
harness init --here --ai claude
```

### Initialize a new project

```bash
harness init my-project --ai claude
```

### Supported `--ai` options

`claude`, `copilot`, `cursor`, `gemini`, `codex`

## CLI Reference

| Command | Description |
|---------|-------------|
| `harness init` | Bootstrap `.harness/` directory in a project |
| `harness check` | Verify harness infrastructure setup |
| `harness constraint list` | List all active constraints |
| `harness constraint add` | Add a new constraint with `--name`, `--rule`, `--fix` |
| `harness constraint check` | Run constraint checks |
| `harness lint` | Run all constraint checks |
| `harness lint --fix-instructions` | Agent-friendly output with remediation instructions |
| `harness gc` | Run garbage collection (entropy detection) |
| `harness audit` | Generate codebase health report with context budget |
| `harness loop record <file>` | Record a file edit for doom loop detection |
| `harness loop status` | Show recent edit frequency |
| `harness loop clear` | Clear edit history |

## The Four Pillars

### 1. Architectural Constraints
Mechanically enforced rules defined in YAML. Each constraint includes a `fix_message` that doubles as a remediation instruction for AI agents. Three built-in constraints: dependency layers, naming conventions, boundary validation.

### 2. Feedback Loops
Pre-commit hooks run `harness lint` on every commit. Failures include fix instructions. The doom loop detector tracks edit frequency and advises agents when they're stuck.

### 3. Context Architecture
Tiered, progressive context disclosure. `AGENTS.md` is the entry point (~100 lines). Domain docs load on demand. `harness audit` tracks context budget — target is under 40% utilization.

### 4. Garbage Collection
`harness gc` checks for: documentation freshness (stale docs), empty/orphaned files, constraint definition consistency. Catches entropy before it compounds.

## Dogfooding

harness-kit uses itself. The `.harness/` directory in this repo contains constraints tailored to harness-kit's own architecture. Running `harness lint` on this codebase is part of our development workflow. We've already caught and fixed a cross-command import violation this way.

## Supported AI Agents

| Agent | Context File Generated |
|-------|----------------------|
| Claude Code | `CLAUDE.md` + `.claude/commands/` slash commands |
| GitHub Copilot | `.github/copilot-instructions.md` |
| Cursor | `.cursorrules` |
| Gemini CLI | `GEMINI.md` |
| Codex CLI | `AGENTS.md` |

## Prerequisites

- Python 3.11+
- [uv](https://docs.astral.sh/uv/)
- Git

## License

MIT
