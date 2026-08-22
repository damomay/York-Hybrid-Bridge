# Release process

This process is fail-closed and manual-only. It separates twelve decisions that
must not be inferred from one another. A passing check or completed record is
evidence, not approval for a later decision.

## Twelve separately controlled decisions

1. **Candidate selection and scope freeze:** freeze the candidate identifier,
   intended version, included behavior, exclusions, limitations, test boundary,
   and rollback boundary.
2. **Exact commit identification:** record the candidate's full 40-character
   commit SHA; do not use a branch name, moving ref, archive, or later control
   commit as a substitute.
3. **Test-plan readiness:** approve the exact plan revision as `Ready` through
   preferred independent review or a separate, dated sole-maintainer readiness
   approval. Writing the plan does not approve it.
4. **Result validation:** after the operator submits the run, select its outcome
   through preferred independent validation or a separate, dated sole-maintainer
   result assessment. Test completion does not validate the result.
5. **Candidate-specific qualification:** the qualification reviewer selects
   exactly one decision for the exact candidate SHA, version, and identifier.
   Independent review is preferred. When the controlled sole-maintainer
   exception in `docs/testing/README.md` is expressly selected, the accountable
   maintainer may make this separate, dated decision after evidence collection
   and result assessment, with the permanent record clearly disclosing reduced
   independence and assurance.
6. **Merge approval:** authorize merging the reviewed candidate source.
7. **Tag approval:** authorize one proposed immutable tag for the exact qualified
   candidate SHA; this does not create the tag.
8. **Tag creation:** create and push only the approved tag for that SHA; this
   does not authorize publication or dispatch a workflow.
9. **Publication approval:** authorize publication of the exact existing tag,
   candidate SHA, qualification record, and release identity; this does not
   dispatch the workflow.
10. **Manual release workflow dispatch:** first rehearse the exact candidate
    using `verify_only` and `VERIFY <tag>`. A later separately authorized
    operator may select `publish` and supply `PUBLISH <tag>` using the control
    revision on `main`.
11. **Post-publication verification:** independently verify and record the
    immutable release and downloaded artifacts without deploying them.
12. **Deployment approval, if ever applicable:** separately authorize a named
    installation or operational change with its own rollback controls.

## Required records

- approved scope and review reference;
- full candidate commit SHA, version, existing tag, and source branch;
- approved test plans, their review route/date, and immutable test-article identity;
- assessed result records, their review route/date, and sanitized evidence references;
- one `QR-<version>-<candidate>.md` record under
  `docs/testing/qualifications/`, committed after candidate tagging in the
  control revision on `main`, with the exact version, candidate identifier, and
  tagged candidate full commit SHA;
- the qualification route, accountable decision-maker, shared-role disclosure,
  evidence provenance, limitations/omissions/contradictions, applicable
  historical-equivalence rationale, rollback boundary, and decision date;
- separate merge, tag, publication, and deployment approval references;
- reviewed release notes at `docs/releases/<tag>.md`, with the required
  sections and no private evidence;
- workflow run URL, archive identity, SHA-256, release URL, limitations, and
  handover record after publication.

Raw logs, captures, configurations, device identifiers, network addresses,
credentials, tokens, and private evidence remain outside Git. Store only
necessary sanitized facts, opaque references, and hashes calculated from the
originals.

Independent review is preferred at plan readiness, result validation, and
candidate qualification. At each point, the sole-maintainer route requires an
express selection, accountable person, separate decision date, evidence
reviewed, shared-role disclosure, rationale, and reduced-assurance statement.
One decision never performs or authorizes the next.

A sole-maintainer decision must not be described as independently reviewed,
independently validated, independently verified, or independently qualified. It
cannot upgrade historical evidence or bypass any identity, evidence, acceptance,
safety, rollback, tag, publication, workflow, checksum, or existing-release
control below. `Qualified under the sole-maintainer exception` means only that
the documented evidence was accepted through the recorded reduced-assurance
route.

## Operator checklist before manual dispatch

- [ ] Use the exact workflow/control revision on `main`; do not select another
  branch, and retain its immutable workflow `github.sha`.
- [ ] Re-fetch `origin/main`, tags, and releases; read the qualification record
  only from the immutable workflow control SHA, never moving `origin/main`.
- [ ] Select `verify_only` and enter `VERIFY <tag>` when rehearsing. This
  operation has read-only repository permission and cannot run the publication
  job.
- [ ] For `publish`, confirm Damien's separate publication approval identifies
  the exact tag, full SHA, qualification record, controlled release-notes path,
  and release title.
- [ ] Confirm the tag already exists, resolves to the approved SHA, is reachable
  from `origin/main`, and agrees with `VERSION` and `version.py`.
