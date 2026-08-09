# Sprint 3.1.52 — Qualified Mode Loop Consolidation

Alpha.81 consolidates the five physically verified official-SDK mode edges
from Alpha.75 and Alpha.77–80 into one normal mode-control path. It introduces
no new packet, source shape, target shape or transition.

## Qualified loop

| Source | Target | Source fields | Result fields | Physical result |
| --- | --- | ---: | ---: | --- |
| Dry | Fan-only | 8 | 8 | On; Fan Auto; Swing Off |
| Fan-only | Heat 23 °C | 8 | 9 | On; display 23 °C; louvers stationary |
| Heat 23 °C | Auto/FEEL | 9 | 9 | On; dynamic 21 °C observed; louvers stationary |
| Auto/FEEL 21 °C | Cool 21 °C | 9 | 9 | On; display 21 °C; louvers stationary |
| Cool 21 °C | Dry | 9 | 8 | On; Dry internal display 16 °C; louvers stationary |

## Runtime changes

- One immutable `official_sdk_mode_transitions` registry owns all five frames,
  source guards, targets and field-applicability rules.
- One manager selector admits only an exact registered source/request pair.
- One encrypted transport allowlist and packet builder handles every edge.
- The Alpha.67–72 legacy matrix, retired unsafe Fan-only packet and five
  one-release qualification modules are absent from the deployment package.
- Delayed read-only verification remains 30 seconds with 5-second polling.
- Each transaction performs one control write, zero automatic retries and no
  fallback. An unexpected Power Off remains an immediate critical failure.

## Qualification summary

- Native Probes: five official-SDK offline frames, all 31 bytes and XOR-clean.
- Successful Replies: Alpha.75 and Alpha.77–80 live tests completed the loop.
- Relay Matches: source/target fields match the recorded SDK captures.
- Mismatches: none in the completed live loop; retired frames remain blocked.
- Confidence: high for the exact five registered edges only.
- Readiness: ready for grouped Alpha.81 acceptance testing; not yet a beta.
