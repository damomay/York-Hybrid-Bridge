# Sprint 3.1.39 — Auto/FEEL 22 °C Mode-Matrix Correction

Alpha.68 corrects Alpha.67's Auto/FEEL assumption using the live evidence from
this York unit. Repeated direct reads reported Auto / 22 °C / Fan Auto / Swing
Off with `status_byte=0x06`. Remote selections of 20, 26 and 23 °C were each
held for 45 seconds but did not alter the authoritative state. The manual also
describes FEEL temperature keys as a relative ±2 °C comfort adjustment rather
than a conventional absolute setpoint.

The corrected ordered sequence is:

1. Auto / 22 °C / Fan Auto / Swing Off → Cool / 22 °C / Fan Auto / Off
2. Cool / 22 °C / Fan Auto / Swing Off → Dry / 16 °C / Fan Auto / Off
3. Dry / 16 °C / Fan Auto / Swing Off → Fan-only / 23 °C / Fan High / Off
4. Fan-only / 23 °C / Fan High / Swing Off → Heat / 25 °C / Fan Auto / Off
5. Heat / 25 °C / Fan Auto / Swing Off → Auto / 22 °C / Fan Auto / Off

Only the two Auto endpoints change. The other target shapes remain anchored to
the labelled TFIAC Modes log. The canonical Auto command uses temperature byte
`0x09` for 22 °C and a recalculated XOR checksum.

Each edge requires an exact nine-field authoritative source, a matching fresh
direct pre-read, one candidate write, four UDP sends, zero retries and a fresh
nine-field verification read. The obsolete Auto / 23 °C source, skipped edges,
same-mode requests, altered settings and feature flags stop before client
creation.

Auto temperature commands remain unsupported. Alpha.68 does not attempt to
encode the FEEL ±2 °C comfort offset because it was not exposed by the observed
authoritative Wi-Fi state.
