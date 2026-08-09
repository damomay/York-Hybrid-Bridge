# Climate Bridge project status

Stage 1 project-control work is completed and merged through pull request #6.
The Stage 1 merge commit is
`97e253603f9f507699ca8eb6e53bb24902a84c4f`.

| Item | Current accepted state |
| --- | --- |
| Version | Climate Bridge 1.0.0 (`VERSION` and `version.py`) |
| Architecture | One York/TCL TFIAC 20014 unit; Home Assistant over MQTT; authenticated native LAN reads; guarded native command boundary; no Android relay runtime dependency |
| Validated V1 scope | Authoritative state plus the physically accepted Power, Cool, Heat, temperature, Fan Low/High, swing, and restricted mode-loop operations recorded in the V1 acceptance evidence |
| Known limitations | One configured York device; no multi-device orchestration; no broader vendor adapter; commands outside the qualified boundary fail closed |
| Release/tag mismatch | Source identifies 1.0.0, while the current published GitHub tag/release is `v3.0.0` / “York Hybrid Bridge v3.0.0” |
| Governance stage | Stage 1 is complete. Stage 2 Step 1 has been drafted outside the repository but has not been implemented or approved for GitHub. |
| Active blockers/decisions | Provisional Stage 2 Step 1 templates require review against the merged Stage 1 governance documents. Later Stage 2 steps remain prohibited until separately approved. Tag/release alignment also requires Damien's explicit approval. |
| Protocol authority | `protocols/york/` for schemas, packet documentation, sanitized observations, fixtures, and qualification material |
| Acceptance authority | `docs/history/V1_0_0_ACCEPTANCE_AND_STABILITY_EVIDENCE.md` and `docs/V1_0_0_RELEASE_AND_UPGRADE_GUIDE.md` |
| Next permitted action | Review the provisional Stage 2 Step 1 templates against the merged Stage 1 governance documents. Do not implement or publish them, or begin later Stage 2 steps, without the required separate approval. |

Historical Alpha, Beta, relay, tablet-removal, and reconciliation records explain
how V1 was reached. They are evidence, not current operating instructions.
