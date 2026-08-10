# Climate Bridge release-control checklist

This is a control record, not authority to merge, tag, publish, or deploy.

## Accepted source and controls

- [x] `VERSION`, `version.py`, V1 guidance, and native example identify 1.0.0.
- [x] Current runtime has no Android relay dependency.
- [x] Stage 2 testing and evidence controls are accepted on `main`.
- [x] Tag push and release publication are separate workflow actions.
- [x] Tag-push verification has read-only repository permission.
- [x] Only the deliberate publication job has `contents: write`.

## Candidate and tag decision

- [ ] Damien approved the exact accepted commit and version decision.
- [ ] Damien separately approved creation of the exact immutable tag.
- [ ] The tag resolves to the approved full commit SHA and agrees with source
  version identifiers.
- [ ] The tag-triggered offline candidate verification passed and its sanitized
  results and artifact hashes were recorded.

## Qualification decision

- [ ] A candidate-specific record under `docs/testing/qualifications/` is
  complete and marked `Qualified` by its reviewer.
- [ ] Every physical matrix entry uses reviewer-validated controlled results.
- [ ] Limitations, failed/inconclusive attempts, provenance, and candidate-change
  assessment are accurate and sanitized.

## Publication decision

- [ ] Damien separately approved publication of this exact qualified tag.
- [ ] An authorized operator deliberately selected `publish`, supplied the
  qualification record, and entered `PUBLISH` in the manual workflow.
- [ ] Re-verification passed before the write-enabled publication job ran.
- [ ] Release title, tag, notes, archive, checksum, and accepted source agree.

The existing `v3.0.0` tag/release does not agree with the accepted source
version 1.0.0. Stage 3 neither changes nor tests that release. Follow
`docs/RELEASE_PROCESS.md`; alignment remains separately prohibited until
Damien explicitly approves it.

## Superseded historical gate wording

The following unchecked wording is retained solely for the Phase 12 evidence
contract. Phase 12 is completed; these lines are not current status or authority:

- [ ] Phase 12 reconciliation closeout has passed.
- [ ] Any tag or release publication has separate approval.
