# Architecture

> System architecture overview. Loaded on demand when working on structural changes.

## Dependency Layer Model

This project enforces unidirectional dependency flow:

```
Layer 0: Types       — Pure types, interfaces, enums. No imports from other layers.
Layer 1: Config      — Configuration loading. May import from Types.
Layer 2: Repository  — Data access. May import from Types, Config.
Layer 3: Service     — Business logic. May import from Types, Config, Repository.
Layer 4: Runtime     — Application lifecycle, middleware. May import from layers 0-3.
Layer 5: UI          — Presentation. May import from any lower layer.
```

**Cross-cutting concerns** (auth, logging, telemetry, feature flags) enter **only through Providers** — interfaces defined in the consuming layer, implemented in a lower layer.

## Directory Mapping

[NEEDS CLARIFICATION: Map your project's directory structure to the layer model]

```
src/
├── types/          # Layer 0
├── config/         # Layer 1
├── repositories/   # Layer 2
├── services/       # Layer 3
├── runtime/        # Layer 4
└── ui/             # Layer 5
```

## Key Architectural Decisions

[NEEDS CLARIFICATION: Document your ADRs here or link to `.harness/design-docs/`]

1. **[Decision]**: [Rationale]
2. **[Decision]**: [Rationale]
