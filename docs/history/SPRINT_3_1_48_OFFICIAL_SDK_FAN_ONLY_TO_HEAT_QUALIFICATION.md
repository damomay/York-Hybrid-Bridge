# Sprint 3.1.48 — Official-SDK Fan-only to Heat Qualification

## Evidence

York Write Packet Lab v1 Capture 3 read the live unit as:

| Field | Value |
|---|---:|
| Power | On |
| Native mode | `7` (Fan-only) |
| Protocol temperature | `8` (non-applicable in Fan-only) |
| Measured `indoorTemp` | 14 °C |
| Fan | Auto |
| Left/right swing | Off |
| Up/down swing | Off |
| Display | On |

The lab cloned that live state, changed only native SDK mode to Heat, called
`setSplitAirconInfo()`, and generated this frame without transmitting it:

```text
BB 00 01 03 19 01 00 44 01 08 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 EC
```

In Fan-only, `temp=8` is a non-applicable placeholder. After the mode changes
to Heat, the same field becomes a real 23 °C setpoint.

## Alpha.77 boundary

- Require Power On / Fan-only / Fan Auto / both swing axes Off.
- Require Turbo, Eco and Health Off and Display On.
- Ignore target temperature only in the Fan-only source guard.
- Permit only the byte-exact official-SDK Heat frame above.
- Verify Heat / 23 °C / Fan Auto / Swing Off and all applicable feature fields.
- Send one control write with zero automatic retries.
- Poll read-only for up to 30 seconds after the write.
- Abort critically on any unexpected Power Off state.
- Keep Fan-only → Cool, Dry and Auto disabled.
- Keep the retired Alpha.71 Fan-only frame blocked.

## Qualification status

The packet was generated offline and was not transmitted by the lab. Physical
qualification therefore remains pending until the guarded Alpha.77 test is
performed against the unit.
