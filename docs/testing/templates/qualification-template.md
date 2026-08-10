# Release Qualification: `<version and candidate>`

> This record evaluates one exact candidate. It does not authorize merge, tag creation, publication, deployment, or repository-control changes.

## Record control and exact candidate

| Field | Value |
| --- | --- |
| Qualification ID / status | `<QR-vX.Y.Z-candidate>` / `Draft` |
| Target release / candidate | `<version / candidate>` |
| Owner / reviewer | `<names or pending>` |
| Opened / decision date | `<dates>` |
| Release issue / PR | `<references>` |
| Repository / full commit SHA | `damomay/York-Hybrid-Bridge` / `<40-char SHA>` |
| Source branch / reported version | `<values>` |
| Package/image identity + SHA-256/digest | `<immutable identity>` |
| Configuration schema / qualification-plan revision | `<references>` |

Candidate-changing code, configuration behaviour, dependency, or packaging
changes require a new record unless an approved impact assessment explicitly
preserves unaffected evidence.

## Scope, entry criteria, and limitations

Included: `<scope>`

Excluded: `<scope>`

Known limitations: `<limitations or none>`

- [ ] Scope is frozen and candidate identity is complete and consistent.
- [ ] Version identifiers and required automated workflows agree and pass.
- [ ] Required physical plans are `Ready` for this candidate or have an approved equivalence assessment.
- [ ] No unresolved safety-critical defect affects the candidate.
- [ ] Required private evidence storage is available.

## Qualification matrices

| Automated requirement | Check | Candidate commit | Result/reference | Required? | Exception approval |
| --- | --- | --- | --- | --- | --- |
| `<requirement>` | `<check>` | `<SHA>` | `<result/reference>` | `<yes/no>` | `<reference or none>` |

Only reviewer-validated test results may satisfy the physical matrix.

| Physical requirement | Plan revision | Validated run ID | Tested SHA/package | Outcome | Evidence complete? | Reviewer | Limitations |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `<requirement>` | `<exact ref>` | `<TR ID>` | `<identity>` | `<outcome>` | `<yes/no>` | `<name>` | `<notes>` |

| Stability/recovery requirement | Result/evidence | Duration/conditions | Candidate | Outcome | Notes |
| --- | --- | --- | --- | --- | --- |
| `<requirement>` | `<references>` | `<conditions>` | `<identity>` | `<outcome>` | `<notes>` |

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
automated checks on the exact candidate, reviewer-validated physical matrix,
and accurate limitations.

## Qualification decision

Select exactly one:

- [ ] **Qualified** — this exact candidate satisfies every required matrix entry and gate.
- [ ] **Not qualified** — a requirement failed or blocker remains.
- [ ] **Qualification incomplete** — evidence, review, or checks are missing/inconclusive.

Rationale / qualified scope / exclusions / reviewer / date: `<required values>`

The decision is candidate-specific and is not Damien's separate approval to
merge, tag, publish, change repository controls, or deploy. Record those later
approvals and immutable release identifiers only when separately authorized.
