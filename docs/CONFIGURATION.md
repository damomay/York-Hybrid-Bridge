# Configuration

This reference describes Climate Bridge 1.0.0. Start with
`config.example.yml`; it is the committed native configuration example.

```bash
cp config.example.yml config.yml
python -c "from pathlib import Path; from validate_config import validate; print('Transport:', validate(Path('config.yml')))"
```

Keep `config.yml` untracked. Replace all documentation-only addresses and
identifiers, and never commit MQTT credentials, device details, captures, or
private logs.

## Current native baseline

- `transport.type` is `native`. Legacy relay names are compatibility inputs
  that the factory redirects to the native runtime; they do not enable an
  Android relay.
- `direct_read.enabled` must be true for the native runtime. `host`, `mac`,
  `port`, timeouts, and polling values identify the qualified York module.
- `direct_control.enabled` and `power_enabled` are independent guarded-control
  switches and default to false in the example. Enabling them does not widen
  the physically qualified V1 command boundary.
- `mqtt` configures broker access, the Home Assistant discovery prefix, and a
  device-specific base topic.
- `device.name` and `device.unique_id` identify the single supported unit.
- `logging.level` should normally remain `INFO`.

## Debugging and evidence

Debug switches default to false. Raw-frame publication, probes, and capture
output are engineering functions and can disclose device-specific information.
Use them only within an approved evidence activity and sanitize results before
sharing. A packaged tool or option is not permission to transmit or conduct a
live-device test.

Run `validate_config.py` after every configuration change. The V1 release and
upgrade guide contains the deployment sequence and rollback boundary.
