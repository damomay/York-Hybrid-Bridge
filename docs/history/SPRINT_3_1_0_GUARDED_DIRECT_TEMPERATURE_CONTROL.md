# Sprint 3.1.0 — Guarded Direct Temperature Control

Alpha.29 introduces the first normal Climate Bridge command path that can use
the qualified York LAN temperature generator.

## Boundary

- Disabled by default.
- Relay v2 remains the configured state and fallback transport.
- Only a temperature-only MQTT command is eligible.
- Power, mode, fan, swing, and feature commands always use Relay v2.
- Direct control requires the current relay state and live direct pre-read to
  match all nine qualified fields.
- The qualified shape is On, Heat or Cool, Fan Low, Swing Off, Turbo/Eco/Health
  Off, and Display On.
- Each eligible direct command uses one fresh authenticated session, one
  pre-read, one write, one post-read, and zero retries.
- Any preflight, pre-read, transport, or post-read failure falls back to Relay
  v2.

## Configuration

`direct_control.enabled` remains `false` in `config.example.yml`. Enabling it
also requires `direct_read.enabled: true` and
`direct_control.fallback_to_relay: true`.

## Deliberate exclusions

This sprint does not make York Direct the primary transport and does not
generate commands that preserve arbitrary fan, swing, display, or feature
states. Those remain later qualification stages.
