# Climate Bridge roadmap

## Accepted baseline

Climate Bridge 1.0.0 is the accepted single-device York/TCL release. Its
runtime uses authenticated native LAN state and guarded native command execution.
The Android relay and Relay v2 are historical development tools, not runtime
dependencies.

## Project-control sequence

Each stage is a separate review and approval boundary.

1. **Stage 1 — project control:** completed through pull request #7.
2. **Stage 2 — testing and evidence control:** completed through pull request
   #9 at `8fb4d740b0f1378029095efa7c3d18247ebe7a67`.
3. **Stage 3 — GitHub workflow and release-control hardening:** the source
   revision containing this roadmap also contains the Stage 3 controls. Stage 3
   is accepted only when that revision is reachable from current `origin/main`.
4. **Stage 4 or feature development:** not authorized. It requires a separately
   approved scope, evidence plan, rollback boundary, and pull request.

When the Stage 3 revision is not on `origin/main`, the next permitted action is
review—not an assumed merge. When it is on `origin/main`, the next permitted
action is a separately approved later-stage or release-candidate planning
decision. Neither state authorizes tag/release alignment.

## Known future directions

- independently configured multiple-device operation;
- broader HVAC adapter support;
- improved diagnostics and deployment experience; and
- release/tag alignment for Climate Bridge 1.0.0.

These are directions, not shipped features or permission to implement them.
Reliability, fail-closed behavior, sanitized evidence, physical safety,
reversible changes, and documentation accuracy remain gates.
