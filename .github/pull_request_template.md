# Pull Request

## Purpose and scope

Describe the approved purpose, the files changed, and anything deliberately excluded.

Related issue or control-stage approval:

## Change classification

- [ ] Runtime, protocol, or configuration behaviour
- [ ] Tests or fixtures
- [ ] Docker, packaging, or workflow
- [ ] Documentation or repository controls only
- [ ] Other (explain)

## Verification performed

List exact commands and results. Distinguish safe offline checks from any separately approved physical work.

### Offline verification

- [ ] Relevant automated tests passed
- [ ] `git diff --check` passed
- [ ] Checks not run are listed below with reasons

### Physical or live testing

- [ ] Not performed and not required for this change
- [ ] Performed only under a separately approved plan; controlled record(s):

Passing offline checks do not authorize live HVAC commands, network capture, deployment, physical qualification, tag creation, or release publication.

## Evidence and sensitive data

- [ ] Repository evidence is necessary, sanitized, and limited to opaque references and hashes actually calculated from originals.
- [ ] No raw logs, captures, credentials, tokens, device identifiers, or private network details are included.
- [ ] Failed, stopped, incomplete, and inconclusive attempts remain preserved where applicable.

## Release and control boundaries

- [ ] No tag, release, repository setting, branch protection, ruleset, environment, permission, or secret was changed unless separately and explicitly approved.
- [ ] Candidate qualification, merge, tag approval, publication approval, and deployment approval remain separate decisions.
- [ ] Breaking changes, limitations, risks, and rollback considerations are documented.

## Handover

Summarize checks, unrun checks, limitations, risks, rollback, reviewer needs, and the next permitted action.
