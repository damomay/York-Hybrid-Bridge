# Climate Bridge project status

Stages 1 and 2 are accepted on authoritative `main`. The source revision
containing the Stage 3 files includes GitHub contribution, audit, qualification,
and manual-only release-publication controls. This statement is durable on a
topic branch and after merge: determine acceptance by checking whether that
exact revision is reachable from current `origin/main`.

| Item | Current accepted state |
| --- | --- |
| Version | Climate Bridge 1.0.0 (`VERSION` and `version.py`) |
| Architecture | One York/TCL TFIAC 20014 unit; Home Assistant over MQTT; authenticated native LAN reads; guarded native command boundary; no Android relay runtime dependency |
| Validated V1 scope | The physically accepted operations recorded in the V1 acceptance evidence |
| Known limitations | One configured York device; no multi-device orchestration; no broader vendor adapter; commands outside the qualified boundary fail closed |
| Release/tag mismatch | Source identifies 1.0.0; the existing published GitHub tag/release is `v3.0.0` / “York Hybrid Bridge v3.0.0” |
| Stage 2 authority | Pull request #9 at `8fb4d740b0f1378029095efa7c3d18247ebe7a67` |
| Stage 3 controls in this source revision | Templates separate offline and physical work; `Phase 6 Qualification` preserves the network-free gate; release verification/publication are workflow-dispatch-only and fail closed for one existing qualified tag |
| Hosted controls observed 2026-08-10 | `main` unprotected; no rulesets or environments; detailed read-only audit in `docs/GITHUB_CONTROLS.md`; no setting changed by Stage 3 |
| Protocol authority | `protocols/york/` |
| Testing/evidence authority | `docs/TESTING.md` and controlled records under `docs/testing/` |

If this revision is not reachable from current `origin/main`, the next permitted
action is review of its pull request; merge still requires Damien's separate
approval. If it is reachable from `origin/main`, Stage 3 source controls are
accepted and the next action is only a separately approved later-stage or
candidate-planning decision. In neither case may this text authorize Stage 4,
feature development, tag/release alignment, deployment, or repository settings.

Historical Alpha, Beta, relay, tablet-removal, and reconciliation records are
evidence, not current operating instructions. Current fetched `origin/main`
remains authoritative.
