# Climate Bridge roadmap

## Accepted baseline

Climate Bridge 1.0.0 is the accepted single-device York/TCL release. Its
current runtime uses authenticated native LAN state and guarded native command
execution. The Android relay and Relay v2 are historical development tools,
not runtime dependencies.

Sprint 3.2.1 reconciliation completed when
[pull request #5](https://github.com/damomay/York-Hybrid-Bridge/pull/5) merged
to `main` at `0874ae24f8806eb89f08573473867ac4ad5e2177`.

## Project-control sequence

The approved work is deliberately staged. A stage is a review boundary: later
work does not begin until Damien explicitly accepts the preceding stage.

1. **Stage 1 — project control (current):** establish accurate durable
   documentation and governance without runtime changes.
2. **Stage 2 — evidence/test controls:** may begin only after explicit Stage 1
   approval. No Stage 2 templates are part of Stage 1.
3. **Future implementation:** requires a separately approved scope, evidence
   plan, rollback boundary, and pull request.

## Known future directions

- independently configured multiple-device operation;
- broader HVAC adapter support;
- improved diagnostics and deployment experience; and
- release/tag alignment for Climate Bridge 1.0.0.

These are directions, not shipped features or permission to implement them.
The older tablet-removal roadmap in
[`docs/roadmaps/tablet-removal.md`](docs/roadmaps/tablet-removal.md) is a
historical plan whose runtime objective was completed before 1.0.0; its
remaining statements are not the current work order.

Across all future work, reliability, fail-closed behaviour, sanitized evidence,
physical safety, reversible changes, and documentation accuracy remain gates.
