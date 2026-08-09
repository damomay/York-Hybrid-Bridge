# Sprint 3.1.14 — Guarded Low/Vertical Temperature Control

Alpha.43 integrates the two Alpha.42-qualified Heat/Fan Low/Swing Vertical
temperature transitions into normal Home Assistant control:

- 25 → 24 °C
- 24 → 25 °C

Each transition uses the exact physically verified 31-byte Relay frame. The
complete nine-field Relay state selects the path before a client is created. A
matching live direct pre-read is then required, followed by one write, zero
automatic retries, and a matching nine-field post-read.

Every other Low/Vertical target or starting temperature remains outside the
qualified boundary and uses Relay v2 fallback. Fan Low and Swing Vertical are
preserved.

The one-shot Alpha.42 qualification tool remains isolated from normal command
routing.
