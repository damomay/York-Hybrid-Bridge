# Sprint 3.1.33 — Parameterised Running Mode Control

## Purpose

Remove the narrow captured-state restriction from normal native Heat↔Cool
control while preserving the state-authority and canonical-frame boundaries
physically verified through Alpha.61.

## Evidence boundary

The captured Heat→Cool and Cool→Heat transactions establish that a running
mode change sends the complete powered-On target-state frame. Those target
frames are the same exact canonical command shape used by Alpha.60 for guarded
power-on and by the qualified temperature generators.

Alpha.62 does not infer any new field encoding. It builds only source and target
states already accepted by the canonical Alpha.60 shapes:

- Heat or Cool / Fan Low / Swing Off.
- Heat / Fan Low / Swing Vertical.
- Heat / Fan High / Swing Vertical.
- The whole- and half-degree ranges already enforced by those generators.
- The exact historical Cool / 25 °C / Fan High / Swing Vertical anchor.

Cool / Fan High / Swing Vertical is not promoted into a general parameterised
range; only its exact historical 25 °C capture remains accepted.

## Runtime guards

Every parameterised running-mode request requires:

1. An exact powered-On Heat or Cool mode request.
2. A complete authoritative On state containing all nine guarded fields.
3. A real Heat↔Cool change rather than a same-mode request.
4. Disabled Turbo, Eco and Health flags and enabled Display.
5. Current and target shapes accepted by the canonical builders.
6. A fresh direct pre-read matching all nine authoritative fields.
7. One write with no automatic retry.
8. A fresh direct post-read matching the target mode and all eight retained
   fields.

Failure before the write is a safe-stop. Unsupported or changed state creates
no write client. The runtime does not use Relay fallback.

## Preserved boundaries

- Historical captured command fixtures and fingerprints are unchanged.
- The immutable capture-replay allowlist is unchanged.
- Alpha.60 parameterised power-on generation is unchanged.
- Alpha.61 parameterised power-off generation is unchanged.
- Temperature, fan and swing managers are unchanged.
- Direct state remains authoritative for startup, polling, commands and
  recovery.
- Normal success remains four UDP sends with zero retries.

## Acceptance baseline

The first physical acceptance test starts after Alpha.61 with the unit Off and
retaining `Heat / 22.5 °C / Fan Low / Swing Off`. Alpha.60's inherited guarded
Power On first restores that exact state. Home Assistant Cool must then change
only the running mode, leaving 22.5 °C, Fan Low and Swing Off unchanged. A
following Heat command verifies the reverse direction.
