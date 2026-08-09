# Sprint 3.1.21 — Independent Horizontal Axis Qualification

Alpha.50 replaces Alpha.49's rejected status-bit inference with exact Relay v2
write-command evidence and models Vertical and Horizontal as independent axes.

The physically comfortable anchor state is:

- On / Heat / 21.5 °C / Fan Low
- Vertical On / Horizontal Off (`vertical`)
- Enable Horizontal while preserving Vertical (`both`)
- Disable Horizontal while preserving Vertical (`vertical`)

## Evidence boundary

- Relay transaction #20 physically moved the Horizontal louvres left-to-right
  and established the command-side Horizontal flag as `0x08`.
- The separate handheld-remote buttons confirm that the Vertical and Horizontal
  axes are independently toggled.
- The exact Relay Both frame uses bytes 10–11 `3A 0A`: Vertical stays enabled
  in `0x3A`, while byte 11 combines Horizontal `0x08` with the half-degree
  flag `0x02`.
- Alpha.49's `02 22` candidate commanded Off. It is retained only as rejected
  evidence and is excluded from the write allowlist.

The Both state remains pending physical qualification because Vertical motion
was not visibly confirmed during the Relay test. Alpha.50 therefore exposes
only an explicitly confirmed one-shot qualification path.

## Safety boundary

- Normal Home Assistant Horizontal and Both requests continue through Relay v2.
- Execution requires a case-specific confirmation token.
- A fresh authenticated pre-read must match all nine fields.
- Exactly one write is sent, followed by one post-read.
- Four UDP sends, zero retries and no automatic restore.
- A mismatch stops before the write or reports failure without repeating it.
