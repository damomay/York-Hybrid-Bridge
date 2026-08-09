# Sprint 3.1.19 — Guarded Native Swing Control

Alpha.48 enables normal guarded Swing Vertical ↔ Off control for the qualified
On / Heat / Fan Low operating shape.

## Evidence reused

- The earlier dynamic temperature path physically qualified the canonical
  Heat / Fan Low / Swing Off command shape with state byte `0x02`.
- Alpha.45 and Alpha.46 qualified the Heat / Fan Low / Swing Vertical command
  shape with state byte `0x3A`.
- Both shapes preserve the setpoint with the established whole-degree byte and
  byte-11 half-degree flag.

No new packet formula or Relay capture is introduced.

## Normal-control boundary

- The unit must be On / Heat / Fan Low / Display On.
- The current and requested swing modes must be Off or Vertical and must differ.
- The shared qualified setpoint range is 16–30 °C in exact 0.5 °C increments.
- A fresh authenticated pre-read must match all nine qualified fields.
- The command sends one native write, four UDP datagrams and no automatic retry.
- A delayed post-read must match all nine target fields.
- Horizontal, Both, Fan High, invalid setpoints, state mismatches and direct
  communication failures retain Relay v2 fallback.

## Physical confirmation

Deploy Alpha.48 at Heat / 21 °C / Fan Low / Swing Vertical, then use normal
Home Assistant control once for:

1. Swing Vertical → Off.
2. Swing Off → Vertical.

Physically confirm the louvre stops and resumes vertical movement. Temperature
must remain 21 °C and Fan must remain Low throughout.
