# Climate Bridge project status

Authoritative `main` contains the accepted Climate Bridge 1.0.0 source and
project controls through Stage 5. GitHub is the software integration, revision,
change, and release-control system. Detailed Stage 5 project-control evidence
is retained outside Git.

The current software release is `v1.0.0`; `v3.0.0` is historical.

| Item | Current accepted state |
| --- | --- |
| Source version | Climate Bridge 1.0.0 (`VERSION` and `version.py`) |
| Current software release | `v1.0.0`, resolving to accepted commit `9eb9b73732ef453d600566ea4c4adb82cac0e6bf` |
| Historical release | `v3.0.0` is retained unchanged as historical identity; it is not the current source/release authority |
| Architecture | One York/TCL TFIAC 20014 unit; Home Assistant over MQTT; authenticated native LAN reads; guarded native command boundary; no Android relay runtime dependency |
| Validated V1 scope | The physically accepted operations recorded in the V1 acceptance evidence |
| Known limitations | One configured York device; no multi-device orchestration; no broader vendor adapter; commands outside the qualified boundary fail closed |
| Stage 4 | Protected pull-request path and required checks validated; `main` and matching `v*` tag identities are protected |
| Stage 5 | WP5.0–WP5.5 accepted; detailed project-control evidence remains outside Git |
| Release controls | Manual dispatch only; verification can be rehearsed without publication; publication remains a separate explicit decision |
| Protocol authority | `protocols/york/` |
| Testing/evidence authority | `docs/TESTING.md` and controlled records under `docs/testing/` |

Existing `v1.0.0` and `v3.0.0` releases predate native GitHub immutable
releases and remain legacy release objects. Neither may be edited, replaced, or
deleted under this status. A future publication requires the native immutable
releases repository setting to be separately approved, enabled, and verified
before the publish operation is authorised.

Historical Alpha, Beta, relay, tablet-removal, reconciliation, and `v3.0.0`
records are evidence, not current operating instructions. Current fetched
`origin/main` remains authoritative.
