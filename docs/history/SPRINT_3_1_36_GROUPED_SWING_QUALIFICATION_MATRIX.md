# Sprint 3.1.36 — Grouped Swing Qualification Matrix

Alpha.65 qualifies one ordered Heat / 22.5 °C / Fan Low swing sequence while
retaining an independent fail-closed transaction for every Home Assistant
command.

## Evidence boundary

- Off and Vertical target shapes reuse the parameterised commands already
  qualified in Alpha.48.
- Both reuses the independently verified Vertical byte `0x3A` and captured
  Horizontal command flag `0x08` from Alpha.50.
- Horizontal reuses the captured Horizontal-only target shape from Alpha.53.
- The previously proven temperature delta changes only the setpoint byte from
  the 21.5 °C anchors to 22.5 °C; the half-degree flag remains `0x02`.
- The case-specific Both and Horizontal frames remain outside the immutable
  captured replay allowlist until physical acceptance is complete.

## Runtime boundary

- Exact state: On / Heat / 22.5 °C / Fan Low / all features off / Display On.
- Exact ordered edges: Off → Vertical → Both → Horizontal → Off.
- A fresh authenticated nine-field pre-read must match before every write.
- Each successful command uses four UDP sends and zero retries.
- A delayed nine-field post-read must match all target fields.
- Skipped edges and every nearby mode, temperature, fan, power or feature
  shape remain a zero-write safe-stop.
- Alpha.64's exact Heat / 22.5 °C / Low↔High / Swing Off fan path remains
  available for the final two steps.

## Continuous physical acceptance

Start at On / Heat / 22.5 °C / Fan Low / Swing Off:

1. Off → Vertical: vertical moves; horizontal remains stationary.
2. Vertical → Both: both axes move.
3. Both → Horizontal: vertical stops; horizontal continues moving.
4. Horizontal → Off: both axes stop.
5. Fan Low → High: fan increases; both axes remain stationary.
6. Fan High → Low: fan decreases; both axes remain stationary.

Allow at least one direct poll after each command. Stop immediately on any
physical mismatch, unexpected axis movement, unavailable entity, verification
mismatch, safety stop, error, retry or no response. Preserve one continuous
container log through the final completed step.
