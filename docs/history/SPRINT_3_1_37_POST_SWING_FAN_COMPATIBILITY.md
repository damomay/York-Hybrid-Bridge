# Sprint 3.1.37 — Post-Swing Fan Compatibility Qualification

Alpha.65 physically passed the four swing transitions, but its Step 5 fan
request stopped safely. The continuous log showed no `swing=off` transaction
before that request, and the fresh direct source remained decoded as
Horizontal. Alpha.64's fan guard correctly rejected that source.

Alpha.66 adds one case-specific qualification edge:

`Heat / 22.5 °C / Fan Low / decoded Horizontal → Fan High / Swing Off`

The edge uses Alpha.63's exact fingerprint-locked Heat / 22.5 °C / High / Off
frame. It requires the precise nine-field source both before client creation
and again in a fresh authenticated pre-read. The post-read must confirm all
nine target fields, including both Fan High and Swing Off.

The command still uses four UDP sends, zero automatic retries and no fallback.
Nearby modes, temperatures, fan values, swing values or feature flags stop
before a socket is created. Horizontal / High → Low is not authorised; after a
successful normalisation, Alpha.63's existing High / Off → Low / Off edge is
used unchanged.

Acceptance sequence:

1. Begin at the Alpha.65 stopped state: Heat / 22.5 °C / Fan Low, with both
   physical axes stationary.
2. Request Fan High in Home Assistant. Fan speed must increase, both axes must
   remain stationary, and the log must identify the Alpha.66 qualification.
3. Request Fan Low. Fan speed must decrease, both axes must remain stationary,
   and the log must identify the Alpha.63 qualification.
