# Climate Bridge release-control checklist

This record is not authority to merge, tag, publish, deploy, or change settings.
Release verification and publication are manual-only; pushing a tag does not
invoke `.github/workflows/release.yml`.

## Accepted source controls

- [x] `VERSION`, `version.py`, V1 guidance, and native example identify 1.0.0.
- [x] Current runtime has no Android relay dependency.
- [x] Stage 2 testing and evidence controls are accepted on `main`.
- [x] `Phase 6 Qualification` preserves push-to-main, pull-request, and manual
  triggers plus its existing safe offline and network-free container gates.
- [x] Release verification and publication require one deliberate manual
  dispatch with `PUBLISH <tag>` confirmation.
- [x] Repository permission is read-only except for the publication job.

## Candidate and tag prerequisites

- [ ] Damien approved the exact candidate, version, full commit SHA, and scope.
- [ ] The candidate revision is accepted on `origin/main`.
- [ ] Damien separately approved creation of the exact immutable tag.
- [ ] The existing tag resolves to the approved SHA and agrees exactly with
  `VERSION` and `version.py`.
- [ ] The candidate-specific QR record is committed to `main`, contains no
  required placeholders, identifies the tag/version/SHA, and selects exactly
  `Qualified` while leaving both other decisions unselected.
- [ ] No GitHub release exists for the tag.

## Manual verification and publication

- [ ] Damien separately approved publication for the exact qualified tag.
- [ ] The operator selected the workflow on `main`, entered the full SHA,
  committed QR path, and exact confirmation `PUBLISH <tag>`.
- [ ] Full-history identity, main reachability, version, release verifier,
  example configuration, complete tests, decoder, clean-tree, clean-image, and
  network-free container gates passed.
- [ ] The sanitized archive excludes `.github`, governance, tests, controlled
  evidence/qualification records, reports, screenshots, and development-only
  material.
- [ ] SHA-256 passed before upload and after download.
- [ ] The publication job reconfirmed the existing tag and absent release, then
  created a new release without creating/moving a tag or updating a release.

## Post-publication and deployment separation

- [ ] Release URL, tag/SHA, title/state, asset names, downloaded checksum,
  workflow run, limitations, and approval reference were independently recorded.
- [ ] Deployment remains unperformed until separately approved for a named
  environment with rollback and operator controls.
- [ ] Handover states exact identities, checks/unrun checks, risks, evidence,
  owner, pending decision, and next permitted action.

The existing `v3.0.0` tag/release does not agree with accepted source version
1.0.0. Stage 3 does not test, edit, delete, replace, or align it.

## Superseded historical gate wording

The following unchecked wording is retained solely for the Phase 12 evidence
contract. Phase 12 is completed; these lines are not current status or authority:

- [ ] Phase 12 reconciliation closeout has passed.
- [ ] Any tag or release publication has separate approval.
