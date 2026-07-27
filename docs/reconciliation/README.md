# Reconciliation evidence

This directory records the bounded changes and gate results used to reconcile
the polished York Hybrid Bridge repository with the Climate Bridge
`1.0.0-alpha.20` engineering package.

Each completed phase should record:

- the baseline or commit tested;
- the exact checks and results;
- the files intentionally changed;
- unexpected findings and the resulting decision;
- the gate outcome and approval to advance.

Large raw captures, local configuration, secrets, generated reports, caches,
and compiled files do not belong here. Approved protocol fixtures are added
only through the relevant roadmap phase.

## Published gate record

| Phase | Result | Evidence |
| --- | --- | --- |
| 2 | PASS | `phase-2-shell-preparation.md` |
| 3 | PASS | `phase-3-bounded-integration.md` |
| 4 | PASS | `phase-4-identity-version-configuration.md` |
| 5 | PASS | `phase-5-test-suite.md` |
| 6 | PASS | `phase-6-static-packaging-container.md` |
| 7 | PASS | `phase-7-live-relay-regression.md` |
| 8 | PASS | `phase-8-protocol-evidence-safety.md` |

Phase 9 consolidates the public documentation and pull-request evidence. Later
phases remain governed by the controlling reconciliation roadmap.
