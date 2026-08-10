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
3. **Test-plan readiness:** approve the exact plan revision as `Ready`.
4. **Result validation:** an independent reviewer validates each run; the
   operator cannot self-validate it.
5. **Candidate-specific qualification:** the qualification reviewer selects
   exactly one decision for the exact candidate SHA, version, and identifier.
   Independent review is preferred. When the controlled sole-maintainer
   exception in `docs/testing/README.md` is expressly selected, the accountable
   maintainer may make this separate decision with the permanent record clearly
   disclosing reduced independence and assurance.
6. **Merge approval:** authorize merging the reviewed candidate source.
7. **Tag approval:** authorize one proposed immutable tag for the exact qualified
   candidate SHA; this does not create the tag.
8. **Tag creation:** create and push only the approved tag for that SHA; this
   does not authorize publication or dispatch a workflow.
9. **Publication approval:** authorize publication of the exact existing tag,
   candidate SHA, qualification record, and release identity; this does not
   dispatch the workflow.
10. **Manual publication workflow dispatch:** an authorized operator supplies
    the exact inputs and confirmation `PUBLISH <tag>` using the control revision
    on `main`.
11. **Post-publication verification:** independently verify and record the
    immutable release and downloaded artifacts without deploying them.
12. **Deployment approval, if ever applicable:** separately authorize a named
    installation or operational change with its own rollback controls.

## Required records

- approved scope and review reference;
- full candidate commit SHA, version, existing tag, and source branch;
- approved test plans and immutable test-article identity;
- reviewer-validated result records and sanitized evidence references;
- one `QR-<version>-<candidate>.md` record under
  `docs/testing/qualifications/`, committed after candidate tagging in the
  control revision on `main`, with the exact version, candidate identifier, and
  tagged candidate full commit SHA;
- the qualification route, accountable decision-maker, shared-role disclosure,
  evidence provenance, limitations/omissions/contradictions, applicable
  historical-equivalence rationale, rollback boundary, and decision date;
- separate merge, tag, publication, and deployment approval references;
- workflow run URL, archive identity, SHA-256, release URL, limitations, and
  handover record after publication.

Raw logs, captures, configurations, device identifiers, network addresses,
credentials, tokens, and private evidence remain outside Git. Store only
necessary sanitized facts, opaque references, and hashes calculated from the
originals.

A sole-maintainer qualification does not make an operator's modern result
independently validated and must not describe the candidate as independently
reviewed, independently validated, or independently qualified. It cannot
upgrade historical evidence or bypass any identity, evidence, tag, publication,
workflow, checksum, or existing-release control below. A sole-maintainer
`Qualified` decision means only that the documented evidence was accepted under
the recorded reduced-assurance exception.

## Operator checklist before manual dispatch

- [ ] Use the exact workflow/control revision on `main`; do not select another
  branch, and retain its immutable workflow `github.sha`.
- [ ] Re-fetch `origin/main`, tags, and releases; read the qualification record
  only from the immutable workflow control SHA, never moving `origin/main`.
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
qualification decisions and placeholders, absence of an existing release,
`release_verifier.py`, example configuration, the full safe offline suite, and
the existing network-free container gate.

It builds a sanitized archive that excludes `.github`, governance, tests,
controlled evidence and qualification material, reports, screenshots, and
other non-release paths. It verifies the SHA-256 before uploading. Only after
all verification passes does the write-scoped publication job download the
exact artifact, verify the checksum again, reconfirm the tag and absent release,
and create a new release with `gh release create --verify-tag`. It cannot update
an existing release or create/move a tag.

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
SHA-256, workflow run, qualification record, limitations, and publication
approval. Stop if GitHub state differs from the recorded candidate. Any
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

The current `v3.0.0` mismatch remains unresolved. This process neither begins
nor authorizes tag/release alignment.
