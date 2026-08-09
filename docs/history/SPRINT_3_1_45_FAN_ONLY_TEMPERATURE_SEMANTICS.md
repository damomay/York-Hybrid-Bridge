# Sprint 3.1.45 — Fan-only Temperature Semantics

## Evidence

Write Packet Lab Capture 2 read the live unit in Fan-only as:

- `power=1`, `mode=7`, `wind=0`, both swing axes off;
- protocol `temp=8`, which the status decoder represents as 23 °C;
- independent `indoorTemp=16`, matching the indoor display and a separate
  room thermometer;
- a physical remote with no target-temperature value in Fan-only.

The raw status frame was:

```text
BB 01 00 03 0F 01 00 32 07 00 00 00 00 00 00 00 00 5A 00 00 D8
```

Capture 1's Dry frame mapped byte 17 `0x5C` to 17 °C. Capture 2 maps `0x5A`
to 16 °C. These independent observations establish the half-degree indoor
temperature encoding `raw / 2 - 29`.

## Alpha.74 boundary

- The Dry → Fan-only command remains the exact official-SDK frame qualified in
  Alpha.73.
- The source must still match all nine Dry fields exactly.
- Fan-only post-write verification excludes only target temperature and checks
  the remaining eight applicable fields.
- Fan-only state publication suppresses the placeholder target temperature.
- The measured indoor temperature is published separately to Home Assistant.
- Temperature commands in Fan-only and every Fan-only exit remain fail-closed.
- The control write remains single-shot with zero retries. Read-only polling
  may continue for 30 seconds, and unexpected Power Off aborts immediately.
