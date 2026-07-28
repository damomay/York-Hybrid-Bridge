# Phase 12 — Reconciliation closeout

Status: IN PROGRESS.

## Purpose

Close the reconciliation record without changing the verified runtime, then
start future work from the reconciled baseline.

## Gate ledger

| Gate | Result | Evidence |
| ---: | --- | --- |
| 0 | PASS | Controlling roadmap: frozen repository and alpha.20 baselines |
| 1 | PASS | Controlling roadmap: Phase 1 manifest SHA-256 and inventory |
| 2 | PASS | `phase-2-shell-preparation.md` |
| 3 | PASS | `phase-3-bounded-integration.md` |
| 4 | PASS | `phase-4-identity-version-configuration.md` |
| 5 | PASS | `phase-5-test-suite.md` |
| 6 | PASS | `phase-6-static-packaging-container.md` |
| 7 | PASS | `phase-7-live-relay-regression.md` |
| 8 | PASS | `phase-8-protocol-evidence-safety.md` |
| 9 | PASS | `phase-9-documentation-release-evidence.md` |
| 10 | PASS | `phase-10-repository-review.md` |
| 11 | PASS | `phase-11-post-merge-verification.md` |
| 12 | IN PROGRESS | This closeout record and final qualification |

## Source-manifest reconciliation

The approved Phase 1 manifest is
`phase1-reconciliation-manifest.md`, SHA-256
`c2668aefb17d672e3c146ccecd43988d09d056b35fd2bda3fc6a7f3fe12c9ed4`.

It classifies:

- all 45 files tracked by polished repository baseline
  `Develop` at `741145f1a2de81f1f338eccf7f2d4af6595510fd`;
- all 244 files in
  `Climate_Bridge_1.0.0-alpha.20_Sprint_2_8_3_Relay_Command_Extraction.zip`,
  SHA-256
  `2d53cc8a01b409433086605c3640d8840975f7663ab516b17676f59864ac17a2`;
- all 18 same-path files, including 16 deliberate merges;
- 84 generated cache or bytecode files assigned omission; and
- eight generated outputs assigned regeneration.

Phase 10 detected and restored the only unexplained manifest gap: 24 approved
historical records and `RELEASE_CHECKLIST.md`. The four-test Phase 10 contract
guards that inventory. No unclassified source remains.

## Final qualification archive

| Area | Final verified result |
| --- | --- |
| Canonical Python gate | 126/126 tests on fresh canonical `main`; forced compilation and clean Git checks passed |
| Phase 12 closeout gate | 131/131 tests, including 5/5 Phase 12 contracts; forced compilation and staged/working-tree diff checks passed |
| Package and identity | Climate Bridge `1.0.0-alpha.20`; relay example; release verifier passed |
| Container | Clean build, network-free health and clean shutdown passed in pull-request CI |
| Live relay | Power, Cool mode, temperature, High fan, Vertical swing and power-off passed on York AC2 |
| Restart recovery | Clean shutdown, MQTT reconnect, 64 discovery entities, READY and synchronised Off state |
| Protocol | 14/14 decoder fixtures; 23 observed state responses; zero eligible or executable native requests |
| Canonical privacy gate | 199 tracked files passed the privacy and generated-material scan |
| Phase 12 privacy gate | 204 staged files passed the privacy and generated-material scan |

## Accepted limitations

- The Android tablet relay remains required.
- The Android application still constructs the native York command.
- Native York direct control remains experimental, guarded, disabled by
  default and without a verified executable request.
- Existing evidence contains 23 state responses and zero eligible native
  request candidates.
- Only one York unit and one relay deployment have been qualified.
- Multiple-device operation has not been implemented or qualified.
- Broader HVAC adapter support remains future work.
- No alpha.20 tag or GitHub release has been created or approved.

## Baseline and repository closure

The reconciled runtime baseline is canonical `main` commit
`137b509b5dadd6459b43f70c5a8295beba477d5c`. Pull request #2 is closed and
merged. The reconciliation feature branch remains preserved until this
closeout change is reviewed and Gate 12 is confirmed.

The next implementation roadmap is
`../roadmaps/tablet-removal.md`. It starts from the reconciled baseline and
keeps tablet removal ahead of multiple-device support.

## Gate decision

The local closeout gate passed 131/131 tests, 14/14 decoder fixtures and the
204-file privacy/generated-material scan. Gate 12 remains in progress until
the bounded documentation change is reviewed on GitHub, the canonical
post-closeout `main` commit is recorded and the obsolete reconciliation
branch is closed.
