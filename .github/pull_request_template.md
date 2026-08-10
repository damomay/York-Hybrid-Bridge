# Pull request

## Approval, purpose and exact scope

- Approval / issue / stage reference:
- Purpose and user impact:
- Base commit / candidate full SHA:
- Files changed:
- Explicit exclusions and next-stage boundary:

## Change classification and effects

- [ ] Runtime, protocol, or configuration behaviour
- [ ] Tests, fixtures, or evidence controls
- [ ] Docker, packaging, dependency, or workflow
- [ ] Documentation or repository controls only
- [ ] Version, tag, release, deployment, or repository setting (requires separate explicit approval)
- [ ] Breaking change (explain migration and compatibility)

Describe architecture, security, safety, compatibility, performance, Home
Assistant/MQTT, Docker/package, and operator effects. State “none” explicitly
where reviewed and unaffected.

## Safe offline verification

List every command, environment/tool version, exact result and count:

- [ ] Relevant tests passed without weakened assertions, unexplained skips, or xfails
- [ ] Static, metadata, configuration, and package checks passed
- [ ] Network-free container qualification passed when applicable
- [ ] `git diff --check` passed
- [ ] Worktree cleanliness checked

Checks not run, reason, limitation, and responsible next action:

Offline checks do not authorize live HVAC commands, capture, deployment,
physical qualification, merge, tag creation, release publication, or settings.

## Physical or live testing

- [ ] Not performed and not required for this change
- [ ] Separately approved and recorded below

Plan revision / device and case / operator / date / expected observation /
actual observation / result IDs / reviewer / stop or rollback events:

Do not label manual review, Docker startup, or offline simulation as physical
qualification. Stop on unexpected commands, retries, state changes, or a
reported/physical disagreement.

## Evidence and sensitive-data review

- [ ] Only necessary sanitized facts and opaque private-evidence references are included
- [ ] Recorded SHA-256 values were actually calculated from originals
- [ ] No raw logs, captures, configurations, credentials, tokens, device identifiers, addresses, or private paths are included
- [ ] Failed, stopped, incomplete, and inconclusive attempts remain preserved
- [ ] Evidence owner, provenance, reviewer, limitations, and retention location are recorded

## Risk, rollback and decision separation

- Risks, limitations, known deviations and mitigations:
- Rollback boundary and procedure:
- [ ] Documentation and release notes are accurate for this exact revision
- [ ] Plan readiness, result validation, qualification, merge, tag, publication, deployment, and repository-control approvals remain separate
- [ ] No tag, release, environment, secret, permission, protection, ruleset, setting, or deployment was changed without explicit approval

## Handover

Owner / current state / exact revision / checks and unrun checks / open defects
or evidence / pending reviewer / next permitted action:
