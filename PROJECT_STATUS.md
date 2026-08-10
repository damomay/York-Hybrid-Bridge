# Climate Bridge project status

Stages 1 and 2 are completed on authoritative `main`. Stage 3 GitHub workflow
and release-control hardening is implemented on its dedicated branch and awaits
pull-request review and merge.

| Item | Current accepted state |
| --- | --- |
| Version | Climate Bridge 1.0.0 (`VERSION` and `version.py`) |
| Architecture | One York/TCL TFIAC 20014 unit; Home Assistant over MQTT; authenticated native LAN reads; guarded native command boundary; no Android relay runtime dependency |
| Validated V1 scope | The physically accepted operations recorded in the V1 acceptance evidence |
| Known limitations | One configured York device; no multi-device orchestration; no broader vendor adapter; commands outside the qualified boundary fail closed |
| Release/tag mismatch | Source identifies 1.0.0; the existing published GitHub tag/release is `v3.0.0` / “York Hybrid Bridge v3.0.0” |
| Governance stage | Stage 2 merged through pull request #9 at `8fb4d740b0f1378029095efa7c3d18247ebe7a67`; Stage 3 awaits review and merge |
| GitHub/release controls | Stage 3 separates offline checks, physical qualification, immutable tag verification, and manual publication; tag push cannot publish a release |
| Repository settings observed during Stage 3 preflight | `main` was not protected and no repository rulesets were configured; Stage 3 does not change settings |
| Protocol authority | `protocols/york/` |
| Testing/evidence authority | `docs/TESTING.md` and controlled records under `docs/testing/` |
| Next permitted action | Review the Stage 3 pull request; do not merge, align tags/releases, begin Stage 4, or develop features without separate approval |

Historical Alpha, Beta, relay, tablet-removal, and reconciliation records are
evidence, not current operating instructions. Current fetched GitHub `main`
remains authoritative.
