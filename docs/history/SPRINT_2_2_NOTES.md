# Sprint 2.2 — York Adapter Architecture and Capture Pipeline

## Completed

- Split native York support into connection, protocol session, encoder, decoder,
  state model and adapter-specific errors.
- Made the direct device UDP port configurable.
- Added a safe captured-frame inspection path for known `0xBB` frames.
- Added operator-friendly transport names in the startup banner.
- Kept packet transmission and state mapping disabled until validated captures
  establish the exact request, sequence, authentication and checksum fields.

## Operational mode

Keep `transport.type: relay`. Sprint 2.2 is an engineering build and does not
replace the tablet yet.

## Next evidence required

The next implementation step is to import full request/response pairs from the
York Protocol Explorer or packet logs, including exact bytes, direction and the
HVAC state at capture time. These become decoder fixtures before direct polling
is enabled.
