# Sprint 3.1.16 — Parameterised Low/Vertical Temperature Control

## Purpose

Alpha.45 promotes the physically qualified Heat/Fan Low/Swing Vertical
whole-degree generator into normal guarded Home Assistant temperature control.
Targets from 16 through 31 °C can now use the native York LAN path.

## Evidence carried forward

- Alpha.42 matched the exact Relay v2 frames at 24 and 25 °C.
- Alpha.43 physically proved normal native 25 → 24 → 25 °C control.
- Alpha.44 validated all sixteen 16–31 °C frames offline.
- Alpha.44 physically proved the parameterised 25 → 26 → 25 °C sequence.
- Fan remained Low and Swing remained Vertical throughout the live tests.

## Guarded normal path

A native Low/Vertical temperature write is eligible only when:

- the command changes temperature only;
- the synchronized state is On / Heat / Fan Low / Swing Vertical;
- Turbo, Eco and Health are off and Display is on;
- the target is a whole degree from 16 through 31 °C;
- a fresh authenticated direct pre-read matches all nine qualified fields.

Each eligible command performs one write, four UDP sends, zero automatic
retries and a fresh nine-field post-read verification.

If command validation, authentication, the pre-read or post-read fails, normal
control retains Relay v2 fallback according to configuration. Other operating
shapes remain on their previously qualified native paths or Relay v2.

## Normal-operation verification

Deploy with the existing configuration unchanged. From the comfortable
Heat / 25 °C / Fan Low / Swing Vertical state, use Home Assistant once to
change 25 → 26 °C and once to return 26 → 25 °C. Confirm the physical unit,
Fan Low and Swing Vertical after each command.
