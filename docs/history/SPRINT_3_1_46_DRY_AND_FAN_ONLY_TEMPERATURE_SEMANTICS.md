# Sprint 3.1.46 — Dry and Fan-only Temperature Semantics

## Evidence

The physical remote exposes no temperature selection in either Dry or
Fan-only. Fresh York Write Packet Lab reads confirmed:

| State | Native mode | Native fan | Protocol temp | SDK indoorTemp |
|---|---:|---:|---:|---:|
| Dry / Fan Auto | `2` | `0` | `15` | 16 °C |
| Fan-only / Fan High | `7` | `5` | `8` | 15 °C |

The protocol temperature fields are non-applicable status/placeholders, not
setpoints. The independent `indoorTemp` field remains the room measurement.

## Alpha.75 boundary

- Omit target temperature from authoritative Dry and Fan-only state.
- Publish `indoorTemp` as current temperature in both modes.
- Reject target-temperature writes unless the live mode is Heat or Cool.
- Qualify only Dry / Fan Auto / Swing Off → Fan-only using the exact offline
  official-SDK frame already proven live in Alpha.73.
- Verify the eight applicable power, mode, fan, swing and feature fields before
  and after the write; temperature is excluded on both sides.
- Send the control frame once, with zero automatic retries.
- Use read-only delayed verification and stop critically on unexpected Power
  Off.
- Keep Fan-only exits and the retired Alpha.71 packet disabled.

## Indoor-temperature correction

The new Fan High capture maps raw byte `0x57` to SDK `indoorTemp=15`. Together
with the earlier `0x5A` → 16 °C and `0x5C` → 17 °C captures, this establishes
the SDK-observed whole-degree conversion used by Alpha.75.
