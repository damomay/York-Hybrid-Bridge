# Sprint 3.1.18 — Guarded Native Fan Control

Alpha.47 enables normal native Fan Low ↔ High changes for the qualified
Heat/Swing Vertical operating shape.

## Evidence

- Alpha.41 qualified Heat/Fan High/Swing Vertical with state byte `0x3D`.
- Alpha.45 qualified Heat/Fan Low/Swing Vertical with state byte `0x3A`.
- Alpha.46 qualified both shapes across 16–31 °C in 0.5 °C increments.
- Physical temperature tests repeatedly preserved the selected fan and
  Vertical swing in both shapes.

The fan command selects one of those already qualified complete target-state
frames at the current setpoint. It does not introduce a new packet formula.

## Runtime boundary

- The unit must be On / Heat / Swing Vertical / Display On.
- The current and requested fan modes must form Low → High or High → Low.
- The current setpoint must be 16–31 °C in exact 0.5 °C increments.
- Turbo, Eco and Health must be off.
- The Relay state and fresh direct pre-read must match all nine qualified
  fields before the write is constructed.
- Each eligible command sends one write within four UDP exchanges and has
  zero automatic retries.
- A fresh nine-field post-read must confirm the target fan while preserving
  temperature and swing.
- Auto, Medium, invalid states and direct failures retain Relay v2 fallback.

## Physical confirmation

Deploy Alpha.47 at Heat / 25 °C / Fan Low / Swing Vertical, then use normal
Home Assistant fan control for one Low → High → Low sequence. Confirm the
physical fan changes in both directions while the setpoint remains 25 °C and
Swing remains Vertical.
