# Sprint 2.9.1 — Fan Status Diagnostics

Alpha.21 proved repeated read-only Broadlink LAN observations but exposed one
state mismatch: Relay v2 reported `fan=low` while the direct York status frame
decoded as `fan=auto`.

Alpha.22 preserves the decoder mapping and publishes the evidence needed to
resolve the mismatch:

- exact 21-byte York status frame as uppercase hexadecimal;
- raw status byte 8;
- high fan-status nibble extracted from byte 8;
- relay fan label;
- direct fan label.

The diagnostic data is retained under:

`york/ac2/diagnostic/native_state`

Safety boundaries are unchanged:

- relay remains the active transport;
- direct LAN access remains read-only;
- the only York request is `BB000104020100BD`;
- each observation permits authentication plus one state query;
- there are no automatic retries or direct control encoders.
