# Climate Bridge

[![Python](https://img.shields.io/badge/Python-3.12-blue.svg)]()
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED.svg)]()
[![Home Assistant](https://img.shields.io/badge/Home%20Assistant-MQTT%20Discovery-41BDF5.svg)]()
[![License](https://img.shields.io/badge/License-MIT-green.svg)]()

Climate Bridge connects supported York split-system air conditioners to Home
Assistant through MQTT Discovery.

**Current version:** `1.0.0-alpha.20`

**Release status:** reconciliation alpha

**Verified transport:** Android/tablet HTTP relay (`relay`)

**Native York control:** research only; disabled and not verified for
transmission

The current working path still requires the Android York TFIAC Relay V2.
Climate Bridge sends local HTTP JSON to that relay; the Android application
constructs the native command sent to the Broadlink/TFIAC Wi-Fi module.
Climate Bridge does not currently extract or send those native command bytes.

## Verified capabilities

The one-device Android-relay path has been live-tested with a York split
system and Home Assistant:

- MQTT Discovery and device/entity publication;
- state polling and returned-state synchronisation;
- power on and off;
- heat and cool mode selection;
- target-temperature changes;
- low and high fan speeds;
- vertical swing on and off;
- automatic MQTT and relay recovery; and
- a container restart that did not wake the powered-off air conditioner.

The Phase 9 reconciliation gate collected **122 tests**, all passing. The
qualified Docker workflow also proved a clean image build, network-free
packaging startup, health reporting and clean `SIGTERM` shutdown.

## Requirements

- Home Assistant with an MQTT broker;
- one supported York split-system air conditioner with a Broadlink/TFIAC
  Wi-Fi module (device type 20014);
- the Android York TFIAC Relay V2 reachable from the Docker host;
- Docker with Compose support; and
- a host that can reach the MQTT broker and relay.

The current configuration represents one York device. Multiple-device support
has not started.

## Architecture

```text
Home Assistant
    ↕ MQTT state, commands and discovery
Climate Bridge
    ↕ local HTTP JSON
Android York TFIAC Relay V2
    ↕ native York/TFIAC traffic built by the Android app
York Wi-Fi module and air conditioner
```

Climate Bridge separates the bridge core, York adapter and selectable
transport. The abstraction is present, but only the relay transport is
verified for normal use. See [Architecture](docs/ARCHITECTURE.md).

## Install with Docker Compose

1. Clone or download this repository.
2. Copy the committed example:

   ```bash
   cp config.example.yml config.yml
   ```

3. Edit `config.yml`:

   - set `transport.base_url` to the Android relay URL;
   - set `mqtt.host`, and credentials if your broker requires them;
   - choose unique `mqtt.base_topic`, `mqtt.client_id`,
     `device.unique_id` and `device.bridge_unique_id`; and
   - leave `transport.type: "relay"` and `direct_device.enabled: false`.

4. Validate the configuration:

   ```bash
   python -c "from pathlib import Path; from validate_config import validate; print('Transport:', validate(Path('config.yml')))"
   ```

5. Build and start:

   ```bash
   docker compose build --pull
   docker compose up -d
   docker compose logs -f climate-bridge
   ```

6. Confirm the log reports:

   - Climate Bridge `1.0.0-alpha.20`;
   - transport `Relay (Legacy)`;
   - MQTT connected;
   - discovery published; and
   - bridge state `READY`.

7. Confirm the Home Assistant device appears and agrees with the physical
   unit before sending a command.

For Synology Container Manager, import `docker-compose.yml` as a project after
creating `config.yml` in the project directory. Keep the relative
`qualification-reports` directory because Compose mounts it at `/reports`.

The repository does not contain `config.yml`; it is intentionally ignored so
local addresses and credentials are not committed.

## Configuration

The complete, sanitized schema is in
[`config.example.yml`](config.example.yml). MQTT credentials are optional:
leave both values empty only when the broker allows anonymous connections.

The safe transport settings are:

```yaml
transport:
  type: "relay"
  base_url: "http://TABLET_IP:8765"

direct_device:
  enabled: false
```

Do not enable `york_direct` by copying an observed response frame into
`state_request_hex`. The current evidence library contains state responses,
not a verified native request. See
[Configuration](docs/CONFIGURATION.md) and
[York protocol evidence](protocols/york/README.md).

## Development and qualification

Create an isolated environment and run the reproducible local gate:

```bash
python -m venv .venv
. .venv/bin/activate
python -m pip install -r requirements.txt
python -m pip install pytest
python -m compileall -q -f .
python phase6_quality_gate.py
python release_verifier.py
python -c "from pathlib import Path; from validate_config import validate; print('Example transport:', validate(Path('config.example.yml')))"
python -m pytest
python york_decoder_qualification.py --no-write
```

On the Phase 8 baseline, the expected results are:

- complete suite: `117 passed`;
- decoder qualification: `PASS (14/14)`;
- observed York library: 23 state responses;
- eligible native request candidates: 0; and
- verified/executable native records: 0.

Docker build and shutdown qualification runs in
[`.github/workflows/qualification.yml`](.github/workflows/qualification.yml).
See [Testing](docs/TESTING.md) for local and container commands.

## Known limitations

- The Android relay is still required.
- Native direct control and tablet removal have not been achieved.
- The native evidence store has no verified, transmit-safe command/request.
- Only one York device is configured and live-qualified.
- Multiple-device and multi-vendor support are future work.
- Protocol analysis tools are offline/no-send by default and do not prove
  that a response packet is safe to transmit.
- This is an alpha release; back up a working deployment before replacing it.

See [Troubleshooting](docs/TROUBLESHOOTING.md) before changing timeouts,
transport type or experimental settings.

## Project lineage

Climate Bridge evolved from the proven York Hybrid Bridge 3.0 RC5 runtime and
the polished York Hybrid Bridge 3.0 repository. The reconciliation retained
that relay runtime, recovery, diagnostics, repository structure and test
baseline, then incorporated the Climate Bridge alpha.20 transport abstraction
and protocol-research tooling.

York Hybrid Bridge names and 3.0 version numbers in the changelog describe
historical milestones. They are not the current application identity.

## Roadmap

Reconciliation must finish before feature expansion. The locked order after
reconciliation is:

1. native command discovery and tablet removal;
2. qualification of direct device communication;
3. controlled single-device direct-operation testing;
4. multiple-device support; and
5. broader HVAC adapter framework work.

See [Roadmap](ROADMAP.md) for milestones and safety gates.

## Contributing, security and license

- Read [Contributing](CONTRIBUTING.md) before proposing changes.
- Report vulnerabilities using [Security Policy](SECURITY.md); never publish
  credentials or private capture data.
- Climate Bridge is released under the [MIT License](LICENSE).

Current release details are in [Release notes](RELEASE_NOTES.md) and project
history is in the [Changelog](CHANGELOG.md).
