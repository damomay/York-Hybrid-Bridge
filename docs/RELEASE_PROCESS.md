# Release process

This process is fail-closed and manual-only. It separates twelve decisions that
must not be inferred from one another. A passing check or completed record is
evidence, not approval for a later decision.

## Twelve separately controlled decisions

1. **Implementation scope approval:** authorize the bounded source change.
2. **Candidate and version selection:** identify the exact commit, reported
   version, intended tag, scope, limitations, and rollback boundary.
3. **Test-plan readiness:** approve the exact plan revision as `Ready`.
4. **Physical-run authorization:** separately authorize the named device/case,
   operator, observation, stop conditions, and rollback readiness.
5. **Result validation:** an independent reviewer validates each run; the
   operator cannot self-validate it.
6. **Candidate qualification:** the qualification reviewer selects exactly one
   decision for the exact candidate.
7. **Merge approval:** authorize merging the reviewed source revision.
8. **Tag-creation approval:** authorize creation and push of one immutable tag
   for one full commit SHA.
9. **Release-publication approval:** authorize one manual publication dispatch
   for that existing tag and qualified candidate.
10. **Deployment approval:** separately authorize installation or operation in
    a named environment; publication does not grant it.
11. **Repository-control approval:** separately authorize any branch protection,
    ruleset, environment, permission, secret, or setting change.
12. **Post-publication corrective-action approval:** separately authorize any
    release edit/deletion, tag mutation, rollback, replacement candidate, or
    corrective publication.

## Required records

- approved scope and review reference;
- full candidate commit SHA, version, existing tag, and source branch;
- approved test plans and immutable test-article identity;
- reviewer-validated result records and sanitized evidence references;
- one `QR-<tag>-<candidate>.md` record under
  `docs/testing/qualifications/`, committed to `main`, with the exact tag,
  version, and tagged full commit SHA;
- separate merge, tag, publication, and deployment approval references;
- workflow run URL, archive identity, SHA-256, release URL, limitations, and
  handover record after publication.

Raw logs, captures, configurations, device identifiers, network addresses,
credentials, tokens, and private evidence remain outside Git. Store only
necessary sanitized facts, opaque references, and hashes calculated from the
originals.

## Operator checklist before manual dispatch

- [ ] Use the workflow revision on `main`; do not select another branch.
- [ ] Re-fetch `origin/main`, tags, releases, and the qualification record.
- [ ] Confirm Damien's separate publication approval identifies the exact tag,
  full SHA, qualification record, and release title.
- [ ] Confirm the tag already exists, resolves to the approved SHA, is reachable
  from `origin/main`, and agrees with `VERSION` and `version.py`.
- [ ] Confirm no GitHub release exists for the tag.
- [ ] Confirm the QR path and filename are candidate-specific, placeholders are
  resolved, the identity rows match, and exactly `Qualified` is selected.
- [ ] Enter the full 40-character SHA and confirmation `PUBLISH <tag>`.
- [ ] Do not dispatch merely to test the workflow.

## Manual verification and publication

`Release controls` has only `workflow_dispatch`; pushing a tag never invokes it.
The read-only verification job checks full history, immutable tag identity,
`origin/main` reachability, version agreement, qualification integrity, absence
of an existing release, `release_verifier.py`, example configuration, the full
safe offline suite, and the existing network-free container gate.

It builds a sanitized archive that excludes `.github`, governance, tests,
controlled evidence and qualification material, reports, screenshots, and
other non-release paths. It verifies the SHA-256 before uploading. Only after
all verification passes does the write-scoped publication job download the
exact artifact, verify the checksum again, reconfirm the tag and absent release,
and create a new release with `gh release create --verify-tag`. It cannot update
an existing release or create/move a tag.

## Stop conditions

Stop and preserve the failed run on any unexpected command or retry, shallow or
incomplete history, missing/moved tag, SHA or version disagreement, candidate
not reachable from `origin/main`, invalid QR path/name/content, unresolved
placeholder, non-unique or non-Qualified decision, missing/failed gate,
repository dirtiness, archive exclusion failure, checksum disagreement,
existing release, physical/reported-state disagreement, or absent approval.
Do not weaken a check, mutate a tag/release, or substitute another candidate.

## Post-publication verification

Without deploying, verify and record the immutable release URL, tag and commit,
release title, draft/prerelease state, exactly expected asset names, downloaded
SHA-256, workflow run, qualification record, limitations, and publication
approval. Stop if GitHub state differs from the recorded candidate. Correction
or rollback requires decision 12; do not edit history under this procedure.

## Deployment separation and handover

Release publication does not authorize deployment, Home Assistant changes,
MQTT connection, HVAC commands, network capture, or physical qualification.
Handover must state owner, exact candidate and artifact hashes, approvals,
checks and unrun checks, evidence locations, limitations, deviations, rollback
boundary, pending reviewer/operator, and next permitted action. If the source
revision containing these controls is on `main`, the next action is separately
approved candidate planning; otherwise it is review of that revision.

The current `v3.0.0` mismatch remains unresolved. This process neither begins
nor authorizes tag/release alignment.
