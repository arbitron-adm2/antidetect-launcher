# Global Copilot Rules

Production-grade system. All agents obey these rules.

## Absolute Rules

- No hardcoded values
- No placeholders, stubs, temporary code
- No TODO/FIXME comments
- No rewriting without request

## Configuration

- All constants in TOML/ENV
- No defaults in code
- Missing config = startup failure

## Architecture

- Strict separation of concerns
- One purpose per module
- No implicit coupling

## Code Quality

- Clean, minimal, explicit
- No clever tricks

## Output

- No explanations unless requested
- No filler text

## Memory Hierarchy

- **L1**: This file (immutable)
- **L2**: .docs/INVARIANTS.md, .docs/DECISIONS.md, .docs/CONSTRAINTS.md
- **L3**: .github/agents/, .github/prompts/, .github/skills/

## Agents

Use `.github/agents/coder.agent.md` for universal coding tasks.

## System Graph

See [.docs/GRAPH.md](.docs/GRAPH.md) for rule connections.

## Project Info

See [README.md](README.md) for project context.
