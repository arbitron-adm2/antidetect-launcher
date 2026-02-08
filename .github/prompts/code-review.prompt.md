---
name: code-review
description: Review code against INVARIANTS.md
mode: ask
tools:
  - codebase
  - search
---

# Code Review

## Must Check

- [ ] No hardcode (INVARIANTS.md)
- [ ] Config in TOML/ENV only
- [ ] No defaults in code

## Architecture

- [ ] No cross-layer deps
- [ ] No circular imports
- [ ] New concept → DECISIONS.md

## Code

- [ ] No TODO/FIXME
- [ ] Typed exceptions
- [ ] No global state

## Reject if any violated
