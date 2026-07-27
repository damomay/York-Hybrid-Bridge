# York Hybrid Bridge v3.0 RC4.4

RC4.4 improves command and activity integrity without changing the tablet relay transport.

## Changes
- Temperature selected while the AC is off is classified as `deferred`, not failed.
- The deferred setpoint is retained in Home Assistant and included with the next power-on/mode command.
- Deferred and not-applicable requests do not reduce Command success rate or Bridge stability.
- Adds Commands deferred and Commands not applicable diagnostics.
- Adds York AC2 activity sensors for power, target temperature, operating mode, fan mode, swing mode and last AC event.
- `Last state update` is renamed `Last state change` and updates only when the AC state changes, reducing Activity noise.

## Expected off-state behaviour
1. Turn the AC off.
2. Change the Home Assistant temperature dial.
3. Last command result becomes `deferred`.
4. Command failures remains unchanged.
5. Turn the AC on; the selected setpoint is sent with the power-on command.
