# Sprint 3.1.5 — Guarded Direct Power Control

Alpha.34 integrates three previously qualified captured commands into normal
Home Assistant MQTT control:

- Power Off from On/Cool/25 °C/High/Vertical.
- Power On + Heat from Off/Cool/25 °C/High/Vertical.
- Power On + Cool from Off/Heat/25 °C/High/Vertical.

Turbo, Eco, and Health must be off and Display must be on for every case.
Every eligibility decision compares all nine evidence-backed fields against
the last Relay v2 state before opening a direct session. The live direct
pre-read must independently match the same state.

Each accepted case performs exactly:

1. Broadlink authentication.
2. One direct state pre-read.
3. One exact captured 31-byte write.
4. One direct state post-read.

There are zero direct retries and no automatic restore. The post-read must
match all nine expected fields. A failed guard, network error, device error, or
verification mismatch falls back to Relay v2 when
`direct_control.fallback_to_relay` is true, and the transaction records the
fallback reason.

`direct_control.power_enabled` defaults to false independently of guarded
temperature control. This ensures that an Alpha.33 configuration copied
unchanged starts Alpha.34 with normal power control still on Relay v2.

Requests containing an unqualified field combination—including power-on with
a deferred target temperature—remain on Relay v2. Fan, swing, feature, and
other operating-mode transitions remain Relay-controlled.
