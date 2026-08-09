# Sprint 3.1.10 — Temperature Encoding Qualification

Alpha.39 qualifies the whole-degree temperature encoding observed in three
successful Relay v2 transactions from an exact On / Heat / Fan High / Swing
Vertical state.

## Captured relationship

- 24 °C uses setpoint byte `0x07`
- 25 °C uses setpoint byte `0x06`
- 26 °C uses setpoint byte `0x05`
- Formula: byte 9 = `31 - setpoint °C`
- Byte 10 remains `0x3D`
- The final York XOR checksum is regenerated after the setpoint byte changes

## Safety boundary

Alpha.39 accepts only the captured 24, 25 and 26 °C targets. Each live case
requires an exact nine-field pre-read, sends one write with zero retries, and
requires an exact nine-field post-read. The qualification tool is not connected
to normal MQTT temperature routing. Relay v2 fallback remains unchanged.
