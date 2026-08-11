# Release Qualification: `v1.0.0 / main-9eb9b737`

> This record evaluates one exact candidate. It does not authorize merge, tag creation, publication, deployment, or repository-control changes.

## Record control and exact candidate

| Field | Value |
| --- | --- |
| Qualification ID / status | `QR-v1.0.0-main-9eb9b737` / `Qualified` |
| Target release / candidate | v1.0.0 / main-9eb9b737 |
| Exact existing tag | `v1.0.0` |
| Qualification route | `Sole-maintainer exception` |
| Accountable maintainer / qualification reviewer | Damien May / Damien May |
| Development / test planning / readiness approval / physical operation / evidence collection / result assessment / qualification assessment / publication approval roles | Development and project direction: Damien May; test planning: historical role not separately recorded; readiness approval: approved unchanged-runtime equivalence assessment by Damien May on 2026-08-11; physical operation: Damien May historically, with exact run metadata not recorded; evidence collection and acceptance reporting: Damien May historically; result assessment: sole-maintainer evidence and equivalence assessment by Damien May on 2026-08-11; qualification assessment: Damien May on 2026-08-11; publication approval: pending and not granted |
| Role-overlap disclosure | Damien May is project owner and sole maintainer and performed overlapping development, historical physical-test operation, evidence collection and acceptance reporting, equivalence assessment, and qualification approval roles. No independent reviewer or validator participated. |
| Opened / decision date | 2026-08-11 / 2026-08-11 (Australia/Melbourne) |
| Evidence reviewed for qualification | Candidate GitHub `Tests` run 31378990124; candidate `Phase 6 Qualification` run 31378990108; post-policy-merge runs 31487248384 and 31487248465; Stage 2 reconciliation and legacy acceptance records listed below; Git comparison of the exact candidate and Stage 2 baseline |
| Release issue / PR | Candidate and tag approval recorded in the Stage 3.1 control process; sole-maintainer policy merged by PR #11; this qualification decision was expressly approved by Damien May on 2026-08-11 |
| Repository / full commit SHA | `damomay/York-Hybrid-Bridge` / `9eb9b73732ef453d600566ea4c4adb82cac0e6bf` |
| Source branch / reported version | `main` / `1.0.0` |
| Package/image identity + SHA-256/digest | No release package or image has been created. The existing annotated tag object is `d3848e0832967f321586d5f194426cae14b2b171` and resolves to the candidate SHA above. Packaging and checksum creation require later publication approval. |
| Configuration schema / qualification-plan revision | Candidate `config.example.yml` validated as `native`; approved unchanged-runtime equivalence assessment dated 2026-08-11 replaces a new physical-plan revision for this bounded decision |
| Rollback boundary | No release or deployment exists. Stop without publishing if any identity, evidence, or workflow gate disagrees. Do not move or delete the tag. If this assessment is invalidated, preserve this record and use a later control revision to mark the qualification superseded or not qualified; any release correction or deployment requires separate approval. |

Candidate-changing code, configuration behaviour, dependency, or packaging
changes require a new record unless an approved impact assessment explicitly
preserves unaffected evidence.

## Scope, entry criteria, and limitations

Included: the recorded Climate Bridge V1 functional boundary for one York unit,
including the eight-step Home Assistant acceptance sequence, formal 9/9 command
verification reported by the legacy acceptance record, bounded physical
observations, later stable authoritative reads, and the recorded connection and
container stability conclusions. Automated qualification applies to the exact
tagged candidate.

Excluded: independent assurance; a new candidate-specific physical run;
multi-device operation; broader vendor adapters; deployment; behavior outside
the recorded V1 command and safety boundary; publication; and any claim that
legacy evidence meets modern result-record requirements.

Known limitations: no independent reviewer or validator participated. The
historical test date, package identity and hash, commit SHA, configuration
identity, device alias, operator metadata, reviewer, raw-evidence reference, and
evidence checksum were not recorded. Historical originals were unavailable for
Stage 2 migration and were not retrospectively verified. The annotated tag is
unsigned. No modern candidate-specific physical `TR` record exists.

Omissions or contradictions: the omissions above are accepted under the
sole-maintainer exception. No material contradiction was found between the
committed Stage 2 reconciliation, candidate tree, automated results, and bounded
historical conclusion. Older alpha.20 and relay records describe superseded
historical states and are not used to expand this qualification.

Reduced-assurance disclosure: Damien May made this separate qualification
decision as project owner and sole maintainer after reviewing the evidence and
equivalence assessment. Overlapping roles reduce assurance. This decision is
not independent review, independent validation, independent verification, or
independent qualification.

- [x] Scope is frozen and candidate identity is complete and consistent.
- [x] Version identifiers and required automated workflows agree and pass.
- [x] Required physical plans are `Ready` for this candidate or have an approved equivalence assessment.
- [x] No unresolved safety-critical defect affects the candidate.
- [x] Required private evidence storage is available. No new private evidence is required; unavailable historical originals remain an accepted, explicit limitation.
- [x] Independent review is used, or every sole-maintainer exception condition is expressly satisfied and documented.

