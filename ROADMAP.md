# Climate Bridge roadmap

## Accepted baseline

Climate Bridge 1.0.0 is the accepted single-device York/TCL release. Its
current runtime uses authenticated native LAN state and guarded native command
execution. The Android relay and Relay v2 are historical development tools,
not runtime dependencies.

## Project-control sequence

The work is deliberately staged; each stage is a review boundary.

1. **Stage 1 — project control:** completed and merged through pull request #7.
2. **Stage 2 — testing and evidence control:** completed and merged through
   pull request #9 at `8fb4d740b0f1378029095efa7c3d18247ebe7a67`.
3. **Stage 3 — GitHub workflow and release-control hardening:** implemented in
   its dedicated pull request; completion requires review and merge.
4. **Stage 4 or feature development:** not authorized. It requires a separately
   approved scope, evidence plan, rollback boundary, and pull request.

## Known future directions

- independently configured multiple-device operation;
- broader HVAC adapter support;
- improved diagnostics and deployment experience; and
- release/tag alignment for Climate Bridge 1.0.0.

These are directions, not shipped features or permission to implement them.
Release/tag alignment remains separate from Stage 3 and requires explicit
approval. Across future work, reliability, fail-closed behaviour, sanitized
evidence, physical safety, reversible changes, and documentation accuracy
remain gates.
