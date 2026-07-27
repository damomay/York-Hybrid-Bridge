# Troubleshooting

## Start with the logs

```bash
docker compose ps
docker compose logs --tail 200 climate-bridge
```

On a healthy relay startup, look for Climate Bridge `1.0.0-alpha.20`,
`Relay (Legacy)`, MQTT connection, discovery publication and `READY`.

## Configuration validation fails

Run:

```bash
python -c "from pathlib import Path; from validate_config import validate; print('Transport:', validate(Path('config.yml')))"
```

Common causes:

- missing `mqtt`, `device` or `transport` mapping;
- empty `mqtt.host`;
- relay `base_url` without `http://` or `https://`;
- invalid numeric YAML value; or
- selecting `york_direct` while its explicit safety requirements are absent.

Compare the file with `config.example.yml`. Do not weaken validation to make an
old configuration pass.

## Home Assistant device does not appear

Check:

1. the broker address and credentials;
2. MQTT integration health in Home Assistant;
3. `discovery_prefix` (normally `homeassistant`);
4. that `unique_id`, `bridge_unique_id`, `client_id` and `base_topic` do not
   collide with another deployment; and
5. the logs for discovery publication.

Restart Climate Bridge only after fixing the cause. A successful restart
republishes discovery; it should not operate the physical unit.

## Relay is unavailable

Confirm the Docker host can reach `transport.base_url` and that the Android
relay is running. Keep the URL scheme and port. Network routing or firewall
rules between the Docker host and relay must allow the local HTTP connection.

Do not switch to `york_direct` as a workaround. It is unverified research, not
a fallback transport.

## Home Assistant and the physical unit disagree

Stop issuing commands. Record:

- the bridge version;
- Home Assistant state and timestamp;
- physical unit state;
- the bridge log around the event; and
- whether a command repeated.

Restore the last working package/configuration if required. Test one setting at
a time only after polling has recovered.

## Container is unhealthy

Check that:

- `config.yml` exists beside `docker-compose.yml`;
- it is mounted read-only at `/config/config.yml`;
- `qualification-reports/` exists and is writable by the container;
- the MQTT broker and relay are reachable; and
- the log shows no repeated recovery loop.

`healthcheck.py` evaluates the running bridge. The separate
`container_qualification.py --healthcheck` applies only to the network-free CI
qualification command.

## Reports are not present

Compose mounts `./qualification-reports` at `/reports`. Runtime tools may write
below that mount, including `native-probes`, `relay-extraction` and request
hunter output. Generated reports are intentionally untracked. Permissions on
the host directory must allow container writes.

Review reports for device identifiers, addresses and credentials before
sharing them.

## Native protocol tool reports no request candidates

That is the expected qualified result for the current evidence. The observed
library contains 23 state responses and no eligible native request candidate.
Never promote a response to a command or copy it into `state_request_hex`.

## Getting useful support

Include version, deployment platform, redacted configuration, steps to
reproduce and a short relevant log excerpt. Never publish MQTT passwords,
tokens, device MAC addresses, private captures or unredacted relay
initialization records.