## Qualification matrices

| Automated requirement | Check | Candidate commit | Result/reference | Required? | Exception approval |
| --- | --- | --- | --- | --- | --- |
| Complete safe offline test gate | GitHub `Tests` | `9eb9b73732ef453d600566ea4c4adb82cac0e6bf` | Success, run 31378990124 | yes | none |
| Static, packaging, clean-tree, and network-free container gate | GitHub `Phase 6 Qualification` | `9eb9b73732ef453d600566ea4c4adb82cac0e6bf` | Success, run 31378990108 | yes | none |
| Accepted Stage 2 offline baseline | Compilation, 773 tests, Phase 6 gate, release verifier, native example validation, and 14/14 decoder fixtures | `0874ae24f8806eb89f08573473867ac4ad5e2177` | Pass, `docs/reconciliation/sprint-3.2.1-v1-source-reconciliation.md` | yes | unchanged-runtime equivalence approved 2026-08-11 |
| Merged sole-maintainer control revision | GitHub `Tests` and `Phase 6 Qualification` | `04372249b6f6c1f4d35cbc3a2efd46a5c69b5113` | Success, runs 31487248384 and 31487248465 | yes | none; control evidence only, not substituted for candidate source |

Only modern results with a completed independent validation or separate
sole-maintainer result assessment may satisfy the physical matrix. The latter
does not claim independent validation and must retain its reduced-assurance and
role-overlap disclosure. Historical evidence may be relied upon only through
the separate provenance and equivalence assessment below.

| Physical requirement | Plan revision | Assessed run ID | Tested SHA/package | Outcome | Evidence complete? | Result assessor / route | Limitations |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Modern candidate-specific physical matrix | No modern plan; approved unchanged-runtime equivalence assessment dated 2026-08-11 | None; legacy evidence is not a `TR` | No modern physical article identity | Not used as modern validation | no | Damien May / Sole-maintainer exception | Historical evidence is evaluated separately below and retains all legacy limitations. |

| Stability/recovery requirement | Result/evidence | Duration/conditions | Candidate | Outcome | Notes |
| --- | --- | --- | --- | --- | --- |
| Recorded connection stability | `docs/testing/results/legacy/LR-V1.0.0-001-final-acceptance-summary.md` | Multiple Alpha.67 through Beta.1 releases reportedly ran overnight for 12–16 hours between tests | Historical Beta.1 article; exact commit and package not recorded | Accepted only through bounded unchanged-runtime equivalence | No raw evidence, checksum, exact dates, or modern validation is available. |
| Current network-free container behavior | GitHub runs 31378990108 and 31487248465 | Clean image build, health, clean shutdown, and network-free qualification | Exact candidate for 31378990108; merged control revision for 31487248465 | passed | Automated container evidence is not physical HVAC evidence. |

## Evidence provenance and historical-equivalence assessment

| Evidence | Physical, historical, or automated | Exact provenance and identity | Applicable conclusion | Limitation, omission, or contradiction |
| --- | --- | --- | --- | --- |
| `docs/history/V1_0_0_ACCEPTANCE_AND_STABILITY_EVIDENCE.md` | historical | Committed historical acceptance summary | Bounded eight-step functional acceptance, reported 9/9 verification, physical observations, later stable reads, and recorded stability | Exact date, article, commit, configuration, operator metadata, reviewer, raw evidence, and checksum not recorded |
| `docs/testing/results/legacy/LR-V1.0.0-001-final-acceptance-summary.md` | historical | Stage 2 sanitized migration of the preceding committed summary | Preserves the historical conclusion and explicitly records missing modern metadata | Not a `TR`; not retrospectively verified; originals unavailable and not hashed |
| `docs/reconciliation/sprint-3.2.1-v1-source-reconciliation.md` | historical control record | Accepted Stage 2 baseline `0874ae24f8806eb89f08573473867ac4ad5e2177` | Establishes the intended Climate Bridge 1.0.0 runtime baseline and 773-test/offline qualification result | This assessment relies on the committed reconciliation record and did not inspect historical ZIP inputs |
| Baseline-to-candidate Git comparison | automated identity assessment | `0874ae24f8806eb89f08573473867ac4ad5e2177` to `9eb9b73732ef453d600566ea4c4adb82cac0e6bf` | No runtime, protocol implementation, configuration, test, dependency, Docker, or version difference; intervening changes are governance, documentation, templates, and workflows | `protocols/york/README.md` changed as documentation; this does not establish new physical behavior |
| Candidate GitHub Actions | automated | Runs 31378990124 and 31378990108 at the exact candidate SHA | Required offline and network-free gates passed on the tagged candidate | Automated evidence cannot replace physical observation |

Historical evidence must not be rewritten, upgraded, or represented as modern
candidate-specific evidence. If unchanged-source equivalence is used, identify
the compared revisions and paths, establish the candidate's exact relationship
to the historical article, and explain why each retained conclusion remains
applicable. Record all conclusions that cannot be preserved.

