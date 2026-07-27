# Sprint 2.3 — Controlled Native State Probe

Version: 1.0.0-alpha.3

## Completed

- Centralized and synchronized release metadata.
- Added release/package verification for required Python packages and versions.
- Added an operator-controlled one-shot native York probe utility.
- Native packets may only be transmitted when `direct_device.state_request_hex`
  contains a previously captured request frame.
- Guessed requests and all native commands remain blocked.
- Raw native responses are stored as JSON under `/reports/native-probes` for
  decoder fixture development.

## Production mode

Keep `transport.type: relay`. The one-shot probe is a separate development tool
and does not alter Home Assistant entities or the working relay path.
