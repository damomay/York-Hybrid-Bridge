# Sprint 2.5.3 — Evidence-backed York decoder

This release enables decoding only for fields isolated in recovered Protocol
Explorer captures. It does not enable native command transmission and does not
change the active Relay (Legacy) transport.

Supported status fields:
- power
- mode: auto, cool, dry, fan-only, heat
- fan: low, auto, medium, high
- swing: off, horizontal, vertical, both
- turbo
- eco
- health
- display

Unresolved fields remain unset:
- target temperature
- current temperature
- sleep
- timer and clock data
