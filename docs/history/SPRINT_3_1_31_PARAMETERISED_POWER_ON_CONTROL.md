# Sprint 3.1.31 — Parameterised Power-On Control

Alpha.60 extends the guarded native power-on path to complete target-state
frames already qualified by the York command generators. It addresses the
Alpha.59 physical finding where Off / Heat / 21.5 °C / Fan Low / Swing Off was
correctly rejected because the original power manager recognised only one
captured Off baseline.

The fresh authoritative direct read remains mandatory. Alpha.60 preserves its
temperature, fan and swing while applying the requested Heat or Cool mode, and
accepts only these proven shapes:

- Heat or Cool / Fan Low / Swing Off, 16–30 °C in 0.5 °C increments.
- Heat / Fan Low / Swing Vertical, 16–31 °C in 0.5 °C increments.
- Heat / Fan High / Swing Vertical, 16–31 °C in 0.5 °C increments.
- Turbo, Eco and Health must be Off; Display must be On.

The observed 21.5 °C frame is byte-for-byte the exact command already captured
and physically qualified for Heat / Fan Low / Swing Off. Unsupported shapes
safe-stop before client creation. Every accepted command retains one fresh
pre-read, one write, one post-read, nine-field verification, four UDP sends,
zero automatic retries and no fallback.

Alpha.60 also replaces the obsolete power-path phrase `relay state` with
`authoritative direct state`. Relay runtime remains absent.
