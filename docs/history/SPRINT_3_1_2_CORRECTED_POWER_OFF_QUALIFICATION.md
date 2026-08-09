# Sprint 3.1.2 — Corrected Power Off Qualification

Alpha.31 corrects the Power Off qualification with fresh evidence from Relay
v2 transaction 46. Alpha.30's older 32-byte frame was rejected by the Wi-Fi
module with error `0xFFFB`; it contained one extra zero byte immediately before
checksum `D9`.

## Qualified case

- `off`: Relay v2 transaction 46, On/Cool/25/High/Vertical to Off.

The fresh accepted Power Off frame is 31 bytes. It is identical to Alpha.30's
rejected frame through byte 29, but omits the extra zero byte before `D9`.
Both frames have a zero XOR; exact length and SHA-256 are therefore required in
addition to checksum validation.

The case requires an exact nine-field live precondition, the Power Off
confirmation token, one write, zero retries, and a direct post-write
verification read. Offline validation opens no socket. Automatic restore is
disabled.

The normal MQTT power and mode paths remain on Relay v2. Guarded direct
temperature control from Alpha.29 is unchanged. Power On is not executable
from this qualification tool and remains deferred until corrected Power Off
passes live.
