# Sprint 3.1.44 — Official-SDK Fan-only Qualification

## Evidence

York Write Packet Lab v1 connected to the type-20014 Wi-Fi module on
2026-08-08 and read this live state through the official TCL/Broadlink SDK:

- Power On
- Dry
- 17 °C
- Fan Auto
- Swing Off
- Turbo, Eco and Health Off
- Display On

The lab cloned that state, changed only native SDK `mode` from `2` (Dry) to `7`
(Fan-only), and called `setSplitAirconInfo()`. It generated this frame without
transmitting it:

```text
BB 00 01 03 19 01 00 44 07 0E 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 EC
```

## Qualification boundary

- Only the exact captured source state may select the command.
- The exact SDK output is immutable and lives in a dedicated allowlist.
- The retired Alpha.71 `mode=0x04 / temp=0x08 / fan=0x05` frame remains blocked.
- No parameterised or inferred Fan-only frame may reach the production client.
- Fan-only → Heat and all other Fan-only transitions remain disabled.

## Runtime safety

- One control write only; zero write retries and no fallback.
- Fresh authoritative pre-read must match all nine guarded fields.
- Read-only post-write checks continue for up to 30 seconds.
- Power, mode, temperature, fan, swing, turbo, eco, health and display must all
  match the exact target.
- Any observed unexpected Power Off aborts immediately as a critical failure.

## Qualification status

- Focused official-SDK and containment suite: 45 passed.
- Full regression suite: 818 passed.
- Python compilation and release verification: passed.
- Physical qualification remains intentionally pending the isolated Alpha.73
  test.
