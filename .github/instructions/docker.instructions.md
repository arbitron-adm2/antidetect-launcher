---
name: docker-rules
applyTo: "**/Dockerfile"
---

# Docker Rules

## Image Build

- Multi-stage builds only
- Pin base image versions (e.g., `python:3.12-slim`)
- Non-root user execution
- Minimal final image size

## Configuration

- No hardcoded values in image
- All runtime config via ENV
- Config files mounted as volumes
- Secrets via environment or secrets manager

## Entrypoint

- Single responsibility
- No logic in ENTRYPOINT
- Use exec form: `["python", "-m", "..."]`

## Health Checks

- Always define HEALTHCHECK
- Reasonable intervals (30s)
- Quick timeout (10s)

## Security

- No secrets in image layers
- Read-only config mounts
- Drop capabilities where possible

## Resources

- Define resource limits in compose
- Memory limits prevent OOM
- CPU limits for fair scheduling
