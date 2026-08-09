# Climate Bridge 1.0.0

Climate Bridge connects one physically qualified York/TCL TFIAC 20014 air
conditioner to Home Assistant over MQTT. Version 1.0.0 uses authenticated
native LAN reads as its state authority and permits only guarded, physically
qualified native commands. Commands outside the accepted boundary fail closed;
the Android relay is not part of the current runtime.

## Start here

- [`PROJECT_STATUS.md`](PROJECT_STATUS.md) is the concise current source of truth.
- [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) explains the native runtime.
- [`docs/CONFIGURATION.md`](docs/CONFIGURATION.md) documents configuration.
- [`docs/V1_0_0_RELEASE_AND_UPGRADE_GUIDE.md`](docs/V1_0_0_RELEASE_AND_UPGRADE_GUIDE.md)
  contains deployment and upgrade guidance.
- [`docs/TESTING.md`](docs/TESTING.md) defines safe verification boundaries.
- [`AGENTS.md`](AGENTS.md) defines repository working rules.

## Supported V1 boundary

The accepted first-unit scope covers authoritative state reads and the guarded
Power, Cool, Heat, temperature, Fan Low/High, swing, and restricted mode-loop
operations recorded in the
[`V1 acceptance evidence`](docs/history/V1_0_0_ACCEPTANCE_AND_STABILITY_EVIDENCE.md).
The runtime is single-device and York-specific. Unsupported or ambiguous
requests are rejected without relay fallback.

## Quick start

Copy `config.example.yml` to an untracked `config.yml`, replace the documented
placeholder host and MAC address, and validate it before deployment:

```bash
python -c "from pathlib import Path; from validate_config import validate; print('Transport:', validate(Path('config.yml')))"
docker compose up -d --build
```

Do not commit credentials, device identifiers, private logs, raw captures, or
local configuration. Do not run a second bridge against the same MQTT topics.

## Current versus historical documentation

Root documents and the current files linked above describe 1.0.0. Earlier
Alpha, Beta, Relay v2, Android-relay, and incremental Sprint descriptions are
historical engineering records. They remain available in
[`RELEASE_NOTES.md`](RELEASE_NOTES.md), [`docs/history/`](docs/history/), and
[`docs/reconciliation/`](docs/reconciliation/) and must not be read as current
runtime requirements.

## Development

Begin with the mandatory orientation in `AGENTS.md`. Changes use a branch from
current `main` and a pull request into `main`; direct changes to `main` are not
permitted. The full safe local gate is documented in `docs/TESTING.md`.