Equivalence rationale: Stage 2 accepted the reconciled Climate Bridge 1.0.0
runtime at `0874ae24f8806eb89f08573473867ac4ad5e2177`. The tagged candidate at
`9eb9b73732ef453d600566ea4c4adb82cac0e6bf` has no changes from that baseline in
runtime, protocol implementation, configuration, tests, dependencies, Docker,
or version identity. Candidate-specific automated gates passed. The historical
record states that V1.0.0 promotes the accepted Beta.1 runtime with metadata and
documentation changes only. Therefore its bounded functional and stability
conclusions are accepted for this candidate under the sole-maintainer exception,
without converting the legacy record into modern candidate-specific evidence or
preserving conclusions outside its recorded scope.

## Integrity and candidate-change assessment

- [x] Every accepted run identifies the exact article and resolves to private evidence. No modern physical run is accepted or relied upon; legacy evidence is classified and assessed separately.
- [x] Recorded hashes were checked against originals. Git commit/tag identities and GitHub asset identities used here were checked; no unavailable historical hash is claimed.
- [x] Sensitive evidence is excluded from Git.
- [x] Failed/inconclusive runs remain preserved. No modern run was created or relabelled by this assessment.
- [x] Physical conclusions remain separate from automated results.

| Change/commit | Affected runs | Classification | Qualification impact | Required action/rationale |
| --- | --- | --- | --- | --- |
| Stage 2 baseline through candidate `9eb9b73732ef453d600566ea4c4adb82cac0e6bf` | Legacy record only; no modern `TR` | Governance, documentation, templates, and workflows only; executable candidate tree unchanged | bounded historical conclusions preserved with reduced assurance | Record exact comparison, legacy limitations, shared roles, and sole-maintainer approval; require a new assessment for any candidate-changing behavior |
| PR #11 merge `04372249b6f6c1f4d35cbc3a2efd46a5c69b5113` | none | governance documentation and templates only | enables the disclosed sole-maintainer route; does not alter candidate evidence | Keep the control commit separate from the tagged candidate source |

Do not assume a merge commit is equivalent to a physically tested commit.

## Defects and consistency checks

| Defect/deviation | Severity | Scope | Disposition | Approval/reference |
| --- | --- | --- | --- | --- |
| Missing historical identity, provenance, raw evidence, and checksum fields | reduced assurance | historical functional and stability evidence | accepted only as explicit legacy limitations under bounded equivalence | Damien May, 2026-08-11 |
| No independent reviewer or validator | reduced assurance | readiness, result/equivalence assessment, and qualification | accepted under the expressly selected sole-maintainer exception | Damien May, 2026-08-11 |
| No modern candidate-specific physical `TR` | reduced assurance | physical matrix | accepted because executable runtime is unchanged and historical evidence is used only through the documented equivalence assessment | Damien May, 2026-08-11 |
| Unsigned annotated tag | informational | release identity | exact tag object and resolved candidate SHA verified; publication remains separately gated | tag object `d3848e0832967f321586d5f194426cae14b2b171` |

Confirm version/runtime reporting, documentation, proposed tag/package names,
immutable checksums, install/rollback instructions, exclusion of raw evidence,
automated checks on the exact candidate, properly assessed physical matrix, and
accurate limitations.

## Qualification review route

- [ ] **Independent (preferred)** — identify the independent reviewer and evidence reviewed.
- [x] **Sole-maintainer exception** — confirm the project is genuinely sole-maintained, no suitable independent reviewer is reasonably available, indefinite delay would prevent an otherwise supportable release, the exception was deliberately selected, all required objective evidence/identity/limitation/rollback information is available, and the accountable maintainer accepts reduced assurance.

Damien May is the project owner and sole maintainer. No suitable independent
reviewer is reasonably available. Damien May expressly selected this route,
accepted its reduced assurance, disclosed the overlapping roles above, and made
this separate, dated assessment after evidence collection and equivalence
review. This decision is not independent review, independent validation,
independent verification, or independent qualification.

## Qualification decision

Select exactly one:

- [x] **Qualified** — this exact candidate satisfies every required matrix entry and gate.
- [ ] **Not qualified** — a requirement failed or blocker remains.
- [ ] **Qualification incomplete** — evidence, review, or checks are missing/inconclusive.

Rationale / qualified scope / exclusions / accountable reviewer or maintainer /
decision date: **Qualified under the sole-maintainer exception.** The exact
tagged Climate Bridge 1.0.0 candidate is accepted for the bounded V1 functional
and stability scope described above based on unchanged-runtime equivalence,
candidate-specific automated gates, and explicitly limited legacy evidence.
Excluded are independent assurance, new physical validation, broader devices or
adapters, publication, deployment, and behavior outside the recorded boundary.
Accountable maintainer: Damien May. Decision date: 2026-08-11
(Australia/Melbourne).

The documented evidence is accepted through the sole-maintainer exception. This
decision does not claim independent assurance. The exception, shared roles, and
reduced-assurance limitations in this record are permanent.

The decision is candidate-specific and is not Damien's separate approval to
merge, tag, publish, change repository controls, or deploy. Record those later
approvals and immutable release identifiers only when separately authorized.
