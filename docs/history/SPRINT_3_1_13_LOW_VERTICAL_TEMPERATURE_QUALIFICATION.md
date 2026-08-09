# Sprint 3.1.13 — Low/Vertical Temperature Qualification

Alpha.42 adds a bounded, operator-run direct-write qualification for the
occupied-room state:

- Power On
- Heat mode
- Fan Low
- Swing Vertical
- Display On
- Turbo, Eco and Health Off

Relay v2 transactions #1 and #2 on 2026-07-30 physically changed the unit
25 → 24 °C and 24 → 25 °C while preserving Fan Low and Swing Vertical.

The two captured 31-byte frames use setpoint byte 9 as `31 - temperature` and
the distinct Low/Vertical state byte `0x3A`. Alpha.42 does not extend this
observation beyond the two captured targets.

The operator tool exposes exactly two live cases:

- `25-to-24`
- `24-to-25`

Each case requires the exact nine-field direct precondition, an exact
case-specific confirmation token, one write, zero retries, a nine-field
post-read, and physical confirmation by the operator. No automatic restore is
performed.

Normal Home Assistant temperature routing is unchanged. Low/Vertical commands
continue to use Relay v2 until both one-shot cases are physically qualified in
Alpha.42 and a later release explicitly integrates them.
