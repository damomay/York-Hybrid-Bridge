# Sprint 3.1.60 — Official-SDK Cool 22 → 20 °C Fan Auto Qualification

Capture 12 was generated offline by York Write Packet Lab v1 from an
authoritative Cool 22 °C / Fan Auto / Swing Off read. The lab explicitly
reported that no packet was transmitted.

Alpha.89 authorises only this exact additional edge:

- Source: Power On / Cool 22.0 °C / Fan Auto / Swing Off
- Target: Power On / Cool 20.0 °C / Fan Auto / Swing Off
- Frame: `BB 00 01 03 19 01 00 44 03 0B 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 ED`

The target frame is byte-identical to Capture 11's qualified 20.5 → 20.0 °C
command. Alpha.89 therefore distinguishes the edge with exact cached-state and
fresh authenticated pre-read source guards. Only a verified 22.0 °C source may
use this route.

The normal command path performs one write with zero retries and uses delayed
read-only verification. Unexpected Power Off is critical. Every other
uncaptured Cool/Fan Auto target from the 22.0 °C source remains blocked.
