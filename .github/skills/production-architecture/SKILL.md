---
name: production-architecture
description: Enforces clean 3-layer architecture. Use when designing systems, adding features, or reviewing code structure.
---

# Production Architecture

Three-layer model with strict separation.

## Layers

```
Domain (pure logic) ← no external imports
    ↓
Infrastructure (I/O, APIs, DB)
    ↓
Presentation (HTTP, CLI, handlers)
```

## Rules

- No cross-layer imports
- No circular dependencies
- Config via injection
- One responsibility per module

## Checklist

- [ ] Correct layer identified
- [ ] No hardcoded values
- [ ] Interfaces defined
- [ ] Config external

## Resources

- [templates/clean_module.py](templates/clean_module.py)
- [checklists/architecture_checklist.md](checklists/architecture_checklist.md)
