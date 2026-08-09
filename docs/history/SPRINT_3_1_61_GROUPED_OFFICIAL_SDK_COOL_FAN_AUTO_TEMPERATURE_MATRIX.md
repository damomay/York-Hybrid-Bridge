# Sprint 3.1.61 — Grouped Official-SDK Cool/Fan Auto Temperature Matrix

Alpha.90 consolidates six official native-parser temperature targets from York
Write Packet Lab Capture 10 and Capture 12 into one guarded qualification
release. The captures were generated offline and explicitly not transmitted.

The ordered physical qualification sequence is:

1. Cool 20.0 → 22.5 °C
2. Cool 22.5 → 24.0 °C
3. Cool 24.0 → 24.5 °C
4. Cool 24.5 → 20.5 °C
5. Cool 20.5 → 22.0 °C
6. Cool 22.0 → 20.0 °C

Every source and target is Power On / Cool / Fan Auto / Swing Off with Turbo,
Eco, and Health disabled and Display enabled. Each step requires an exact
nine-field cached source plus a matching fresh authenticated read before its
immutable SDK target frame is available to the write client.

The normal path performs one control write, four UDP sends, and zero automatic
retries. Immediate nine-field verification and delayed read-only verification
are mandatory. Unexpected Power Off is critical. A failed or stale source, an
uncaptured source→target pair, a modified frame, or any unrelated state change
stops the command without fallback.

The same target bytes may appear in earlier independently qualified edges.
Alpha.90 does not infer authority from packet bytes alone: cached-state and
fresh-read source gating remain the controlling distinction.
