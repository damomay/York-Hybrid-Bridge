# Sprint 2.5.4 — Deployment Hardening

Climate Bridge 1.0.0-alpha.11 fixes the missing host bind-mount directory used by Synology Container Manager.

## Fixes

- Adds the root-level `qualification-reports/` directory referenced by `docker-compose.yml`.
- Retains `protocols/york/qualification-reports/` for protocol-reference reports.
- Replaces shell brace expansion in the Docker startup command with explicit portable paths.
- Creates `/reports` and all runtime protocol directories when the container starts.
- Extends release verification to reject packages missing the bind-mount source.
