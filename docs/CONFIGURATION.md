# Configuration

This reference describes Climate Bridge `1.0.0-alpha.20`.

Start from the committed example:

```bash
cp config.example.yml config.yml
python -c "from pathlib import Path; from validate_config import validate; print('Transport:', validate(Path('config.yml')))"
```

`config.yml` is ignored by Git and should contain the deployment-specific
values. Do not commit MQTT credentials, device addresses, capture secrets or
private logs.

## `transport`

| Key | Required/default | Meaning |
| --- | --- | --- |
| `type` | default `relay` | Use `relay`. `tablet_relay` is a compatibility alias. `york`/`york_direct` are guarded research modes. |
| `base_url` | required in relay mode | Android relay URL including `http://` or `https://`; trailing `/` is removed. |
| `timeout_seconds` | `10` (`12` in example) | HTTP timeout; minimum 0.1 seconds. |
| `poll_seconds` | `5` | State poll interval; minimum 0.1 seconds. |
| `command_retries` | `2` | Retry count; minimum 0. |
| `retry_delay_seconds` | `1` | Delay between retries; minimum 0 seconds. |
| `offline_after_failures` | `3` | Consecutive failures before unavailable state; minimum 1. |

The legacy top-level `relay:` mapping is accepted, but new configurations
should use `transport:`.

## `direct_device`

This section exists for guarded York-direct research. Keep `enabled: false`
during normal operation.

`host`, `mac`, `port`, `connect_timeout_seconds` and `state_request_hex` do not
make direct control safe. Startup validation rejects direct mode unless it is
explicitly enabled and a complete request is configured. The evidence library
currently contains no verified, transmit-safe native request, so enabling this
mode is unsupported.

## `mqtt`

| Key | Required/default | Meaning |
| --- | --- | --- |
| `host` | required | MQTT broker hostname or address. |
| `port` | `1883` | MQTT broker port. |
| `username` | empty | Optional username. |
| `password` | empty | Optional password; an intentional empty password is preserved. |
| `base_topic` | `york/ac2` | Root topic for this device; trailing `/` is removed. |
| `discovery_prefix` | `homeassistant` | Home Assistant MQTT Discovery prefix. |
| `client_id` | `york-ac2-hybrid-bridge` | MQTT client identifier. |
| `discovery_refresh_seconds` | `300` | Discovery republish interval; 0 disables periodic refresh. |
| `reconnect_min_seconds` | `1` | Minimum reconnect delay. |
| `reconnect_max_seconds` | `60` | Maximum reconnect delay; never lower than the minimum. |
| `startup_connect_timeout_seconds` | `30` | Startup broker wait; minimum 5 seconds. |

Leave both credentials empty only when anonymous broker connections are
allowed. Use a distinct base topic and client ID for every future device; the
current runtime still operates only one configured device.

## `device`

`name` is the Home Assistant York device name. `unique_id` anchors its entity
identifiers. `bridge_name` and `bridge_unique_id` identify the diagnostics
device. Treat unique IDs as persistent: changing them creates new entities in
Home Assistant.

## `logging`

`level` accepts `DEBUG`, `INFO`, `WARNING` or `ERROR`. Use `INFO` for normal
operation. Temporary `DEBUG` logging may contain network and state context;
sanitize it before sharing.

## `debug`

All debug switches default to false. `native_compare`, raw-frame publication,
relay extraction and startup probes are engineering functions, not normal
operation. Generated material is written below `capture_directory`
(`/reports/native-probes` by default) and may contain device-specific evidence.
Review and sanitize it before sharing.

## Safe baseline

The committed `config.example.yml` is the authority for the safe alpha.20
shape. At minimum, confirm:

```yaml
transport:
  type: "relay"

direct_device:
  enabled: false

debug:
  enabled: false
  native_compare: false
  publish_raw_frames: false
  relay_extraction: false
  probe_on_startup: false
```
