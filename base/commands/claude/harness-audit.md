---
description: "Run harness audit to generate a full health report with scores and recommendations."
arguments: []
---

# /harness-audit

Generate a comprehensive health assessment of the project's harness infrastructure.

## Pre-checks

1. Verify `.harness/` directory exists in the project root.
   - If missing: STOP. Tell the user to run `harness init` first.
2. Verify `harness` CLI is available on PATH.
   - If missing: STOP. Tell the user to install harness-kit.
3. Load `.harness/memory/constitution.md` for project principles.
4. Load `.harness/AGENTS.md` for current project rules.

## Execution

### Step 1 — Run the audit

```bash
harness audit
```

Capture the full output including all health scores and findings.

### Step 2 — Analyze health scores

The audit produces scores across multiple dimensions. For each dimension:

1. **Record the score** (0-100 scale).
2. **Identify the trend** — is it improving, stable, or declining compared to previous audits?
3. **Note critical findings** — anything scored below 60 needs immediate attention.

Key dimensions to track:

| Dimension | What it measures | Healthy threshold |
|-----------|-----------------|-------------------|
| **Constraint coverage** | % of code covered by at least one constraint | >= 70% |
| **Constraint health** | Constraints that are active, valid, and producing results | >= 80% |
| **Documentation freshness** | Docs updated within the last 30 days | >= 60% |
| **Context budget** | Total context loaded vs available window | <= 40% |
| **Feedback loop health** | Pre-commit hooks active, lint passing, tests running | >= 80% |
| **Entropy score** | Inverse of stale/orphaned/dead findings from GC | >= 70% |

### Step 3 — Identify top 3 improvement areas

From all dimensions and findings, select the top 3 areas that would most improve overall health:

1. **Prioritize by severity**: Errors > warnings > info.
2. **Prioritize by impact**: Issues affecting many files > issues in one file.
3. **Prioritize by effort**: Quick wins first when severity is equal.
4. **Context budget is critical**: If context usage exceeds 40%, this is ALWAYS a top priority. Large context wastes tokens and degrades agent performance.

For each improvement area:

1. State the problem clearly.
2. Explain why it matters.
3. Provide a specific, actionable recommendation.
4. Estimate effort: trivial (< 5 min), small (< 30 min), medium (< 2 hours), large (> 2 hours).

### Step 4 — Check feedback loop integrity

Verify that the full feedback pipeline is functional:

```
harness lint → type-check → test → build → security scan
```

For each stage:

1. Is it configured? (Does the tooling exist?)
2. Is it automated? (Does it run in CI or pre-commit?)
3. Is it passing? (What is the current status?)
4. Is it enforced? (Can it be bypassed?)

Flag any broken links in the pipeline.

### Step 5 — Review constraint inventory

```bash
harness constraint list
```

For each constraint:

1. Is it producing findings? (A constraint with zero hits may be obsolete or misconfigured.)
2. Is the severity appropriate? (Too many warnings get ignored; too many errors cause friction.)
3. Is the fix message actionable? (Vague fix messages cause doom loops.)
4. Does it have proper test coverage? (Constraints should be tested like code.)

### Step 6 — Compile the health dashboard

Assemble all findings into the output format below.

## Operating Principles

- **Context budget under 40%.** This is the most impactful metric for agent effectiveness. Bloated context means slower, less accurate responses.
- **Prioritize high-severity issues.** Don't let the perfect be the enemy of the good — fix critical issues before optimizing.
- **Track trends, not just snapshots.** A score of 65 that was 50 last week is better than 75 that was 90.
- **Actionable recommendations only.** Every recommendation must have a clear next step. "Improve test coverage" is not actionable. "Add integration tests for the /api/users endpoint" is.
- **Don't audit in a vacuum.** Cross-reference audit findings with recent git history. Recent changes are more likely to have issues.
- **Respect the constitution.** Some audit findings may be intentional trade-offs documented in the constitution.

## Output Format

```
## Health Dashboard

**Overall Score: N/100**
**Trend: [improving | stable | declining]**

### Dimension Scores

| Dimension              | Score | Status | Trend |
|------------------------|-------|--------|-------|
| Constraint coverage    | N/100 | [pass/warn/fail] | [up/stable/down] |
| Constraint health      | N/100 | [pass/warn/fail] | [up/stable/down] |
| Documentation freshness| N/100 | [pass/warn/fail] | [up/stable/down] |
| Context budget         | N%    | [pass/warn/fail] | [up/stable/down] |
| Feedback loop health   | N/100 | [pass/warn/fail] | [up/stable/down] |
| Entropy score          | N/100 | [pass/warn/fail] | [up/stable/down] |

### Top 3 Improvement Areas

1. **[Area name]** (severity: [high/medium/low], effort: [trivial/small/medium/large])
   - Problem: ...
   - Impact: ...
   - Recommendation: ...

2. **[Area name]** (severity: [high/medium/low], effort: [trivial/small/medium/large])
   - Problem: ...
   - Impact: ...
   - Recommendation: ...

3. **[Area name]** (severity: [high/medium/low], effort: [trivial/small/medium/large])
   - Problem: ...
   - Impact: ...
   - Recommendation: ...

### Feedback Pipeline Status

| Stage          | Configured | Automated | Passing | Enforced |
|----------------|------------|-----------|---------|----------|
| harness lint   | [yes/no]   | [yes/no]  | [yes/no]| [yes/no] |
| type-check     | [yes/no]   | [yes/no]  | [yes/no]| [yes/no] |
| test           | [yes/no]   | [yes/no]  | [yes/no]| [yes/no] |
| build          | [yes/no]   | [yes/no]  | [yes/no]| [yes/no] |
| security scan  | [yes/no]   | [yes/no]  | [yes/no]| [yes/no] |

### Constraint Inventory

| Constraint | Severity | Findings | Fix Message Quality |
|------------|----------|----------|-------------------- |
| ...        | ...      | N        | [good/needs-work]   |
```
