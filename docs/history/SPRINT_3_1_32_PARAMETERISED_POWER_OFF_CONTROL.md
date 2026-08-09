# Sprint 3.1.32 — Parameterised Power-Off Control

## Purpose

Remove the remaining narrow captured-state restriction from normal native
Power Off while preserving the safety boundary physically verified through
Alpha.60.

## Evidence boundary

The captured 25 °C / Fan High / Swing Vertical Power On and Power Off pairs in
both Heat and Cool establish that the complete York target-state command uses
byte 7 bit `0x04` as the power control. For an otherwise identical target
state, Power On uses byte 7 value `0x44`; Power Off uses `0x40`. The final byte
is the XOR checksum and is recalculated after clearing the power bit.

Alpha.61 does not infer any mode, temperature, fan or swing encoding. It starts
only from a canonical frame already accepted by Alpha.60's parameterised
power-on allowlist. This limits Power Off to the same qualified shapes:

- Heat or Cool / Fan Low / Swing Off.
- Heat / Fan Low / Swing Vertical.
- Heat / Fan High / Swing Vertical.
- The whole- and half-degree temperature ranges already enforced by the
  corresponding canonical generators.

Cool / Fan High / Swing Vertical remains limited to the exact historical
captured case and is not promoted into the parameterised set.

## Runtime guards

Every parameterised Power-Off request requires:

1. An exact `power: false` request.
2. A complete authoritative On state containing all nine guarded fields.
3. Disabled Turbo, Eco and Health flags and enabled Display.
4. A target shape accepted by the Alpha.60 canonical builders.
5. A fresh direct pre-read matching all nine authoritative fields.
6. One write with no automatic retry.
7. A fresh direct post-read matching the expected Off state across all nine
   fields.

Failure before the write is a safe-stop. Unsupported or changed state creates
no write client. The runtime does not use Relay fallback.

## Preserved boundaries

- Historical captured command fixtures and fingerprints are unchanged.
- The immutable capture-replay allowlist is unchanged.
- Alpha.60 parameterised power-on generation and validation are unchanged.
- Temperature, mode, fan and swing command managers are unchanged.
- Direct state remains authoritative for startup, polling, commands and
  recovery.
- Normal success remains four UDP sends with zero retries.

## Acceptance baseline

The first physical acceptance test starts from the Alpha.60-verified live state
`Heat / 22.5 °C / Fan Low / Swing Off`. Home Assistant Power Off must turn the
physical unit off while the direct state retains Heat, 22.5 °C, Fan Low and
Swing Off. A following Home Assistant Heat command can then confirm Alpha.60's
parameterised Power On still restores that retained half-degree state.
