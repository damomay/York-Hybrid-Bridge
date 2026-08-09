# Sprint 3.1.58 — Official-SDK Cool 20.5 → 20 °C Fan Auto Qualification

Capture 11 was generated offline by York Write Packet Lab v1 from an
authoritative Cool 20.5 °C / Fan Auto / Swing Off read. The lab explicitly
reported that no packet was transmitted.

Alpha.87 authorises only this exact edge:

- Source: Power On / Cool 20.5 °C / Fan Auto / Swing Off
- Target: Power On / Cool 20.0 °C / Fan Auto / Swing Off
- Frame: `BB 00 01 03 19 01 00 44 03 0B 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 ED`

The normal command path requires an exact nine-field cached source and an
exact fresh authenticated pre-read, performs one write with zero retries, and
uses delayed read-only verification. Unexpected Power Off is critical. Every
other uncaptured Cool/Fan Auto target from the 20.5 °C source remains blocked.
