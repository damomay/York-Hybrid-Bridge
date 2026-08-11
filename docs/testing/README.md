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
`Awaiting review`; only a later result assessment may select the other three
states. That assessment uses either preferred independent review or the
expressly selected sole-maintainer exception below.
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
2. Have the plan independently reviewed and marked `Ready`, or record a
   separate sole-maintainer readiness approval under the exception below.
3. Identify the exact test article.
4. Perform the physical run within the approved boundaries.
5. Submit the result as `Awaiting review`.
6. After the run, have an independent reviewer or the accountable maintainer in
   a separate sole-maintainer assessment select `Validated`, `Failed`, or
   `Inconclusive`.
7. Preserve failed and inconclusive records.
8. Give every retest a new run ID.
9. Use only validated results to satisfy a qualification matrix.
10. Keep qualification and release publication as separate decisions.

## Control rules

- **Ownership:** the plan owner maintains intent; the operator records facts;
  an independent reviewer preferably controls readiness and result validation;
  and the qualification reviewer controls the candidate decision. Under the
  expressly selected sole-maintainer exception, the accountable maintainer may
  make each of those three decisions only as a separate, dated assessment with
  shared roles and reduced assurance disclosed. Writing a plan does not make it
  `Ready`, and completing a run does not select its result outcome.
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

## Sole-maintainer review and qualification exception

Independent human review remains the preferred route for test-plan readiness,
physical-result validation, and candidate qualification. Any of those decisions
may instead use the sole-maintainer exception only when the project is genuinely
operated by one maintainer, no suitable independent reviewer is reasonably
available, indefinite delay would prevent otherwise supportable work or release,
the exception is expressly selected and recorded for that decision, and the
accountable maintainer accepts the reduced assurance. The exception is never
implicit merely because one person performed the work.

Each affected plan, result, or qualification record must identify the people who
performed development, test planning, plan-readiness approval, physical test
operation, evidence collection, result assessment, qualification assessment,
and publication approval where later applicable. Any overlap must be explicit.
Use **Sole-maintainer readiness approval**, **Sole-maintainer result
assessment**, or **Qualified under the sole-maintainer exception** as applicable;
never describe the decision as independent review, independent validation,
independently verified, or independently qualified.

The exception changes who may make a controlled decision, not what that decision
must prove. A readiness assessment remains separate from writing the plan and
must check candidate identity and scope, objectives and acceptance criteria,
prerequisites and starting state, safe operating boundaries, evidence capture,
stop conditions, restoration or rollback, limitations, role overlap, and reduced
assurance. A result assessment remains separate from operating the test and must
compare the exact approved plan and candidate with the recorded steps and
acceptance criteria; separate observations from interpretations; identify
missing, ambiguous, contradictory, or safety-relevant evidence; and preserve
deviations, failures, incomplete steps, and raw-evidence provenance. Missing
evidence never silently passes and acceptance criteria are not weakened.

Candidate qualification remains a separate, dated assessment after applicable
plan readiness, execution, evidence collection, and result assessment. Where
one maintainer performs multiple decisions, each action and date must be
recorded separately; no decision automatically authorizes the next.

Every exception decision requires its applicable objective evidence, exact
identity controls, limitations, contradictions, rollback information, decision
date, accountable person, route selection, evidence reviewed, and rationale.
Qualification additionally retains the exact tag, candidate identifier, full
candidate SHA, version identity, automated results, physical or historical
evidence and provenance, omissions, and any historical-evidence equivalence
rationale. Historical evidence remains labelled with its original limitations;
it is never rewritten as modern candidate-specific physical evidence.
Unchanged-source equivalence must be justified explicitly and only preserves
the conclusions its recorded scope supports.

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
