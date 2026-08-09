# Sprint 3.1.56 — Official-SDK Auto/FEEL 20 °C to Cool Qualification

Alpha.85 adds the one exact mode edge needed to leave the Auto/FEEL 20 °C
program observed during Alpha.83 and accepted by Alpha.84. York Write Packet
Lab v1 Capture 9 read the live unit on 8 August 2026 as Power On, Auto/FEEL,
20 °C program, Fan Auto, both swing axes Off, Display On and all optional
features Off. The official TCL/Broadlink parser then generated the Cool frame
offline through `setSplitAirconInfo()` and explicitly did not transmit it.

## Capture 9 evidence

- Raw status: `BB 01 00 03 0F 01 00 35 04 00 00 00 00 00 00 00 00 5F 00 00 D9`
- SDK fields: `power=1, mode=8, temp=11, half=0, wind=0, LR=0, UD=0`
- Bridge state: Auto/FEEL 20 °C / Fan Auto / Swing Off
- Requested SDK output: `MODE COOL`
- Exact command: `BB 00 01 03 19 01 00 44 03 0B 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 ED`
- Command length: 31 bytes
- XOR over the complete command: zero
- Packet Lab network write: none

The retained native `temp=11` becomes an applicable 20 °C target when Cool is
active. No temperature conversion or packet synthesis is inferred by this
release; the command is stored byte-for-byte from the official SDK output.

## Alpha.85 boundary

- Authorise only Auto/FEEL 20 °C → Cool 20 °C.
- Require all nine exact source fields from both the current authoritative
  state and a fresh authenticated pre-read.
- Require all nine exact Cool result fields.
- Preserve Fan Auto, Swing Off, Display On, and Turbo/Eco/Health Off.
- Perform one control write, four normal UDP sends, zero automatic retries and
  no fallback.
- Use delayed read-only verification for convergence.
- Treat unexpected Power Off as an immediate critical failure.
- Keep Auto 18 °C and all other uncaptured Auto-temperature sources blocked.
- Keep Auto 20 °C exits to Heat, Dry and Fan-only blocked.

Alpha.85 does not alter the Auto program allowlist, decoder, transport retry
policy, temperature-control selector, or any previously qualified edge.
