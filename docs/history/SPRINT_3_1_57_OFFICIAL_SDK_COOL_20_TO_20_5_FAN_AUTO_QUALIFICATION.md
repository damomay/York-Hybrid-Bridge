# Sprint 3.1.57 — Official-SDK Cool 20 → 20.5 °C Fan Auto Qualification

Capture 10 was generated offline by York Write Packet Lab v1 from an
authoritative Cool 20 °C / Fan Auto / Swing Off read. The lab explicitly
reported that no packet was transmitted.

Alpha.86 authorises only this exact edge:

- Source: Power On / Cool 20.0 °C / Fan Auto / Swing Off
- Target: Power On / Cool 20.5 °C / Fan Auto / Swing Off
- Frame: `BB 00 01 03 19 01 00 44 03 0B 00 02 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 EF`

The normal command path requires an exact nine-field cached source and an
exact fresh authenticated pre-read, performs one write with zero retries, and
uses delayed read-only verification. Unexpected Power Off is critical. The
reverse 20.5 → 20.0 °C edge and every other Cool/Fan Auto target remain
blocked until separately captured.
