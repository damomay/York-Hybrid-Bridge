# Release Qualification: `<version and candidate>`

> This record evaluates one exact candidate. It does not authorize merge, tag creation, publication, deployment, or repository-control changes.

## Record control and exact candidate

| Field | Value |
| --- | --- |
| Qualification ID / status | `<QR-vX.Y.Z-candidate>` / `Draft` |
| Target release / candidate | `<version / candidate identifier>` |
| Exact existing tag | `<tag>` |
| Qualification route | `<Independent / Sole-maintainer exception>` |
| Accountable maintainer / qualification reviewer | `<names or pending>` |
| Development / test planning / readiness approval / physical operation / evidence collection / result assessment / qualification assessment / publication approval roles | `<name or pending for each applicable role>` |
| Role-overlap disclosure | `<shared roles or none>` |
| Opened / decision date | `<dates>` |
| Evidence reviewed for qualification | `<references>` |
| Release issue / PR | `<references>` |
| Repository / full commit SHA | `damomay/York-Hybrid-Bridge` / `<40-char SHA>` |
| Source branch / reported version | `<values>` |
| Package/image identity + SHA-256/digest | `<immutable identity>` |
| Configuration schema / qualification-plan revision | `<references>` |
| Rollback boundary | `<exact boundary and separately approved action required>` |

Candidate-changing code, configuration behaviour, dependency, or packaging
changes require a new record unless an approved impact assessment explicitly
preserves unaffected evidence.

## Scope, entry criteria, and limitations

Included: `<scope>`

Excluded: `<scope>`

Known limitations: `<limitations or none>`

Omissions or contradictions: `<values or none>`

Reduced-assurance disclosure: `<required for the sole-maintainer route; otherwise not applicable>`

- [ ] Scope is frozen and candidate identity is complete and consistent.
- [ ] Version identifiers and required automated workflows agree and pass.
- [ ] Required physical plans are `Ready` for this candidate or have an approved equivalence assessment.
- [ ] No unresolved safety-critical defect affects the candidate.
- [ ] Required private evidence storage is available.
- [ ] Independent review is used, or every sole-maintainer exception condition is expressly satisfied and documented.

## Qualification matrices

| Automated requirement | Check | Candidate commit | Result/reference | Required? | Exception approval |
| --- | --- | --- | --- | --- | --- |
| `<requirement>` | `<check>` | `<SHA>` | `<result/reference>` | `<yes/no>` | `<reference or none>` |

Only modern results with a completed independent validation or separate
sole-maintainer result assessment may satisfy the physical matrix. The latter
does not claim independent validation and must retain its reduced-assurance and
role-overlap disclosure. Historical evidence may be relied upon only through
the separate provenance and equivalence assessment below.

| Physical requirement | Plan revision | Assessed run ID | Tested SHA/package | Outcome | Evidence complete? | Result assessor / route | Limitations |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `<requirement>` | `<exact ref>` | `<TR ID>` | `<identity>` | `<outcome>` | `<yes/no>` | `<name>` | `<notes>` |

| Stability/recovery requirement | Result/evidence | Duration/conditions | Candidate | Outcome | Notes |
| --- | --- | --- | --- | --- | --- |
| `<requirement>` | `<references>` | `<conditions>` | `<identity>` | `<outcome>` | `<notes>` |

## Evidence provenance and historical-equivalence assessment

| Evidence | Physical, historical, or automated | Exact provenance and identity | Applicable conclusion | Limitation, omission, or contradiction |
| --- | --- | --- | --- | --- |
| `<reference>` | `<classification>` | `<opaque reference/hash/commit/workflow>` | `<bounded conclusion>` | `<values or none>` |

Historical evidence must not be rewritten, upgraded, or represented as modern
candidate-specific evidence. If unchanged-source equivalence is used, identify
the compared revisions and paths, establish the candidate's exact relationship
to the historical article, and explain why each retained conclusion remains
applicable. Record all conclusions that cannot be preserved.

Equivalence rationale: `<required when historical evidence is relied upon>`

## Integrity and candidate-change assessment

- [ ] Every accepted run identifies the exact article and resolves to private evidence.
- [ ] Recorded hashes were checked against originals.
- [ ] Sensitive evidence is excluded from Git.
- [ ] Failed/inconclusive runs remain preserved.
- [ ] Physical conclusions remain separate from automated results.

| Change/commit | Affected runs | Classification | Qualification impact | Required action/rationale |
| --- | --- | --- | --- | --- |
| `<change or none>` | `<TR IDs>` | `<runtime/protocol/config/package/docs-only>` | `<none/partial/full>` | `<action>` |

Do not assume a merge commit is equivalent to a physically tested commit.

## Defects and consistency checks

| Defect/deviation | Severity | Scope | Disposition | Approval/reference |
| --- | --- | --- | --- | --- |
| `<ID or none>` | `<severity>` | `<scope>` | `<fixed/accepted/blocking>` | `<reference>` |

Confirm version/runtime reporting, documentation, proposed tag/package names,
immutable checksums, install/rollback instructions, exclusion of raw evidence,
automated checks on the exact candidate, properly assessed physical matrix, and
accurate limitations.

## Qualification review route

- [ ] **Independent (preferred)** — identify the independent reviewer and evidence reviewed.
- [ ] **Sole-maintainer exception** — confirm the project is genuinely sole-maintained, no suitable independent reviewer is reasonably available, indefinite delay would prevent an otherwise supportable release, the exception was deliberately selected, all required objective evidence/identity/limitation/rollback information is available, and the accountable maintainer accepts reduced assurance.

For the exception, list the shared roles, state the reduced independence and
assurance, and record the accountable maintainer's separate, dated assessment
after applicable plan readiness, execution, evidence collection, and result
assessment. Do not use “independent review”, “independent validation”,
“independently verified”, or “independently qualified” for that decision.

## Qualification decision

Select exactly one:

- [ ] **Qualified** — this exact candidate satisfies every required matrix entry and gate.
- [ ] **Not qualified** — a requirement failed or blocker remains.
- [ ] **Qualification incomplete** — evidence, review, or checks are missing/inconclusive.

Rationale / qualified scope / exclusions / accountable reviewer or maintainer /
decision date: `<required values>`

For a sole-maintainer `Qualified` decision, use **Qualified under the
sole-maintainer exception** and state explicitly that the documented evidence is
accepted through that route and the decision does not claim independent
assurance. The exception and this reduced-assurance limitation must remain
visible permanently.

The decision is candidate-specific and is not Damien's separate approval to
merge, tag, publish, change repository controls, or deploy. Record those later
approvals and immutable release identifiers only when separately authorized.
