---
description: "Onboard to a harness-kit project. Read rules, constraints, and project health."
arguments: []
---

# /harness-setup

Onboard to this project. Understand its rules, architecture, constraints, and current health.

## Pre-checks

1. Verify `.harness/` directory exists in the project root.
   - If missing: Tell the user this project hasn't been initialized with harness-kit yet. Offer to run `harness init`.
2. Verify `harness` CLI is available on PATH.
   - If unavailable: Explain that harness-kit is not installed but you can still read the `.harness/` files directly.

## Execution

### Step 1 — Read the constitution

Read `.harness/memory/constitution.md`.

This is the project's governing document. It contains:
- Core principles that override all other rules.
- Quality standards and non-negotiable requirements.
- Architectural decisions and their rationale.

Internalize these principles. They apply to everything you do in this project.

### Step 2 — Read the agent entry point

Read `.harness/AGENTS.md`.

Extract:
- Project name and description.
- Quick rules (the 4-5 rules that apply to every task).
- Architecture overview (dependency layers, key boundaries).
- Domain context locations (which docs exist and when to load them).

MUST: Do NOT load all domain context files now. Only note what exists and where. Load them on demand when working in a specific area.

### Step 3 — Inventory active constraints

```bash
harness constraint list
```

If the CLI is not available, read `.harness/constraints/*.yml` directly.

For each constraint, note:
- **Name**: What it's called.
- **Type**: What it enforces (naming, layers, boundaries, etc.).
- **Severity**: Error (blocks commit) vs warning (advisory).
- **One-line summary**: What it prevents.

Do NOT dump the full YAML. Summarize each constraint in one line.

### Step 4 — Quick health check

```bash
harness audit
```

If the CLI is not available, perform a manual assessment:
- Count constraint files in `.harness/constraints/`.
- Check if `.harness/context/ARCHITECTURE.md` has been customized (look for `[NEEDS CLARIFICATION]` markers).
- Check if `.harness/memory/constitution.md` has been customized (look for placeholder text).
- Check if pre-commit hooks are installed (`.git/hooks/pre-commit`).

### Step 5 — Scan project structure

Get a high-level understanding of the project:

1. List top-level directories and key files.
2. Identify the primary language(s) and framework(s).
3. Note the test framework and test location.
4. Note the build system and CI configuration.
5. Check for other AI agent configs (CLAUDE.md, .cursorrules, etc.).

MUST: Keep this scan shallow. You are building a mental map, not reading every file.

### Step 6 — Check for slash commands

List available harness slash commands:

```bash
ls .claude/commands/harness-*.md 2>/dev/null
```

Note which commands are available so you can reference them in future tasks.

## Operating Principles

- **Progressive disclosure.** Don't dump everything at once. Present the most important information first, then offer to dive deeper.
- **Constitution first.** The constitution is the highest-authority document. If anything conflicts with it, the constitution wins.
- **Don't load what you don't need.** Note the existence of domain context files but only read them when working in that area. Context budget matters.
- **Summarize, don't parrot.** Rephrase information in your own words. The user wants understanding, not a copy-paste of their own docs.
- **Flag gaps.** If you notice missing or placeholder content (uncustomized templates, `[NEEDS CLARIFICATION]` markers), mention it. These are setup tasks the user may have forgotten.
- **Be honest about health.** If the project is well-configured, say so. If it's missing critical pieces, say that too. Don't sugarcoat.

## Output Format

Present the orientation briefing in this structure:

```
## Project Orientation

### Identity
- **Project**: [name]
- **Stack**: [language(s), framework(s)]
- **Harness version**: [version from AGENTS.md]

### Constitution (key principles)
1. [Most important principle]
2. [Second most important principle]
3. [Third most important principle]

### Quick Rules
1. [Rule 1]
2. [Rule 2]
3. [Rule 3]
4. [Rule 4]

### Active Constraints
| Constraint | Type | Severity | Summary |
|------------|------|----------|---------|
| ...        | ...  | ...      | ...     |

### Architecture
[One-paragraph summary of the dependency model and key boundaries]

### Available Context (load on demand)
- `.harness/context/ARCHITECTURE.md` — [status: customized/template]
- `.harness/context/FRONTEND.md` — [status: exists/missing]
- ...

### Health Status
- Constraints: [N active, N with issues]
- Documentation: [customized/template/missing]
- Hooks: [installed/not installed]
- Overall: [healthy/needs-attention/unconfigured]

### Available Commands
- `/harness-lint` — Check and fix constraint violations
- `/harness-gc` — Detect and fix codebase entropy
- `/harness-audit` — Full health report with scores
- `/harness-setup` — This command (re-run to refresh)
- `/harness-constraint` — Create new constraints
```

After presenting the briefing, ask:

> **What would you like to work on?** I'm ready to help with this project.
