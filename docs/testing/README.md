# Controlled testing and evidence records

This directory controls test plans, individual run records, release-candidate
qualification, and sanitized evidence metadata. It does not authorize live
testing, broaden a command boundary, or replace the approvals required by
[`AGENTS.md`](../../AGENTS.md).

## Record identities and states

Test plans use `TP-<AREA>-<NNN>-<short-description>.md`. Approved initial areas
are `POWER`, `TEMP`, `MODE`, `FAN`, `SWING`, `STABILITY`, `RECOVERY`, and
`RELEASE`. Plan states are `Planned`, `Ready`, `Superseded`, and `Withdrawn`.
Only an approved plan revision marked `Ready` may authorize a physical run.
Plan approval neither validates a result nor authorizes release activity.

Test runs use `TR-<YYYYMMDD>-<AREA>-<NNN>-<short-sha>-R<run>`; for example,
`TR-20260810-TEMP-001-0874ae2-R1`. Result-review states are `Awaiting review`,
`Validated`, `Failed`, and `Inconclusive`. The operator submits a run as
`Awaiting review`; only the reviewer may select the other three states.
`Retest required` is a follow-up relationship or action, not a replacement
outcome. Every retest receives a new run ID and the earlier record remains.

Legacy migrations use `LR-<VERSION>-<NNN>-<short-description>.md`. They preserve
conclusions already recorded in authoritative historical repository documents;
they do not invent modern metadata or imply that historical evidence met later
requirements. Use explicit values such as `Legacy record — accepted
historically`, `Not recorded`, `Unknown`, `Unavailable in repository evidence`,
and `Not retrospectively verified`. A migrated record must not receive a normal
`TR` identity unless every required modern identity and evidence field is
genuinely available.

Qualifications use `QR-<version>-<candidate>.md`, such as `QR-v1.1.0-rc.1.md`
or `QR-v1.1.0-final.md`. States are `Draft`, `Qualified`, `Not qualified`,
`Qualification incomplete`, and `Superseded`. A qualification applies only to
its exact candidate. It does not authorize merge, tag creation, publication,
deployment, or changes to repository controls.

## Required workflow

1. Draft the plan.
2. Have the plan reviewed and marked `Ready`.
3. Identify the exact test article.
4. Perform the physical run within the approved boundaries.
5. Submit the result as `Awaiting review`.
6. Have the reviewer select `Validated`, `Failed`, or `Inconclusive`.
7. Preserve failed and inconclusive records.
8. Give every retest a new run ID.
9. Use only validated results to satisfy a qualification matrix.
10. Keep qualification and release publication as separate decisions.

## Control rules

- **Ownership:** the plan owner maintains intent; the operator records facts;
  the reviewer independently controls readiness and result validation; the
  qualification reviewer controls the candidate decision. One person must not
  use the operator role to self-validate a result.
- **Revision and supersession:** revise a draft in place only before approval.
  After approval, preserve the revision and create a new revision when the
  procedure, identity, acceptance boundary, or safety control changes. Link
  superseding and superseded records in both directions.
- **Immutable history:** never overwrite, delete, or relabel an actual failed,
  stopped, incomplete, or inconclusive attempt because a later run passes.
- **Sensitive data:** raw evidence stays in an approved private location. Git
  contains only sanitized records, opaque references, and SHA-256 values that
  were actually calculated from originals. Follow
  [`EVIDENCE_INDEX.md`](EVIDENCE_INDEX.md).
- **Handover:** record owner, current state, exact revision/candidate, open
  deviations, missing evidence, pending reviewer, and next permitted action.
  Handover does not transfer or imply an approval.
- **Decision separation:** plan approval, result validation, release
  qualification, merge approval, tag approval, publication approval, and
  deployment approval are distinct decisions and must be recorded separately.

## Sole-maintainer qualification exception

Independent qualification review remains the preferred route. A qualification
may instead use the sole-maintainer exception only when the project is genuinely
operated by one maintainer, no suitable independent qualification reviewer is
reasonably available, indefinite delay would prevent an otherwise supportable
release, and the exception is expressly selected in the permanent qualification
record. The exception is never implicit.

The record must identify every role performed by the same person, including
development, test planning, physical test operation, evidence collection, and
qualification approval. It must describe the decision as a **sole-maintainer
qualification exception**, never as independent review, independent validation,
or independent qualification. A `Qualified` decision under this route accepts
the documented evidence with reduced assurance; it does not claim independent
assurance.

The exception changes only who may make the separate candidate-specific
qualification decision. It does not turn test operation into qualification,
waive independent validation required for a modern physical result, or upgrade
historical evidence. After evidence collection is complete, the accountable
maintainer must perform and date a deliberate qualification assessment distinct
from test operation.

Every exception record must retain the exact tag, candidate identifier, full
candidate SHA, version identity, applicable automated results, applicable
physical or historical evidence and provenance, limitations, omissions and
contradictions, any historical-evidence equivalence rationale, rollback
boundary, decision date, and accountable maintainer identity. Historical
evidence remains labelled with its original limitations; unchanged-source
equivalence must be justified explicitly and only preserves the conclusions its
recorded scope supports.

The available decisions remain `Qualified`, `Not qualified`, and
`Qualification incomplete`. None authorizes tag approval or creation, release
publication approval, workflow dispatch, deployment approval, or a
repository-control change. All existing fail-closed release controls continue
to apply.

## Navigation

- [Test-plan template](templates/test-plan-template.md)
- [Test-result template](templates/test-result-template.md)
- [Qualification template](templates/qualification-template.md)
- [Sanitized evidence index](EVIDENCE_INDEX.md)
- [Results](results/README.md) and [legacy results](results/legacy/README.md)
- [Qualifications](qualifications/README.md)
