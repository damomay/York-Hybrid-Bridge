# Phase 11 — Post-merge verification

Status: PASS.

## Canonical baseline

Pull request #2 merged into `main` as:

`137b509b5dadd6459b43f70c5a8295beba477d5c`

The merged tree has no content difference from the approved reconciliation
head `dda185e007477fde89c257e53b832591a952a8e6`.

## Fresh code gate

A fresh single-branch checkout of canonical `main` passed:

- Python 3.12 dependency installation from `requirements.txt`;
- forced Python compilation;
- release identity verification for Climate Bridge `1.0.0-alpha.20`;
- example configuration validation with relay transport;
- 126/126 complete tests;
- 14/14 decoder fixtures;
- the 199-file privacy and generated-material scan;
- `git diff --check`; and
- clean final Git status.

## Clean deployment and live regression

A clean tracked archive of canonical `main` was deployed as Synology project
`climate_bridge_1a20p11` with the preserved working `config.yml`.

The image built and started, connected to MQTT, published 64 Home Assistant
discovery entities and reached `Bridge READY`. York AC2 and Home Assistant
agreed for:

1. Cool power-on at 22 °C.
2. Target-temperature change to 25 °C.
3. Fan change from Low to High.
4. Swing change from Off to Vertical.
5. Power-off.

The physical York unit responded to every command.

## Restart recovery

The Phase 11 project completed a clean signal-15 shutdown, MQTT reconnection,
discovery republish and return to `Bridge READY`. Home Assistant recovered the
synchronised Off state, and the physical unit remained off.

The stopped Phase 7 project and the backed-up working configuration remain
available as the deployment rollback.

Gate 11: PASS.
