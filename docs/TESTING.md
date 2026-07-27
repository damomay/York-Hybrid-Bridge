# Testing and qualification

Run commands from the repository root. Python 3.12 matches the Docker image
and GitHub workflows.

## Local setup

```bash
python -m venv .venv
. .venv/bin/activate
python -m pip install -r requirements.txt
python -m pip install pytest
```

On Windows Command Prompt, activate with `.venv\Scripts\activate.bat`. On
PowerShell, use `.venv\Scripts\Activate.ps1`.

## Complete local gate

```bash
python -m compileall -q -f .
python phase6_quality_gate.py
python release_verifier.py
python -c "from pathlib import Path; from validate_config import validate; print('Example transport:', validate(Path('config.example.yml')))"
python -m pytest
python york_decoder_qualification.py --no-write
git diff --check
git status --short
```

Expected at the Phase 8 baseline:

- tracked-tree privacy/generated-file gate: pass;
- release verification: Climate Bridge `1.0.0-alpha.20`;
- example transport: `relay`;
- complete suite: `117 passed`;
- decoder qualification: `PASS (14/14)`;
- `git diff --check`: no output; and
- no unexpected generated or sensitive files in `git status`.

The exact test count may rise after new tests are added. A lower count requires
investigation; do not hide failures with skips, xfails or weakened assertions.

## Docker build and normal startup

Create a local `config.yml` first, then run:

```bash
docker compose build --pull
docker compose up -d
docker compose ps
docker compose logs climate-bridge
docker compose down
```

Normal startup is a live integration path: it connects to MQTT and the
configured relay. Do not use it as an offline test.

## Network-free container qualification

The authoritative container gate is
`.github/workflows/qualification.yml`. It:

1. installs the exact runtime dependencies and pytest;
2. runs compilation, privacy, package, configuration and complete tests;
3. builds a no-cache image labelled with `VERSION` and the commit SHA;
4. overrides the normal command with `container_qualification.py`;
5. starts without MQTT, relay or HVAC network access;
6. checks health and evidence logs; and
7. verifies clean `SIGTERM` shutdown with exit code 0.

The Phase 6 run passed this gate for `1.0.0-alpha.20`.

## Protocol tools

These commands are offline/no-send unless their help explicitly states
otherwise:

```bash
python york_decoder_qualification.py --no-write
python york_packet_classifier.py --help
python york_request_hunter.py --help
python york_capture_importer.py --help
python york_relay_extraction_report.py --help
```

Do not use `york_replay_engine.py` or a native probe merely because a tool is
packaged. Transmission remains guarded and unverified. Review
`protocols/york/README.md` and the controlling safety evidence first.

## Live regression boundary

Phase 7 qualified one existing Android-relay device in this order: startup,
entity/state review, power on, cool mode, 22 °C, low/high/low fan comparison,
vertical swing on/off, power off and container restart. Every step agreed
across Home Assistant, returned state and physical behaviour. The powered-off
unit remained off through restart.

Repeat live tests one setting at a time, preserve a rollback copy and stop on
duplicate commands, unexpected state changes or physical/state disagreement.
