# Sprint 3.1.8 — Running Mode Change Qualification

Alpha.37 adds two qualification-only cases for changing mode while the York
unit remains powered on:

- `heat-to-cool`: On/Heat/25 °C/High/Vertical to
  On/Cool/25 °C/High/Vertical.
- `cool-to-heat`: On/Cool/25 °C/High/Vertical to
  On/Heat/25 °C/High/Vertical.

Relay v2 transactions #4 and #5 on 2026-07-30 physically verified both
transitions. The captured frames are byte-for-byte identical to the already
qualified Power On + Cool and Power On + Heat target-state frames. Alpha.37
therefore adds no generated or inferred packet.

Each case requires an exact nine-field live precondition, an explicit
case-specific confirmation token, one captured direct write, zero retries, and
one direct post-read. A precondition mismatch stops before the write.

The two cases are not connected to normal MQTT control. Alpha.36's guarded
power and temperature paths and automatic Relay v2 fallback remain unchanged.
