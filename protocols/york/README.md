# York TFIAC Protocol Reference

This directory is the authoritative protocol evidence store for the Climate Bridge York TFIAC adapter.

## Evidence rules

1. A packet is **verified** only when its full raw request/response bytes and capture context are stored here.
2. Notes reconstructed from development conversations are marked **observed** or **unverified** and must not be transmitted by production code.
3. Executable native requests must reference a packet-library entry with
   `verification.status: verified`, `safe_to_transmit: true`, at least one
   successful response, and an identified source capture.
4. Every verified entry must identify its source capture and expected device state.
5. Sensitive identifiers should be redacted before captures are committed.

## Layout

- `captures/` — original or normalized Protocol Explorer logs and raw frame captures.
- `packet_library/` — machine-readable packet records used by tests and probe tooling.
- `documentation/` — protocol format, state mapping, checksum and research notes.
- `schemas/` — JSON schemas for packet-library and capture records.

## Current status

Climate Bridge 1.0.0 uses authenticated native LAN reads and a guarded native
command boundary; the Android relay is not a current runtime dependency. The
supported V1 behaviour remains limited to the accepted scope recorded in
[`PROJECT_STATUS.md`](../../PROJECT_STATUS.md) and the
[`v1.0.0 release guide`](../../docs/V1_0_0_RELEASE_AND_UPGRADE_GUIDE.md).

Historical relay extraction records contain the HTTP JSON that was submitted
to the Android relay during earlier development. They remain useful historical
evidence, but are a separate evidence type and are not native York packet bytes.
Historical observations that York/TCL traffic contains `0xBB`-headed frames and
that controlled UI actions produced repeatable byte changes remain recorded in
`documentation/observations.md`. This status correction does not promote any
packet to `verified` or broaden protocol support.

## Capture importer

Use `york_capture_importer.py` to convert York Protocol Explorer `.txt` or `.log` files into traceable observed records:

```bash
python york_capture_importer.py /path/to/captures
```

The importer deduplicates identical frames, preserves source SHA-256, source
locations, timestamp context, direction tokens, MARK annotations and declared
transformations, reconstructs an event timeline, and quarantines malformed
candidates. It never verifies or transmits a packet.
