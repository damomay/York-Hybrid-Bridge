# Sprint 3.1.17 — Half-Degree Temperature Control

Alpha.46 enables the York protocol's already established 0.5 °C setpoint
encoding through the guarded native Heat temperature paths.

## Evidence

- Relay v2 captures previously proved byte 11 is `0x02` for half-degree
  targets and `0x00` for whole-degree targets.
- The original dynamic encoder and decoder already reproduced and decoded
  half-degree captures exactly, including 23.5 °C.
- Home Assistant already advertises `temp_step: 0.5`.
- Alpha.41 qualified the Heat/High/Vertical state byte `0x3D`.
- Alpha.45 qualified the Heat/Low/Vertical state byte `0x3A`.

Alpha.46 combines those established facts without changing either operating
state byte. Byte 9 remains `31 - whole temperature`; byte 11 carries the
half-degree flag; and the York XOR checksum is recalculated.

## Runtime boundary

- Valid targets are 16.0 through 31.0 °C in 0.5 °C increments.
- Quarter-degree, non-numeric and out-of-range targets stop before client
  creation or socket use.
- The Relay state and fresh direct pre-read must match all nine qualified
  fields.
- Each eligible command sends one write within four UDP exchanges and has
  zero automatic retries.
- A fresh nine-field post-read must match the requested state.
- Relay v2 remains fallback for an ineligible state or direct-path failure.

## Physical confirmation

Deploy Alpha.46 at Heat / 25 °C / Fan Low / Swing Vertical, then use normal
Home Assistant control for one 25 → 25.5 → 25 °C sequence. Confirm the physical
setpoint and that Fan Low and Swing Vertical remain unchanged.
