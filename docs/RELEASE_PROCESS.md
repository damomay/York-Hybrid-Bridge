# Release process

This procedure separates accepted source, tag creation, candidate verification,
physical qualification, and publication. Completing one step never authorizes
the next. Tags and releases do not override newer accepted source on `main`.

## 1. Approve and identify the candidate

Start from a reviewed commit on current `main`. Record the full commit SHA,
reported version, scope, limitations, required checks, and rollback boundary.
Version changes, packaging changes, and candidate selection require their own
approved scope. Passing tests is evidence only.

## 2. Create an immutable tag

Damien must explicitly approve tag creation. Confirm the intended existing
commit and tag name before creating or pushing it. Never move, replace, or
delete a tag to correct a candidate; select and approve a new identity instead.

Pushing a `vX.Y.Z` tag starts only the read-only `verify-candidate` job in
`.github/workflows/release.yml`. It cannot publish a GitHub release.

## 3. Verify the exact tagged candidate

The workflow checks out the existing tag, confirms its identity, runs the safe
offline gates, and creates short-lived verification artifacts. It does not run
live HVAC work or prove physical qualification. Record exact workflow results,
artifact hashes, failures, and limitations without raw sensitive evidence.

## 4. Qualify separately

Use a candidate-specific record under `docs/testing/qualifications/` and the
Stage 2 lifecycle in `docs/testing/README.md`. Only reviewer-validated results
may satisfy its physical matrix. Physical work requires a separately approved
plan, named article and operator, expected and actual observations, rollback
readiness, sanitized evidence provenance, and stop conditions.

A `Qualified` decision applies only to the recorded candidate. It is not
approval to merge, tag, publish, deploy, or alter repository controls.

## 5. Publish deliberately

Damien must separately approve publication. An authorized operator then runs
`Release controls` manually with action `publish`, the already-existing
immutable tag, its `Qualified` record path, and the exact confirmation
`PUBLISH`.

The workflow re-verifies the candidate before its only write-enabled job creates
the GitHub release. Do not dispatch this action to test the procedure. Release
editing, deletion, replacement, or deployment each remains separately governed.

## Failure and rollback boundary

Stop on an identity mismatch, failed gate, missing or non-qualified record,
unexpected workflow action, or evidence disagreement. Preserve the failed run.
Before publication, correct the source through a new reviewed candidate. After
publication, do not mutate tags or releases without Damien's explicit approval.

The current source/release mismatch remains documented in `PROJECT_STATUS.md`.
This procedure does not authorize or perform its alignment.
