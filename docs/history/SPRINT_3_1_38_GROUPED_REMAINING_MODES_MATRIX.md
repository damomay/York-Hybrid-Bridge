# Sprint 3.1.38 — Grouped Remaining Modes Qualification Matrix

Alpha.67 adds one isolated, ordered candidate sequence based on the labelled
TFIAC Modes log recovered from this York unit:

1. Auto / 23 °C / Fan Auto / Swing Off → Cool / 22 °C / Fan Auto / Off
2. Cool / 22 °C / Fan Auto / Swing Off → Dry / 16 °C / Fan Auto / Off
3. Dry / 16 °C / Fan Auto / Swing Off → Fan-only / 23 °C / Fan High / Off
4. Fan-only / 23 °C / Fan High / Swing Off → Heat / 25 °C / Fan Auto / Off
5. Heat / 25 °C / Fan Auto / Swing Off → Auto / 23 °C / Fan Auto / Off

The varying target temperatures and fan values are intentional: they reproduce
the complete authoritative shapes seen in the original labelled sequence.
Alpha.67 does not claim that a mode-only change preserves settings across all
five operating modes.

Each edge requires an exact nine-field authoritative source, a matching fresh
direct pre-read, one candidate write, four UDP sends, zero retries and a fresh
nine-field verification read. Skipped edges, same-mode requests, altered
settings and feature flags stop before client creation. The candidates remain
outside the immutable captured replay allowlist pending physical acceptance.

Earlier Heat/Cool parameterised control and all Alpha.64-66 fan and swing paths
remain unchanged.
