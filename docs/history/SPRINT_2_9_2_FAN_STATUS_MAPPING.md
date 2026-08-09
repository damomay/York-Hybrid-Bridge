# Sprint 2.9.2 — Fan Status Mapping

Live read-only observations on 2026-07-29 established the complete York fan
status mapping:

| Status byte | High nibble | Fan |
|---|---:|---|
| `0x08` | `0` | Auto |
| `0x18` | `1` | Low |
| `0x28` | `2` | Medium |
| `0x38` | `3` | High |

Alpha.22 had the first two labels reversed. Alpha.23 corrects only those
decoder entries and adds regression coverage for all four values.

Safety boundaries are unchanged:

- Relay v2 remains the active state and control transport.
- Direct LAN remains a read-only shadow observer.
- The only York request is `BB000104020100BD`.
- Each observation uses two UDP sends and zero automatic retries.
- No direct control encoder is enabled.
