# Sprint 3.1.28 — Poll-Failure Counter Correction

Alpha.57 corrects the diagnostic counter observed during Alpha.56's physical
York-module interruption test. Once the configured three-failure threshold was
reached, later attempts were displayed as `4/3`, `18/3` and higher even though
the entity had already entered its unavailable state correctly.

## Behaviour

- Threshold-facing poll logs progress from `1/3` through `3/3` and remain
  capped at `3/3` for the rest of the same continuous outage.
- Transport and direct-state retry diagnostics use the same capped value.
- The internal consecutive-attempt history remains available to the recovery
  path and resets only after a successful authoritative read.
- The first failure after recovery is displayed as `1/3`.
- The configured threshold, Home Assistant availability transition, container
  health, recovery duration and polling schedule are unchanged.
- No native York packet, command allowlist, direct-state authority rule or
  optional Relay v2 fallback boundary is changed.

## Physical verification sequence

1. Keep Relay v2 stopped and start Alpha.57 normally.
2. Confirm the authoritative direct read restores the correct Home Assistant
   state.
3. Temporarily block only the York Wi-Fi module in UniFi.
4. Confirm the climate entity becomes unavailable and no displayed failure
   counter exceeds the configured threshold.
5. Unblock the York module and confirm state recovers automatically.
6. Confirm the next controlled interruption begins again at `1/3` only if a
   second interruption is required.

No Home Assistant command is issued while authoritative state is unavailable.
