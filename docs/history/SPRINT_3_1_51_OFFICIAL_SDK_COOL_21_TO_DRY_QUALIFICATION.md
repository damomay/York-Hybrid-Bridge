# Sprint 3.1.51 — Official-SDK Cool 21 °C to Dry Qualification

Capture 6 was generated offline on 2026-08-08 by York Write Packet Lab v1.
The live source was Power On / Cool / 21 °C / Fan Auto / both swing axes Off,
with optional features Off and Display On. The lab generated but did not send:

```text
BB 00 01 03 19 01 00 44 02 0A 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 ED
```

The official parser labels this native write mode as `mode=2` and preserves
the Cool source's `temp=10`, Fan Auto and stationary swing axes. In Dry mode,
the retained temperature byte is not a selectable target setpoint and is
therefore excluded from Home Assistant target publication and verification.

## Guarded behaviour

- Require the exact nine-field Cool / 21 °C / Fan Auto / Swing Off source.
- Recheck all nine fields in a fresh authenticated pre-read before writing.
- Enable only the exact request `Power On / Dry` from that source.
- Admit only Capture 6's byte-exact 31-byte command at the transport boundary.
- Perform one control write, zero retries and no fallback.
- Poll using read-only status queries for up to 30 seconds.
- Require all eight applicable Dry / Fan Auto / Swing Off target fields.
- Keep Home Assistant's Dry target temperature cleared while publishing the
  genuine independent room temperature.
- Abort critically if any verification read observes unexpected Power Off.

Alpha.72's legacy Dry 16 °C frame is removed from the production allowlist.
Capture 6 completes the five-mode official-SDK qualification loop:
Dry → Fan-only → Heat → Auto/FEEL → Cool → Dry.
