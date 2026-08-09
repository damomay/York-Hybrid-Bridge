# Sprint 3.1.9 — Guarded Running Mode Control

Climate Bridge 1.0.0-alpha.38 integrates the two running mode transitions
physically qualified in Alpha.37 into normal Home Assistant MQTT control:

- Heat to Cool
- Cool to Heat

Both transitions reuse the exact captured 31-byte target-state frames already
qualified for Power On + Cool and Power On + Heat. No packet is inferred or
generated.

## Guarded execution

Each eligible request requires:

- the exact nine-field Relay v2 starting state;
- the same exact nine-field direct LAN pre-read;
- one captured direct write;
- zero automatic direct retries; and
- an exact nine-field direct post-read.

The Power On and running-mode cases share target frames and MQTT request shapes,
but remain distinct through the required starting power and mode state.

## Fallback boundary

If the Relay state or direct pre-read is outside the qualified shape, the
direct path stops. When `direct_control.fallback_to_relay` is enabled, Climate
Bridge records the reason and sends the original command through Relay v2.

Fan, swing, features, pending-temperature power-on requests, and every other
unqualified command remain on Relay v2.
