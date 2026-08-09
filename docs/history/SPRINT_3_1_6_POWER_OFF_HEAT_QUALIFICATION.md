# Sprint 3.1.6 — Power Off from Heat Qualification

## Evidence

Relay v2 transaction #7 on 2026-07-30 successfully changed the physical unit
from On/Heat/25 °C/High/Vertical to Off/Heat/25 °C/High/Vertical. SDK response
code was zero and Relay read-back verified the requested power state.

Exact accepted 31-byte command:

```text
BB 00 01 03 19 01 00 40 01 06 3D 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 DB
```

SHA-256:
`6be1093e8fb776faf047513d3b0bd6b9cca2166fac49d60346ce1f3575707b58`

## Safety boundary

- Case name: `off-heat`
- Confirmation token: `WRITE-QUALIFIED-POWER-OFF-HEAT-ONCE`
- Exact nine-field direct pre-read required
- One captured write
- Zero automatic retries
- Exact nine-field post-read required
- No automatic restore
- No startup or normal MQTT route
- Alpha.34 guarded power control and Relay v2 fallback remain unchanged
