# Sprint 2.3 alpha.5 — Native Debug Configuration

- Added opt-in debug configuration.
- Added disabled-by-default Home Assistant diagnostic entities for native probe and comparison state.
- Relay remains the active transport.
- Native packets are not transmitted unless explicitly enabled and a captured request is configured.
- Existing one-shot `york_capture_probe.py` remains the controlled first native receive-path utility.
