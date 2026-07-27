# Sprint 2.5.1 — York Capture Importer

Climate Bridge 1.0.0-alpha.8 adds an evidence-preserving importer for York Protocol Explorer text logs.

## Usage

From the project directory:

```bash
python york_capture_importer.py /path/to/explorer.log
```

Multiple files and directories are supported:

```bash
python york_capture_importer.py /captures/session1.log /captures/session2.txt
```

Inside the container, mount or copy captures under `/config/captures`, then run:

```bash
python /app/york_capture_importer.py /config/captures --protocol-root /config/york_protocol
```

## Outputs

- Original source copies under `captures/imported/`
- Malformed candidates under `captures/quarantine/`
- Deduplicated observed packet records under `packet_library/observed/`
- Chronological events under `timelines/`
- Import reports under `reports/`
- Latest summary under `statistics/latest_import.json`

## Safety

The importer never marks a packet as verified and never transmits packets. Every generated packet record has `verification.status: observed`, `kind: unknown`, and remains non-executable until manually reviewed.
