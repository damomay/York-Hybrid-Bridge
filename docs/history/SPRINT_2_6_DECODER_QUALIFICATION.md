# Sprint 2.6 — York Decoder Qualification

Climate Bridge 1.0.0-alpha.13 qualifies the York state decoder offline against recovered Protocol Explorer observations.

## Scope

- 14 evidence-backed status-frame fixtures.
- Power, mode, fan, swing, turbo, eco, health and display checks.
- Header, length, message-type and XOR-checksum validation through the production decoder.
- JSON and Markdown reports written to `qualification-reports/`.
- No network traffic and no commands sent to the York module.

## Run

```bash
python york_decoder_qualification.py
```

Inside the container:

```bash
docker exec climate-bridge python /app/york_decoder_qualification.py --output-dir /reports
```

Temperature, sleep, timer and clock remain unresolved and are not guessed.
