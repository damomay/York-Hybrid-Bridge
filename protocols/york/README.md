# York TFIAC Protocol Reference

This directory is the authoritative protocol evidence store for the Climate Bridge York TFIAC adapter.

## Evidence rules

1. A packet is **verified** only when its full raw request/response bytes and capture context are stored here.
2. Notes reconstructed from development conversations are marked **observed** or **unverified** and must not be transmitted by production code.
3. Executable native requests must reference a packet-library entry with `verification.status: verified`.
4. Every verified entry must identify its source capture and expected device state.
5. Sensitive identifiers should be redacted before captures are committed.

## Layout

- `captures/` — original or normalized Protocol Explorer logs and raw frame captures.
- `packet_library/` — machine-readable packet records used by tests and probe tooling.
- `documentation/` — protocol format, state mapping, checksum and research notes.
- `schemas/` — JSON schemas for packet-library and capture records.

## Current status

The existing project history establishes that York/TCL device traffic contains `0xBB`-headed frames and that controlled UI actions produced repeatable byte changes. Those observations are recorded in `documentation/observations.md`, but no full state-poll request has yet been promoted to `verified` status in this repository.

The live bridge therefore remains on `Relay (Legacy)` until a complete captured request/response pair is imported and verified.

## Capture importer

Use `york_capture_importer.py` to convert York Protocol Explorer `.txt` or `.log` files into traceable observed records:

```bash
python york_capture_importer.py /path/to/captures
```

The importer deduplicates identical frames, preserves MARK annotations and source locations, reconstructs an event timeline, and quarantines malformed candidates. It never verifies or transmits a packet.
