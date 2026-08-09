# Sprint 3.1.50 — Official-SDK Auto/FEEL 21 °C to Cool Qualification

Capture 5 was generated offline on 2026-08-08 by York Write Packet Lab v1.
The live source was Power On / Auto/FEEL / 21 °C status / Fan Auto / both
swing axes Off, with optional features Off and Display On. The lab generated
but did not send:

```text
BB 00 01 03 19 01 00 44 03 0A 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 EC
```

The official parser labels this native write mode as `mode=3` and preserves
the Auto/FEEL source's `temp=10`, Fan Auto and stationary swing axes. Once
Cool is active, `temp=10` becomes an applicable 21 °C target setpoint.

## Guarded behaviour

- Require the exact nine-field Auto/FEEL / 21 °C / Fan Auto / Swing Off source.
- Recheck all nine fields in a fresh authenticated pre-read before writing.
- Enable only the exact request `Power On / Cool` from that source.
- Admit only Capture 5's byte-exact 31-byte command at the transport boundary.
- Perform one control write, zero retries and no fallback.
- Poll using read-only status queries for up to 30 seconds.
- Require all nine Cool / 21 °C / Fan Auto / Swing Off target fields.
- Restore 21 °C as Home Assistant's applicable Cool target setpoint.
- Abort critically if any verification read observes unexpected Power Off.

Alpha.72's Cool 22 °C frame is removed from the production allowlist. Every
other Auto/FEEL exit and every nearby Auto/FEEL source remains disabled.
