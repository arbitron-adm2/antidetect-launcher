---
name: config-rules
applyTo: ".config/**/*"
---

# Config Rules

- Declarative only
- No logic
- No defaults
- All via injection

## Files

- app.toml — constants
- runtime.toml — runtime values
- logging.toml — logging
- deploy.toml — deployment

## ENV Override

Format: `APP_SECTION_KEY`
Missing required = startup failure
