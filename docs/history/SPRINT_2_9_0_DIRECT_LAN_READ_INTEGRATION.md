# Sprint 2.9.0 — Direct LAN Read Integration

Climate Bridge 1.0.0-alpha.21 integrates the qualified Broadlink/York LAN
state read as a disabled-by-default shadow observer.

## Runtime boundary

- Relay remains the active Home Assistant state and control transport.
- `direct_read.enabled` defaults to `false`.
- Each scheduled observation authenticates once and sends only
  `BB000104020100BD` once.
- There are zero automatic retries, no discovery packets and no direct control
  encoder.
- A direct-read failure does not mark the relay or York climate entity offline.
- The direct result is compared only across the eight evidence-backed fields:
  power, mode, fan, swing, turbo, eco, health and display.

## Diagnostics

The existing disabled-by-default native diagnostic entities report:

- Native probe status
- Native comparison
- Native response length
- Last native probe

Decoded direct state is also retained at
`<base_topic>/diagnostic/native_state`.

## Qualification evidence

The transport implements the live sequence qualified on 2026-07-28:

`0x65 → 0xE9 → 0x6A → 0xEE`

Authentication accepts the nonzero session ID returned by the device and uses
that exact ID for the single state query.
