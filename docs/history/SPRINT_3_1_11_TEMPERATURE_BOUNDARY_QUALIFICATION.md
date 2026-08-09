# Sprint 3.1.11 — Temperature Boundary Qualification

Alpha.40 extends the Alpha.39 whole-degree setpoint generator across the York
unit's complete confirmed range of 16 to 31 °C.

## Boundary capture evidence

- 16 °C uses setpoint byte `0x0F`
- 17 °C uses setpoint byte `0x0E`
- 30 °C uses setpoint byte `0x01`
- 31 °C uses setpoint byte `0x00`
- All four Relay v2 transactions succeeded and physically read back the
  requested temperature
- The formula remains byte 9 = `31 - setpoint °C`
- Byte 10 remains `0x3D`
- The final York XOR checksum is regenerated after the setpoint byte changes

## Qualification scope

Offline validation builds every whole-degree target from 16 through 31 °C and
checks canonical length, byte encoding, checksum and round-trip validation.
The two live cases exercise both physical endpoints:

- `30-to-31`
- `31-to-16`

Each live case requires an exact nine-field pre-read, sends one write with zero
retries, and requires an exact nine-field post-read. The qualification tool is
not connected to normal MQTT temperature routing. Relay v2 fallback remains
unchanged.
