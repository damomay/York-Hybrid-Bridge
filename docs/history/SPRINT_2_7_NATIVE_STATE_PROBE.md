# Sprint 2.7 — First Native State Probe

## Delivered

- Qualification Report V2 integrated into the packaged project.
- One-shot native state probe decodes a valid York status response.
- Supported native fields are compared with the legacy relay state.
- Per-probe JSON evidence and cumulative qualification statistics are saved under `/reports/native-probes`.
- Qualification Report V2 reads cumulative native statistics automatically.

## Safety gates

- No socket is opened until a packet-library record is marked `verified`.
- Only records with purpose `state_request` and direction `request` are executable.
- One packet is sent per manual invocation.
- No automatic retry loop is used.
- Native write commands remain disabled.

## Commands

Validation only:

```sh
python /app/york_capture_probe.py --validate-only
```

Live one-shot probe after a verified state-request record is present:

```sh
python /app/york_capture_probe.py
```

Refresh the engineering report:

```sh
python /app/qualification_suite.py
```
