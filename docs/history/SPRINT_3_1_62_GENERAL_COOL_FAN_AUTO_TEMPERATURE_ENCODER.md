# Sprint 3.1.62 — General Cool/Fan Auto Temperature Encoder

Alpha.91 converts Alpha.90's fully qualified target-state matrix into one
guarded general encoder for Power On / Cool / Fan Auto / Swing Off.

The official native-parser evidence establishes this canonical frame rule:

- command byte 9 is `31 - whole target temperature`;
- command byte 10 remains `0x00` for Fan Auto;
- command byte 11 is `0x02` for a half degree and `0x00` for a whole degree;
- the complete 31-byte frame keeps Power and Display enabled, Cool mode, Fan
  Auto, Swing Off, and Turbo/Eco/Health disabled;
- the final byte is the XOR of the preceding 30 bytes.

The supported boundary is 16.0–31.0 °C in exact 0.5 °C increments. Both the
cached source and the fresh authenticated pre-read must match all nine guarded
fields, including a valid source temperature in that same boundary. Invalid,
unchanged, non-half-degree, or out-of-range targets stop before client creation.

The physical qualification sequence is:

1. Cool 22.5 → 16.0 °C
2. Cool 16.0 → 16.5 °C
3. Cool 16.5 → 27.5 °C
4. Cool 27.5 → 31.0 °C
5. Cool 31.0 → 22.5 °C

Each step performs one control write, four UDP sends, and zero automatic
retries. Immediate and delayed nine-field verification are mandatory; fallback
is disabled and unexpected Power Off is critical. Earlier byte-exact
qualifications remain as regression evidence, but production selection no
longer depends on a source→target edge registry.
