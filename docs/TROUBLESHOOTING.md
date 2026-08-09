# Troubleshooting

## Start with the logs

```bash
docker compose ps
docker compose logs --tail 200 climate-bridge
```

A healthy Climate Bridge 1.0.0 startup identifies the native transport,
connects to MQTT, publishes Home Assistant discovery, obtains authoritative
native state, and reaches `READY`. The Android relay is not a runtime service.

## Configuration validation fails

Run:

```bash
python -c "from pathlib import Path; from validate_config import validate; print('Transport:', validate(Path('config.yml')))"
```

Compare against `config.example.yml`. Common causes include missing MQTT,
device, transport, or direct-read values; an empty broker host; invalid numeric
YAML; a placeholder/invalid York host or MAC; or native transport without
`direct_read.enabled`. Do not weaken validation to accept old relay config.

## Home Assistant device does not appear

Check broker access, MQTT integration health, the discovery prefix, unique IDs,
client ID, base topic, and discovery-publication logs. A successful restart
republishes discovery; it must not operate the physical unit.

## Native state is unavailable or disagrees with the unit

Stop issuing commands. Record the version, timestamp, Home Assistant state,
physical state, a short sanitized log excerpt, and whether any command repeated.
Check that the configured York host/MAC are the approved unit and that the
container can reach it. Do not substitute an Android relay or enable a broader
command path as a workaround.

Resume only after authoritative polling recovers and the discrepancy is
understood. Live testing requires the approval and boundaries in `AGENTS.md`.

## Container is unhealthy

Confirm that `config.yml` exists and is mounted read-only, required local
directories are writable, MQTT and the configured York module are reachable,
and logs show no repeated recovery loop. `healthcheck.py` evaluates the running
bridge; `container_qualification.py --healthcheck` belongs only to the
network-free qualification command.

## Reports or protocol-tool results

Generated reports are intentionally untracked and may contain private device or
network data. Sanitize them before sharing. A no-candidate or rejected-packet
result is a safety outcome: never convert a response or unknown capture into a
command merely to make a tool pass.

For support, provide the version, platform, redacted configuration, reproduction
steps, and a short relevant sanitized log excerpt. Never publish credentials,
tokens, MAC/IP addresses, or raw private captures.
