# Sprint 3.1.23 — Native Dry Horizontal Axis Control

Alpha.52 promotes the two Alpha.51-qualified Dry-mode Horizontal-axis
transitions into normal Home Assistant control:

- Dry / 21 °C / Fan Low / Vertical → Both
- Dry / 21 °C / Fan Low / Both → Vertical

Each transition uses its exact physically qualified Relay v2 frame, requires
an exact nine-field Relay state and matching direct pre-read, performs one
write through four UDP sends with zero retries, and requires a matching
nine-field post-read.

The existing guarded Heat / Fan Low / Off ↔ Vertical path is unchanged. Every
other Horizontal/Both request or starting state safely falls back to Relay v2.
The Alpha.51 qualification tool remains in the source history but is not copied
into the Alpha.52 runtime container.
