---
name: debug
description: Debug isolated issue
mode: agent
tools:
  - codebase
  - editFiles
  - runInTerminal
  - search
---

# Debug Isolated

## Process

1. Isolate failing logic
2. Don't modify production paths
3. Create testable reproduction
4. Propose minimal fix
5. Document in DECISIONS.md

## Rules

- Workarounds isolated and testable
- Core logic stays clean
- Fix root cause, not symptoms
