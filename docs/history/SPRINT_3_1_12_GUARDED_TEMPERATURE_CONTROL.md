# Sprint 3.1.12 — Guarded Whole-Degree Temperature Control

Alpha.41 integrates the physically qualified Heat/High/Vertical whole-degree
temperature generator into normal Home Assistant MQTT control.

## Qualified path

- Power On
- Heat mode
- Fan High
- Swing Vertical
- Display On
- Turbo, Eco and Health Off
- Current and requested setpoints are whole degrees from 16 through 31 °C

The Relay state must match this shape before a direct client is created. A live
direct pre-read must then match all nine decoded fields before the one write is
sent. The post-read must match all nine expected fields.

The earlier Low/Swing Off Heat and Cool temperature path remains available
under its existing guard. No other state shape is broadened.

## Occupied-room safeguard

Heat/23 °C/Fan Low/Swing Vertical is deliberately not treated as equivalent to
the qualified High/Vertical shape. A temperature request from that state stops
before client creation and uses Relay v2 fallback, preserving Fan Low.

## Invariants

- One direct write
- Four UDP sends
- Zero automatic retries
- Exact nine-field pre/post verification
- Relay v2 fallback for every unqualified state or direct-path failure
- No dependency on the operator-run qualification tool
