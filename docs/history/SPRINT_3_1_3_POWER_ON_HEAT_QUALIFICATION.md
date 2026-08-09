# Sprint 3.1.3 — Power On + Heat Qualification

Alpha.32 adds one bounded direct-write case from a fresh successful Relay v2
transaction recorded on 2026-07-29.

## Qualified case

- Before: Off / Cool / 25 °C / Fan High / Swing Vertical
- Requested by Home Assistant: Power On and mode Heat
- After: On / Heat / 25 °C / Fan High / Swing Vertical
- Captured command: exact 31-byte official SDK frame
- Confirmation token: `WRITE-QUALIFIED-POWER-ON-HEAT-ONCE`

This is a combined Power On + Heat qualification. It is not evidence for a
power-only command and must not be generalized as one.

## Safety boundary

- Offline validation opens no socket.
- Live execution requires `--case on-heat` and the exact confirmation token.
- The nine-field live state must match before transmission.
- One write is permitted, with zero retries and no automatic restore.
- A direct post-read verifies all nine expected fields.
- Alpha.31's corrected Power Off case remains unchanged.
- Normal MQTT power and mode commands remain on Relay v2.
