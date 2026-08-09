# Sprint 3.1.49 — Official-SDK Heat 23 °C to Auto/FEEL Qualification

Capture 4 was generated offline on 2026-08-08 by York Write Packet Lab v1.
The live source was Power On / Heat / 23 °C / Fan Auto / both swing axes Off,
with optional features Off and Display On. The lab generated but did not send:

```text
BB 00 01 03 19 01 00 44 08 08 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 E5
```

The official parser labels this native write mode as `mode=8` and preserves
the Heat source's `temp=8`, Fan Auto and both stationary swing axes.

## Guarded behaviour

- Require the exact nine-field Heat / 23 °C / Fan Auto / Swing Off source.
- Enable only the exact request `Power On / Auto` from that source.
- Admit only Capture 4's byte-exact 31-byte command at the transport boundary.
- Perform one control write, zero retries and no fallback.
- Poll using read-only status queries for up to 30 seconds.
- Require Auto/FEEL plus exact power, fan, swing and feature fields.
- Treat Auto's decoded temperature as a bounded 16.0–31.5 °C dynamic status
  field in 0.5 °C increments; Auto temperature commands remain unsupported.
- Abort critically if any verification read observes unexpected Power Off.

The older Alpha.69/72 Heat 25 °C to Auto candidate remains outside this new
qualification allowlist. No additional mode edge is enabled.
