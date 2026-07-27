# Sprint 2.8.3 — Relay Command Extraction

## Outcome

Climate Bridge now records the exact HTTP command payload sent to the Android York TFIAC Relay V2 immediately before the POST request, plus the relay response and timing.

## Important boundary

The native York packet is constructed inside the Android relay. This instrumentation captures the bridge-to-relay HTTP layer and may reveal native bytes only if the relay includes them in its response. Direct native extraction still requires Android relay source or runtime instrumentation.

## Reports

`/reports/relay-extraction/`

## Summary command

`python /app/york_relay_extraction_report.py`
