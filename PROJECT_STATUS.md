# Climate Bridge project status

Stage 1 project-control work is completed. Its closeout is merged through pull
request #7 at `4f47e91240506259e26b9b6dae122bf95a2947df`.

Stage 2 testing and evidence control is completed and merged through pull
request #8 at `3b3afd97060a13663f28c338d16d42d9c6d716e6`.

| Item | Current accepted state |
| --- | --- |
| Version | Climate Bridge 1.0.0 (`VERSION` and `version.py`) |
| Architecture | One York/TCL TFIAC 20014 unit; Home Assistant over MQTT; authenticated native LAN reads; guarded native command boundary; no Android relay runtime dependency |
| Validated V1 scope | Authoritative state plus the physically accepted Power, Cool, Heat, temperature, Fan Low/High, swing, and restricted mode-loop operations recorded in the V1 acceptance evidence |
| Known limitations | One configured York device; no multi-device orchestration; no broader vendor adapter; commands outside the qualified boundary fail closed |
| Release/tag mismatch | Source identifies 1.0.0, while the current published GitHub tag/release is `v3.0.0` / “York Hybrid Bridge v3.0.0” |
| Governance stage | Stages 1 and 2 are complete. Stage 2 testing and evidence control is merged through pull request #8 at `3b3afd97060a13663f28c338d16d42d9c6d716e6`. Stage 3 has not started. |
| Active blockers/decisions | Stage 3 requires scope review and Damien's explicit approval before work begins. Tag/release alignment also requires Damien's explicit approval. |
| Protocol authority | `protocols/york/` for schemas, packet documentation, sanitized observations, fixtures, and qualification material |
| Acceptance authority | `docs/history/V1_0_0_ACCEPTANCE_AND_STABILITY_EVIDENCE.md` and `docs/V1_0_0_RELEASE_AND_UPGRADE_GUIDE.md` |
| Testing/evidence control | Controlled templates, lifecycle policy, sanitized evidence index, and record directories are under `docs/testing/`. The final V1 acceptance summary has one sanitized legacy migration record. No raw evidence was imported and no retrospective V1 qualification was created. |
| Next permitted action | Review the Stage 3 scope and obtain explicit approval before beginning Stage 3. |

Historical Alpha, Beta, relay, tablet-removal, and reconciliation records explain
how V1 was reached. They are evidence, not current operating instructions.