- [ ] For `publish`, confirm no GitHub release exists for the tag and native
  GitHub immutable releases were separately approved, enabled, and verified.
- [ ] Confirm the QR path and filename are candidate-specific, placeholders are
  resolved, the identity rows match, and exactly `Qualified` is selected.
- [ ] For `publish`, confirm `docs/releases/<tag>.md` is present at the
  immutable control SHA, matches the selected tag, contains every required
  section exactly once, and has no placeholder or private evidence.
- [ ] Enter the full 40-character SHA and the confirmation required by the
  selected operation.
- [ ] Do not dispatch merely to test the workflow.

## Manual verification and publication

`Release controls` has only `workflow_dispatch`; pushing a tag never invokes it.
The default `verify_only` operation runs the complete identity, qualification,
test, container, notes (when supplied), and packaging controls without granting
repository write permission. The `publish` job has an explicit operation
condition and is the only job with `contents: write`.
The read-only verification job keeps two identities separate. A control checkout
is pinned to the immutable `github.sha` that supplied the manually dispatched
workflow; that SHA must be reachable from the fetched `origin/main` history and
is propagated to the publication job and artifact identity. The qualification
record is read only from that pinned control checkout. A separate candidate
checkout is pinned to the existing tag;
all source verification, tests, container qualification, and packaging operate
only on that tagged candidate tree.

The job checks full history, immutable tag identity, candidate reachability from
`origin/main`, version agreement, exact QR filename/version/candidate/SHA fields,
qualification decisions and placeholders, and—only when publishing—absence of
an existing release,
`release_verifier.py`, example configuration, the full safe offline suite, and
the existing network-free container gate.

The controlled archive builder reads blobs from the exact candidate Git tree,
sorts paths byte-for-byte, preserves Git file modes, uses a fixed ZIP timestamp
and stored entries, and creates one `Climate-Bridge-vX.Y.Z/` root. It excludes
`.github`, governance (including controlled release notes), tests, controlled
evidence and qualification material,
reports, screenshots, and other non-release paths. Two independent builds must
be byte-identical, the archive inventory must exactly match the selected tree
after exclusions, and SHA-256 must pass before upload.

Release notes are never generated by GitHub. When supplied, the workflow reads
`docs/releases/<tag>.md` only from the pinned control revision, validates the
tag/path and required sections, and carries the exact bytes in the internal
verification artifact. Only after all verification passes may the write-scoped
publication job download the exact artifact, verify the checksum again,
reconfirm the tag and absent release, and create a release using
`gh release create --verify-tag --notes-file`. It cannot update an existing
release or create/move a tag.

Third-party Actions are pinned to reviewed full commit SHAs. The runner is
`ubuntu-24.04`, Python is 3.12.13, pip is 26.2.1, and pytest is 9.1.1. The
workflow records Docker and GitHub CLI versions, the pulled
`python:3.12-alpine` digest, and the resulting image ID. The floating Alpine
base name in the unchanged Dockerfile remains a recorded reproducibility
limitation; the observed digest is evidence for each run, not a source pin.

## Stop conditions

Stop and preserve the failed run on any unexpected command or retry, shallow or
incomplete history, a control SHA that is not the dispatched workflow SHA or is
not reachable from `origin/main`, a qualification record not present at that
control SHA, missing/moved tag, SHA or version disagreement, candidate not
reachable from `origin/main`, invalid QR path/name/version/candidate/content,
unresolved placeholder, non-unique or non-Qualified decision, missing/failed gate,
repository dirtiness, archive exclusion failure, checksum disagreement,
existing release, physical/reported-state disagreement, or absent approval.
Do not weaken a check, mutate a tag/release, or substitute another candidate.

## Post-publication verification

Without deploying, verify and record the immutable release URL, tag and commit,
release title, draft/prerelease state, exactly expected asset names, downloaded
SHA-256, exact controlled release body, workflow run, qualification record,
limitations, and publication approval. The workflow must also confirm that the
GitHub release API reports `immutable: true`. Stop if GitHub state differs from
the recorded candidate. Any
correction, release edit/deletion, tag mutation, replacement candidate, or
rollback requires new explicit approval; do not edit history under this procedure.

## Deployment separation and handover

Release publication does not authorize deployment, Home Assistant changes,
MQTT connection, HVAC commands, network capture, or physical qualification.
Handover must state owner, exact candidate and artifact hashes, approvals,
checks and unrun checks, evidence locations, limitations, deviations, rollback
boundary, pending reviewer/operator, and next permitted action. If the source
revision containing these controls is on `main`, the next action is separately
approved candidate planning; otherwise it is review of that revision.

The current software release is `v1.0.0`. The existing `v3.0.0` release is
retained unchanged as a historical identity. This process neither begins nor
authorizes editing, deleting, replacing, or aligning either legacy release.
