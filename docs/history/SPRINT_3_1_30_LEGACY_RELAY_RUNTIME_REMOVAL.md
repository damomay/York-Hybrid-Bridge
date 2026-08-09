# Sprint 3.1.30 — Legacy Relay Runtime Removal

## Goal

Remove the dormant Android Relay HTTP runtime after Alpha.58 physically proved
authoritative polling, qualified native commands and fail-closed rejection with
the tablet fully powered off.

## Runtime boundary

- Native LAN is the production transport.
- `relay` and `tablet_relay` remain accepted only as migration aliases.
- Relay URLs, HTTP timeouts, command retries and `fallback_to_relay` are not
  loaded into the runtime configuration.
- The Relay HTTP transport, extraction logger, manager alias and extraction
  report executable are absent from the production package. The one-shot York
  capture probe remains as a direct-LAN-only qualification tool.
- Unsupported and guarded-safe-stop commands are rejected after a fresh direct
  read; the last confirmed state is republished by the MQTT handler.

## Preserved evidence and behaviour

Historical Relay captures, qualification JSON and Sprint notes remain protocol
provenance. York packet fixtures, command encoders, guarded managers, direct
state authority, four-send/zero-retry writes, availability, failure counters,
restart recovery and MQTT recovery are unchanged from Alpha.58.
