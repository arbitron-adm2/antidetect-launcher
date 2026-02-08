---
name: python-rules
applyTo: "**/*.py"
---

# Python Rules

## Runtime

- Python 3.12+
- Async-first for I/O
- No blocking in async paths

## Structure

- One responsibility per file
- No global mutable state
- No circular imports

## Config

- No constants in code
- Config injected only

## Architecture

- Domain = framework-agnostic
- Infrastructure = isolated
- Explicit interfaces

## Errors

- Typed exceptions only
- No blanket except
- Fail fast on invalid states

## Forbidden

- Hardcoded values
- Cross-layer imports
- Temporary fixes
