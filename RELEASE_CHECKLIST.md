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
- [x] Release verification and publication remain manual-dispatch-only.
- [x] `verify_only` requires `VERIFY <tag>` and cannot enter the write-scoped
  publication job.
- [x] `publish` requires separate approval, `PUBLISH <tag>`, and controlled
  release notes at `docs/releases/<tag>.md`.
- [x] Repository permission is read-only except for the publication job.
- [x] Third-party Actions use reviewed full commit SHAs; verification uses the
  recorded Python, pip, and pytest versions.

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
- [ ] Native GitHub immutable releases were separately approved, enabled, and
  verified before publication.

## Manual verification and publication

- [ ] Damien separately approved publication for the exact qualified tag.
- [ ] Before publication, an operator successfully rehearsed the exact
  candidate with `verify_only` and `VERIFY <tag>`.
- [ ] The publishing operator selected the workflow on `main`, chose
  `publish`, entered the full SHA, committed QR and release-notes paths, and
  exact confirmation `PUBLISH <tag>`.
- [ ] Full-history identity, main reachability, version, release verifier,
  example configuration, complete tests, decoder, clean-tree, clean-image, and
  network-free container gates passed.
- [ ] Two independent deterministic builds of the sanitized archive were
  byte-identical; its inventory exactly matched the selected Git tree after
  exclusions.
- [ ] SHA-256 passed before upload and after download.
- [ ] The publication job reconfirmed the existing tag and absent release, then
  created a new release without creating/moving a tag or updating a release.
- [ ] The published body exactly matched the controlled notes and GitHub
  reported the new release as immutable.

## Post-publication and deployment separation

- [ ] Release URL, tag/SHA, title/state, asset names, downloaded checksum,
  workflow run, limitations, and approval reference were independently recorded.
- [ ] Deployment remains unperformed until separately approved for a named
  environment with rollback and operator controls.
- [ ] Handover states exact identities, checks/unrun checks, risks, evidence,
  owner, pending decision, and next permitted action.

The current software release is `v1.0.0`. The existing `v3.0.0` tag/release
is retained unchanged as a historical identity and is not aligned, edited,
deleted, or replaced by this process.

## Superseded historical gate wording

The following unchecked wording is retained solely for the Phase 12 evidence
contract. Phase 12 is completed; these lines are not current status or authority:

- [ ] Phase 12 reconciliation closeout has passed.
- [ ] Any tag or release publication has separate approval.
