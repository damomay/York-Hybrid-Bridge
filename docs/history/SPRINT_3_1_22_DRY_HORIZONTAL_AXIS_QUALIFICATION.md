# Sprint 3.1.22 — Dry-Mode Horizontal Axis Qualification

Alpha.51 moves the independent Horizontal-axis qualification to Dry mode so
both physical axes can be observed without Heat-mode vane parking masking the
result.

The exact Relay v2 evidence was physically confirmed in both directions:

- Dry / 21 °C / Fan Low / Vertical → Both: Horizontal began moving while
  Vertical continued.
- Dry / 21 °C / Fan Low / Both → Vertical: Horizontal stopped while Vertical
  continued.

## Packet boundary

- Vertical → Both: bytes 8–11 `02 0A 3A 08`, checksum `DF`.
- Both → Vertical: bytes 8–11 `02 0A 3A 00`, checksum `D7`.
- The command-side Horizontal flag is the independent `0x08` bit.
- Dry mode reports a normalised 21 °C setpoint; the half-degree flag is absent.

## Safety boundary

- Normal Home Assistant Horizontal and Both requests continue through Relay v2.
- The Alpha.50 Heat-specific tool is not copied into the container.
- Execution requires a case-specific confirmation token.
- A fresh authenticated pre-read must match all nine fields exactly.
- Exactly one write is sent, followed by one post-read.
- Four UDP sends, zero retries and no automatic restore.
- A mismatch stops before the write; a failed post-read is never retried.
