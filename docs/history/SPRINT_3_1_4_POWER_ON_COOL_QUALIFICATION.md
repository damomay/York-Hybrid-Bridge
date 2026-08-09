# Sprint 3.1.4 — Power On + Cool Qualification

Alpha.33 adds one bounded direct-write case from successful Relay v2
transaction #4 recorded on 2026-07-29.

## Qualified case

- Before: Off / Heat / 25 °C / Fan High / Swing Vertical
- Requested by Home Assistant: Power On and mode Cool
- After: On / Cool / 25 °C / Fan High / Swing Vertical
- Captured command: exact 31-byte official SDK frame
- Confirmation token: `WRITE-QUALIFIED-POWER-ON-COOL-ONCE`

This is a combined Power On + Cool qualification. It is not evidence for a
power-only command and must not be generalized as one.

## Safety boundary

- Offline validation opens no socket.
- Live execution requires `--case on-cool` and the exact confirmation token.
- The nine-field live state must match before transmission.
- One write is permitted, with zero retries and no automatic restore.
- A direct post-read verifies all nine expected fields.
- The proven Power Off and Power On + Heat cases remain unchanged.
- Normal MQTT power and mode commands remain on Relay v2.
