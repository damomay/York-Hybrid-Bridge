# Sprint 2.8.2 Phase 1 — TX Instrumentation

Adds transport-agnostic transmission auditing around the York Replay Engine.

## Behaviour

Immediately before the UDP socket send, the engine records the exact immutable
payload, destination, length, SHA-256 hash, verification status and correlation
ID. JSON and Markdown records are written to `/reports/transmissions`.

The logger does not generate, modify, send or retry packets. The existing
verified-request safety gate remains unchanged.
