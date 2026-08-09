# Sprint 3.1.42 — Dry Dynamic Status Mode Matrix Correction

Alpha.70 physically completed Cool → Dry, but the live post-read returned
Dry / 21 °C rather than the historical Dry / 16 °C fixture. Normal polling
then confirmed that live state. The following Dry → Fan-only edge safely
stopped before transmission because its source guard still required 16 °C.

Alpha.71 keeps the byte-exact captured Dry command unchanged. Only comparisons
of an observed Dry status may accept a decoder-representable 16.0–31.5 °C
half-degree value. Mode, fan, swing, power, turbo, eco, health and display remain
exact. Invalid, out-of-range and quarter-degree values stop before a client is
created. Dry temperature commands remain unsupported.

The correction applies to both Cool → Dry post-write verification and
Dry → Fan-only authoritative/fresh pre-read validation. Four UDP sends, zero
retries and no fallback remain mandatory.
