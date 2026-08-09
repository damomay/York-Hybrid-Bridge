# Sprint 3.1.20 — Horizontal Swing Qualification

Alpha.49 adds an explicit one-shot qualification path for Horizontal swing at
the physically comfortable anchor state:

- On / Heat / 21.5 °C / Fan Low / Swing Vertical
- Vertical → Horizontal candidate
- Horizontal → Vertical qualified return

## Evidence boundary

The York status captures repeatedly isolate Horizontal swing as byte 10 bit
`0x20`. Existing native command evidence separately establishes:

- the Heat/Low/Swing Off state byte `0x02`;
- the Heat/Low/Swing Vertical state byte `0x3A`;
- the byte-11 `0x02` half-degree flag.

The candidate Horizontal frame therefore keeps the qualified Low/Off command
shape and uses byte 11 value `0x22` (`0x20` Horizontal plus `0x02` half-degree).
Physical testing showed that this reconstruction commanded Swing Off, not
Horizontal. The status-response bit cannot be copied into this write field.
Alpha.50 retains the frame only as rejected evidence and excludes it from the
write allowlist and executable package paths.

## Safety boundary

- Normal Home Assistant Horizontal and Both requests still use Relay v2.
- Execution requires a case-specific confirmation token.
- A fresh authenticated pre-read must match all nine fields.
- Exactly one write is sent, followed by one post-read.
- Four UDP sends, zero retries and no automatic restore.
- A mismatch stops before the write or reports failure without repeating it.
