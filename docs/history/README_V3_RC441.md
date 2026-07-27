# York Hybrid Bridge v3.0 RC4.4.1

RC4.4.1 is the final polish update for command and activity integrity.

## Changes

- Removes the old `Last state change` entity from Home Assistant discovery.
- Recreates it as `Last state change timestamp`, a diagnostic entity disabled by default.
  This keeps the timestamp available without cluttering the York AC2 Activity timeline.
- Keeps meaningful AC activity entities enabled: power, target temperature, operating mode, fan mode, swing mode, and Last AC event.
- Confirms `deferred` and `not_applicable` commands are excluded from command-failure and success-rate calculations.
- Preserves the RC4.4 deferred-temperature behaviour and applies the selected setpoint on the next power-on command.
- No changes to the tablet relay protocol, MQTT command path, recovery engine, or health calculations.

## Expected result

The York AC2 Activity panel should now focus on meaningful changes rather than timestamp entries.

The hidden timestamp can be enabled manually from the York AC2 entity list if it is ever needed.
