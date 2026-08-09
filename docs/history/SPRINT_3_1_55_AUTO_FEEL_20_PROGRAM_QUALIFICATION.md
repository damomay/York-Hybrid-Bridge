# Sprint 3.1.55 — Auto/FEEL 20 °C Program Qualification

Alpha.84 records the live Alpha.83 Heat 23 °C → Auto/FEEL result observed on
8 August 2026. The exact qualified Heat source and official-SDK command were
unchanged, the unit remained powered on, and the post-write authoritative read
reported Auto/FEEL with `status_byte=0x04`, decoded program temperature 20 °C,
Fan Auto and both swing axes Off. Home Assistant and the indoor display also
showed 20 °C while the independent measured room temperature was 22 °C.

Alpha.83 rejected only the post-write temperature because its explicit Auto
program allowlist contained 18, 21 and 23 °C. The write had already succeeded;
there was no transport, packet, source-guard or physical-control failure.

## Alpha.84 boundary

- Keep the exact Heat 23 °C → Auto/FEEL command unchanged.
- Add only the physically observed 20 °C result to the Auto program allowlist.
- Continue requiring the exact eight non-temperature Auto result fields.
- Count the separately validated Auto program temperature as the ninth matched
  field.
- Preserve one control write, four UDP sends, zero automatic retries, no
  fallback and delayed read-only verification.
- Preserve immediate critical failure on unexpected Power Off.
- Keep arbitrary representable Auto values rejected.
- Keep every Auto 20 °C mode exit blocked until a separate exact SDK capture is
  obtained and physically qualified.

Alpha.84 therefore corrects a result-model omission only. It adds no command
frame, source state, mode edge, temperature control path, fallback or retry.
