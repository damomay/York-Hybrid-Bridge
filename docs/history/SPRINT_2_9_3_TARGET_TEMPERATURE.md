# Sprint 2.9.3 — Target Temperature Qualification

Alpha.24 completes the remaining read-only target-temperature field needed
before a controlled direct-write test can be considered.

Evidence basis:

- York status byte 8 uses its high nibble for fan and low nibble for whole
  target temperature above 16 °C.
- Status byte 9 bit `0x02` adds 0.5 °C.
- The official 24→25→24 °C capture independently confirmed byte 8 low-nibble
  values `0x08` and `0x09`.
- Earlier marked Protocol Explorer evidence confirmed the half-degree bit.

Runtime changes:

- direct state now includes `temperature`;
- relay/direct comparison increases from eight to nine fields when both sides
  provide target temperature;
- the retained native diagnostic and log line show both temperature values;
- startup validation rejects `direct_read:` accidentally indented beneath
  `logging:` and reports whether the observer is enabled.

Safety boundaries are unchanged:

- Relay v2 remains the only command path.
- Direct LAN remains read-only.
- The only direct York request is `BB000104020100BD`.
- Each observation uses two UDP sends and zero automatic retries.
- No direct-write encoder or live write tool is included.

The live exit check is one relay-controlled 24→25→24 °C sequence. Each stable
state must produce a direct observation with `match (9/9)`.
