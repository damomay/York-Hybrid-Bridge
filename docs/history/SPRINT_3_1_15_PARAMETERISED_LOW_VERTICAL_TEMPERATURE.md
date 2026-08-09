# Sprint 3.1.15 — Parameterised Low/Vertical Temperature

## Outcome

Alpha.44 advances Low/Vertical temperature support from two exact captured
targets to a guarded, qualification-only whole-degree generator.

The generator covers 16 through 31 °C using:

- byte 9 = `31 - target temperature`
- byte 10 = `0x3A`
- York XOR across all 31 bytes = `0x00`

The exact Alpha.42 frames for 24 and 25 °C remain byte-for-byte anchors. The
same setpoint formula was already physically qualified across the full range
for High/Vertical, and Low/Vertical operation has been physically observed at
24, 25 and 26 °C.

## Live boundary

Alpha.44 exposes only two comfortable operator-triggered cases:

- `25-to-26`
- `26-to-25`

Each case requires the exact On / Heat / Fan Low / Swing Vertical /
Display On nine-field state, a matching direct pre-read and its own
confirmation token. It sends one write, performs four UDP sends in total, has
zero automatic retries, and requires a matching nine-field post-read.

Physical confirmation remains mandatory because controller read-back alone
previously produced false positives.

## Normal control boundary

Alpha.44 does not broaden normal Home Assistant routing. The Alpha.43 native
Low/Vertical path remains limited to 25 → 24 °C and 24 → 25 °C. Every other
Low/Vertical target continues through Relay v2 fallback.

After both Alpha.44 live cases are physically confirmed, the next release may
enable the complete whole-degree Low/Vertical range behind the existing live
state guards and Relay fallback.

## Commands

Offline validation opens no socket:

```sh
python /app/york_low_vertical_temperature_range_qualification.py
```

The live cases require their exact case-specific confirmation tokens. Never
run either live case more than once after a confirmed pass.
