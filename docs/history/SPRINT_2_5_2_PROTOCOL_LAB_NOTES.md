# Sprint 2.5.2 — York Protocol Lab

Climate Bridge 1.0.0-alpha.9 adds a self-contained static Protocol Lab dashboard and strengthens the capture workflow.

## Added

- `york_protocol_lab.py` dashboard generator.
- `protocols/york/lab_dashboard.py` evidence model and HTML renderer.
- Direct `.docx` capture ingestion without Microsoft Word or extra Python dependencies.
- Automatic dashboard refresh after every import.
- Feature coverage for power, modes, temperature, fan, swing, turbo, eco, health, sleep, display and timer.
- Redacted capture copies by default; raw credential-bearing copies require `--copy-raw`.
- Automatic creation of dashboard and qualification-report directories.
- Initial observed packet library generated from the recovered Modes, Swing, Display and V2 Tests logs.

## Safety

Imported packets remain `observed` and non-executable. The dashboard reports evidence; it does not authorize packets for transmission.
