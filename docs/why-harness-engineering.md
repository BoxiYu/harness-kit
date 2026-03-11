# Why Harness Engineering?

## The Problem

AI coding agents can write a lot of code fast. GPT-4, Claude, Gemini — they can all generate hundreds of lines of working code in seconds. But "working" and "maintainable" are different things.

Without guardrails, AI-generated codebases develop problems quickly:

- **Architecture drift**: The agent takes shortcuts. Service layer imports from UI layer. Types depend on business logic. Dependencies go in every direction.
- **Pattern inconsistency**: The first 10 files follow one pattern. The next 10 follow a different one. By file 50, there are five different ways to do the same thing.
- **Entropy accumulation**: Dead code, stale documentation, orphaned files. The agent creates things but never cleans up.
- **Doom loops**: The agent gets stuck — editing the same file over and over, trying the same approach that keeps failing.

These problems are invisible at first. The code compiles. The tests pass. But six months later, the codebase is a mess that no human or AI can navigate efficiently.

## The Insight

In February 2026, OpenAI published a field report about their Codex team. They had built a production application with over 1 million lines of code — and zero lines were written by human hands.

How? Not by using a better model. By building a better **harness**.

The key insight: **don't tell the agent what to do — constrain what it CAN do.**

Instead of writing instructions like "please follow the layered architecture", they built custom linters that mechanically reject any code that violates the architecture. The error messages from these linters were written specifically for AI agents — they don't just say "violation at line 42", they say "this import goes the wrong direction; move the shared logic to a lower layer or introduce a Provider interface."

This is Harness Engineering: **the discipline of designing the constraints, feedback loops, and lifecycle systems that surround an AI coding agent.**

## The Four Pillars

### 1. Architectural Constraints

Rules that are enforced mechanically, not by instruction.

The traditional approach:
```
# CLAUDE.md
Please follow the layered architecture:
Types → Config → Repo → Service → Runtime → UI
Each layer should only import from lower layers.
```

The harness approach:
```yaml
# .harness/constraints/layers.yml
name: dependency-layers
severity: error
layers:
  - {name: types, index: 0, patterns: ["src/types/**"]}
  - {name: service, index: 3, patterns: ["src/services/**"]}
  - {name: ui, index: 5, patterns: ["src/ui/**"]}
fix_message: |
  VIOLATION at {file}:{line}
    Rule: {source_layer} must not import from {target_layer}.
    Fix: Move shared logic to a lower layer, or use a Provider interface.
```

The first approach relies on the agent reading and remembering the instruction. The second approach catches violations at commit time and tells the agent exactly how to fix them. One is a suggestion. The other is a wall.

### 2. Feedback Loops

Every action the agent takes flows through a pipeline of checks:

```
code → lint → type-check → test → build → security scan
```

Each check provides a signal. If lint fails, the error message is the fix instruction. If the test fails, the failure output shows what went wrong. The agent gets immediate, specific, actionable feedback — not vague "something is wrong" messages.

The critical design principle: **error messages are written for the AI agent, not for humans.** A human can interpret a cryptic compiler error. An agent needs structured, explicit remediation instructions.

### 3. Context Architecture

AI agents have limited context windows. Loading too much information degrades performance — research shows agent effectiveness starts declining around 40% context utilization.

Harness Engineering treats context as architecture:

- **Tier 1**: `AGENTS.md` — always loaded, ~100 lines, table of contents
- **Tier 2**: Domain docs (`FRONTEND.md`, `BACKEND.md`) — loaded on demand
- **Tier 3**: Design decisions, references — loaded only when needed

This is the opposite of dumping everything into a single instruction file. Each tier is sized and scoped so the agent gets exactly the context it needs — no more, no less.

### 4. Garbage Collection

AI-generated codebases accumulate entropy faster than human-written ones. Harness Engineering introduces periodic "garbage collection" — automated checks that scan for:

- **Documentation freshness**: Does the doc match the current code?
- **Pattern drift**: Is code deviating from established conventions?
- **Constraint bypasses**: Did something slip through the linter?
- **Stale artifacts**: Dead code, unused imports, orphaned files

OpenAI's team replaced their weekly "AI slop cleanup" sprints with automated GC agents that continuously scan and submit fix PRs. The result: entropy went from a growing problem to a background process.

## How harness-kit Implements This

harness-kit is a CLI toolkit that sets up Harness Engineering infrastructure in any project:

```bash
harness init --ai claude     # Bootstrap .harness/ directory
harness constraint add       # Define architectural constraints
harness lint                 # Run constraint checks (agent-friendly output)
harness gc                   # Run garbage collection
harness audit                # Generate health report
harness loop status          # Check for doom loops
```

It generates:
- YAML constraint definitions with fix messages
- Pre-commit hooks that enforce constraints at commit time
- Tiered context architecture (`AGENTS.md` → domain docs)
- GC configuration for continuous entropy resistance
- Loop detection that advises agents when they're stuck

## How It Relates to spec-kit

[spec-kit](https://github.com/github/spec-kit) and harness-kit are complementary:

| | spec-kit | harness-kit |
|---|---|---|
| Phase | Before coding | During coding |
| Focus | What to build | How to keep quality while building |
| Output | Specs, plans, tasks | Constraints, hooks, health reports |
| Controls | The "what" and "why" | The "how well" |

Use spec-kit to define what to build. Use harness-kit to ensure the agent builds it right.

## Further Reading

- [OpenAI: Harness Engineering](https://openai.com/index/harness-engineering/) — The original field report
- [Martin Fowler: Harness Engineering](https://martinfowler.com/articles/exploring-gen-ai/harness-engineering.html) — Analysis and context
- [GitHub spec-kit](https://github.com/github/spec-kit) — Complementary spec-driven development toolkit
