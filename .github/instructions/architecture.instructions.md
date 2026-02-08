---
name: architecture-rules
applyTo: "**"
---

# Architecture Enforcement

- No cross-layer dependencies.
- No bidirectional dependencies.
- All boundaries must be explicit.
- Any new concept requires a DECISION entry.

## Layers

### Domain

Business logic, pure functions, typed models.

### Infrastructure

Framework adapters, database access, external APIs.

### Presentation

API endpoints, message handlers, CLI commands.

## Rules

- Domain never imports infrastructure or presentation.
- Infrastructure and presentation never import each other.
- All cross-layer communication through explicit interfaces.
- Configuration is injected into all layers.
