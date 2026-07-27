# Sprint 2.5 — alpha.7

## Native response capture foundation

- Added a typed York packet-library loader.
- Native probes can transmit only a `verified` `request` whose purpose is `state_request`.
- The packet record is validated before any socket is opened.
- Added `--validate-only` and `--record-id` probe options.
- Probe reports now contain request provenance, endpoint, timing, lengths and structural response validation.
- State decoding remains disabled until response fields are backed by verified captures.

## Success criterion

The next field test succeeds when a complete verified request record produces an import-ready report with `probe_status: response_validated`.
