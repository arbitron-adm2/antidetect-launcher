---
name: add-feature
description: Add new feature following project rules
mode: agent
tools:
  - codebase
  - editFiles
  - search
  - usages
---

# Add Feature

## Before

1. DECISIONS.md → similar patterns
2. ARCHITECTURE.md → layer placement
3. INVARIANTS.md → constraints

## Rules

- No hardcode → use config
- No global state
- No circular imports
- Correct layer

## After

- [ ] Layer correct
- [ ] No cross-layer deps
- [ ] Config external
- [ ] No TODO
- [ ] DECISIONS.md updated if new pattern
