# Sprint 3.1.63 — General Cool Encoder Across Qualified Fan States

Alpha.92 extends Alpha.91's physically qualified Cool/Fan Auto temperature
encoder to preserve the three fan states already qualified independently in
Cool mode: Auto, Low, and High. Swing remains Off.

The complete target frame remains formula-derived:

- command bytes 0–8 preserve the canonical Power On / Display On / Cool shape;
- command byte 9 is `31 - whole target temperature`;
- command byte 10 is `0x00` for Auto, `0x02` for Low, or `0x05` for High;
- command byte 11 is `0x02` for a half degree and `0x00` for a whole degree;
- command bytes 12–29 remain zero;
- command byte 30 is the XOR of bytes 0–29.

This produces a closed transport boundary of 93 canonical frames: 31 target
temperatures from 16.0 through 31.0 °C in 0.5 °C increments, multiplied by
three qualified fan states. Medium and all unknown fan states remain rejected.

Each command requires an exact nine-field cached source and an independently
decoded fresh authoritative pre-read. The source must be Power On / Cool /
Swing Off with Turbo, Eco, and Health Off and Display On. The source fan is
preserved in the target; the command never selects a different fan speed.

The transaction remains one write, four UDP sends, zero automatic retries, no
fallback, immediate nine-field verification, and delayed read-only
verification. An unexpected Power Off observation remains a critical failure.

The grouped physical qualification sequence starts at Cool / 22.5 °C / Fan
Auto / Swing Off. Existing fan control first selects Low, then temperature
control tests 22.5 → 16.5 → 22.5 °C. Fan control then selects High, followed by
22.5 → 27.5 → 22.5 °C. This covers both qualified non-Auto fan states,
whole/half-degree targets, and large bidirectional temperature changes without
repeating Alpha.91's already-qualified Auto boundaries.
