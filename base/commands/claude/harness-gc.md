---
description: "Run harness gc to detect and fix codebase entropy."
arguments: []
---

# /harness-gc

Detect and reduce codebase entropy: stale docs, orphaned files, constraint drift, dead code.

## Pre-checks

1. Verify `.harness/` directory exists in the project root.
   - If missing: STOP. Tell the user to run `harness init` first.
2. Verify `harness` CLI is available on PATH.
   - If missing: STOP. Tell the user to install harness-kit.
3. Load `.harness/memory/constitution.md` to understand project principles.

## Execution

### Step 1 — Generate the entropy report

```bash
harness gc --report
```

Capture the full output. This report categorizes entropy into sections.

### Step 2 — Categorize findings

Sort every finding into one of these categories:

| Category | Examples | Risk |
|----------|----------|------|
| **Stale documentation** | Outdated ARCHITECTURE.md, wrong API references, dead links | Medium |
| **Orphaned files** | Unreferenced modules, unused test fixtures, leftover configs | Low |
| **Constraint drift** | Constraints that no longer match code patterns, rules with zero hits | High |
| **Dead code** | Unreachable functions, unused imports, commented-out blocks | Low |
| **Pattern drift** | Code that worked around a now-removed limitation | Medium |

### Step 3 — Apply fixes by category

#### Stale Documentation

1. Read the doc and the code it references side by side.
2. Update the doc to match current code.
3. MUST: Preserve the document's intent and structure. Update content, don't delete the file.
4. MUST: Update dates and version references.
5. NEVER: Delete a documentation file. Update it or flag it for the user.

#### Orphaned Files

1. Verify the file is truly orphaned:
   - Search for imports, references, and dynamic usage (string-based imports, config references).
   - Check git history — was this recently added? It might be in-progress work.
2. If confirmed orphaned and NOT recently added (>30 days old):
   - Delete the file.
   - Remove any references to it (imports, config entries).
3. If uncertain: Flag for user review instead of deleting.
4. NEVER: Delete test files without verifying the tested code is also gone.

#### Constraint Drift

1. For each drifted constraint:
   - Check if the constraint's pattern still matches the codebase structure.
   - Check if the constraint's severity is still appropriate.
   - Update the constraint YAML to match current reality.
2. MUST: Preserve the constraint's intent. Adjust the implementation, not the goal.
3. NEVER: Weaken a constraint just because code doesn't comply. Fix the code or flag for user.

#### Dead Code

1. Verify the code is truly dead:
   - Check for dynamic dispatch, reflection, or plugin systems that might use it.
   - Check for public API exports — dead internally doesn't mean dead externally.
2. If confirmed dead: Remove it cleanly.
3. MUST: Remove the entire unit (function, class, module) — don't leave stubs.
4. NEVER: Delete code that is part of a public API without user confirmation.

#### Pattern Drift

1. Identify the outdated pattern and the current preferred pattern.
2. If the fix is mechanical and safe: Apply it.
3. If the fix requires design decisions: Flag for user review.

### Step 4 — Generate after-report

```bash
harness gc --report
```

Compare the before and after reports to quantify improvement.

## Operating Principles

- **Delete only truly dead code.** When in doubt, flag it — don't delete it. In-progress work looks like dead code.
- **Update docs, don't delete them.** A stale doc is better than no doc. Fix the content.
- **Preserve constraint intent.** Constraints encode architectural decisions. Adjust implementation, not goals.
- **Verify before removing.** Always search for dynamic references, config-based usage, and recent git activity before declaring something orphaned.
- **Small, safe changes.** Each GC fix should be independently correct. Don't batch unrelated changes into one edit.
- **Respect the constitution.** Check `.harness/memory/constitution.md` — some "dead" code may be intentionally preserved.

## Output Format

When complete, provide an entropy report:

```
## Entropy Report

### Before
| Category            | Count |
|---------------------|-------|
| Stale documentation | N     |
| Orphaned files      | N     |
| Constraint drift    | N     |
| Dead code           | N     |
| Pattern drift       | N     |
| **Total**           | **N** |

### After
| Category            | Count |
|---------------------|-------|
| Stale documentation | N     |
| Orphaned files      | N     |
| Constraint drift    | N     |
| Dead code           | N     |
| Pattern drift       | N     |
| **Total**           | **N** |

### Changes Applied
- [category] `path/to/file` — description of change

### Flagged for Review
- [category] `path/to/file` — reason this needs human decision
```
