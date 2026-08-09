# Sprint 3.1.24 — Heat Horizontal Axis Qualification

Alpha.53 adds a guarded, one-shot native qualification for the visibly
observable Horizontal-only axis at On / Heat / 21.5 °C / Fan Low:

- Swing Off → Horizontal
- Swing Horizontal → Off

The two exact Relay v2 command frames preserve mode, setpoint and Fan Low.
Horizontal uses the command-side `0x08` axis flag combined with the `0x02`
half-degree flag in byte 11. Off removes only the axis flag.

Each case requires its own confirmation token and an exact nine-field live
pre-read. It performs one write through four UDP sends with zero retries, then
requires an exact nine-field post-read. A mismatched live state stops before
the write. There is no automatic restore.

Heat-mode firmware can park the Vertical vane, so this stage deliberately
tests only Horizontal-only movement from and back to Off. Normal Home Assistant
Horizontal routing remains on Relay v2 until both native directions are
physically qualified.
