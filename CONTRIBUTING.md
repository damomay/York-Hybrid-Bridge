# Contributing to Climate Bridge

Climate Bridge 1.0.0 is a native, single-device York/TCL bridge. Read
[`PROJECT_STATUS.md`](PROJECT_STATUS.md), [`AGENTS.md`](AGENTS.md), and the
documents they identify before proposing a change.

## Workflow

`main` is the authoritative accepted state. Fetch it, confirm a clean checkout,
create a focused branch from current `origin/main`, and open a pull request into
`main`. Do not commit directly to `main`. The former `Develop` workflow appears
only in historical records and is not the current contribution model.

Keep each pull request to one logical scope. Describe user impact, safety
boundaries, verification, limitations, documentation changes, and handover
details. Architectural, protocol, live-device, release, or governance changes
need Damien's explicit approval as detailed in `AGENTS.md`.

## Engineering expectations

- Prefer clear, focused Python and preserve fail-closed behaviour.
- Add or update tests for behaviour changes; never weaken assertions or hide a
  failure with an unexplained skip or xfail.
- Keep relay JSON, native York requests, and state responses distinct.
- Never treat an observed packet as executable without provenance, review, and
  the required physical qualification.
- Update current documentation when behaviour or configuration changes.
- Preserve useful historical records and label them as history.

## Verification

Use the safe gates in [`docs/TESTING.md`](docs/TESTING.md). Live HVAC testing,
capture collection, Docker deployment, and release operations are not implied
by ordinary contribution work. Report every check run and every check omitted.

## Sensitive information

Never commit `config.yml`, credentials, device addresses, unsanitized logs,
captures, generated reports, caches, or machine-specific files. Redact and
review diagnostic material before sharing it in an issue or pull request.
