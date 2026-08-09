# Sprint 3.1.35 — Grouped Fan Qualification Matrix

Alpha.64 groups compatible fan qualifications into one deployment while
retaining a separate safety transaction for every Home Assistant command.

## Evidence boundary

- Alpha.63 physically verified Heat / 22.5 °C / Low↔High / Swing Off.
- Alpha.62 physically verified Heat↔Cool at 22.5 °C / Low / Swing Off.
- The canonical Cool Low/Off frame differs from Heat Low/Off only at command
  byte 8 (`0x01` to `0x03`) and the XOR checksum.
- Applying that same mode-only transformation to the verified Heat High/Off
  frame produces the Cool High/Off candidate.
- The fan/swing byte remains `0x02` for Low/Off and `0x05` for High/Off.

The Cool High/Off frame is a case-specific candidate, not a general fan-field
encoding. It remains outside the immutable captured replay allowlist.

## Runtime boundary

- Exact new sources: On / Cool / 22.5 °C / Low or High / Off.
- Exact new targets: the opposite Low or High fan state with all other fields
  unchanged.
- A fresh authenticated nine-field pre-read must match before each write.
- Each successful command uses four UDP sends and zero retries.
- A delayed nine-field post-read must match all target fields.
- Every nearby temperature, mode, swing, power or feature state remains a
  zero-write safe-stop.
- Alpha.62 running-mode control and Alpha.63 Heat fan control remain unchanged.

## Continuous physical acceptance

Start at On / Heat / 22.5 °C / Fan Low / Swing Off:

1. Heat Low → High; both louvre axes stationary.
2. Heat High → Low; both louvre axes stationary.
3. Heat → Cool; temperature, fan and swing retained.
4. Cool Low → High; both louvre axes stationary.
5. Cool High → Low; both louvre axes stationary.
6. Cool → Heat; original state restored.

Allow at least one direct poll after each command. Stop the sequence immediately
on any physical mismatch, unexpected louvre movement, unavailable entity,
verification mismatch, safety stop, error, retry, or no response. Preserve one
continuous container log from startup through the final completed step.
