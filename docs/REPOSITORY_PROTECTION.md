# Repository protection

The authoritative `main` branch is protected by the active GitHub ruleset
`Climate Bridge main protection` (ruleset ID `21189524`). Changes to `main`
must arrive through a pull request and pass these GitHub Actions checks:

- `Python 3.12`
- `Static, package and container gate`

The pull-request branch must be up to date with `main` before merging. Deletion
and force-pushes are blocked. The ruleset has no bypass actors and requires zero
approving reviews because the repository currently has one maintainer, who
cannot approve their own pull request.

GitHub automatically added
`require_extra_approval_for_unattributed_changes: true` when the ruleset was
created. It was not part of the submitted Gate A payload, has no operational
effect while required approvals remain zero, and is not an independently
requested protection control.

Changing, disabling, bypassing or deleting the ruleset requires separate
explicit approval and a recorded reason. If protection unexpectedly blocks
normal work, capture the affected pull request, checks, effective rules and
error before proposing the smallest recovery change. Do not weaken protection
as an unrecorded workaround.

Release-tag protection is a separate control and is not documented here as
active until it has been separately approved, created and verified.
