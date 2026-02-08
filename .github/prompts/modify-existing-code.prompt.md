---
name: modify-code
description: Modify existing code with minimal changes
mode: agent
tools:
  - codebase
  - editFiles
  - search
---

# Modify Existing Code

## Rules

- Modify only requested files
- No refactoring
- No new concepts
- Minimal change only

## Check

- ARCHITECTURE.md
- INVARIANTS.md

## Output

Changed code only. No explanation.
