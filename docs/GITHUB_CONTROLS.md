# GitHub controls: read-only audit and operating boundary

This is a read-only audit, not a repository-settings baseline and not approval
to change a setting. Observations were collected on 2026-08-10 with authenticated
`gh api` reads for `damomay/York-Hybrid-Bridge`. Source-workflow observations
apply to the revision containing this document; hosted settings can change after
the observation time and must be re-read before any controlled action.

## Observed controls

### Repository and merge configuration

| Field | Observed value |
| --- | --- |
| Owner / repository | `damomay/York-Hybrid-Bridge` |
| Visibility / archived / disabled | Public / false / false |
| Default branch | `main` |
| Issues / projects / pull requests | Enabled / enabled / enabled |
| Wiki / Pages / discussions | Disabled / disabled / disabled |
| Merge methods | Merge commits, squash merges, and rebase merges enabled |
| Auto-merge / update branch | Disabled / disabled |
| Delete head branch after merge | Disabled |
| Web commit sign-off required | Disabled |
| Repository access used for audit | Authenticated account reported admin, maintain, push, triage, and pull access |

### Branch protection and rules

| Field | Observed value |
| --- | --- |
| `main` commit at audit | `8fb4d740b0f1378029095efa7c3d18247ebe7a67` |
| `main` protected | No; branch protection endpoint returned `404 Branch not protected` |
| Repository rulesets | None returned |
| Required pull-request reviews | Not enforced by branch protection or a ruleset |
| Required approving-review count / code-owner review | Not configured through branch protection |
| Dismiss stale approvals / last-push approval | Not configured through branch protection |
| Required status checks / strict up-to-date branch | None enforced |
| Required conversation resolution | Not enforced |
| Required signed commits / linear history | Not enforced |
| Administrator enforcement | Not configured |
| Push restrictions | Not configured |
| Force-push / branch-deletion protection | Not configured |

### Actions, environments, secrets and integrations

| Field | Observed value |
| --- | --- |
| GitHub Actions enabled | Yes |
| Allowed actions | All actions and reusable workflows |
| Full-length action SHA pinning required | No |
| Default `GITHUB_TOKEN` permission | Read |
| Workflows may approve pull requests | No |
| Environments | None |
| Actions secret names / variable names | None returned |
| Repository webhooks | None returned |
| Secret scanning / push protection | Disabled / disabled |
| Dependabot security updates | Disabled |

The API reveals secret names, not values. No secret value was requested or read.

### Source-controlled workflows and contribution surfaces

- `Tests` runs the existing Python suite on pushes and pull requests to `main`,
  and by manual dispatch. Its workflow permission is `contents: read`.
- `Phase 6 Qualification` retains its established identity and runs on pushes
  and pull requests to `main`, and by manual dispatch. It preserves the static,
  metadata, complete-test, clean-tree, clean-image, and network-free container
  gate. It does not authorize live HVAC testing.
- `Release controls` is manual-dispatch only. Verification and publication are
  part of one deliberate dispatch for an existing immutable tag. Repository
  permission defaults to `contents: read`; only the publication job receives
  `contents: write`.
- Pull-request and issue templates separate offline evidence from physical work,
  warn against sensitive evidence, and preserve approval boundaries.

At audit time the only tag and release were `v3.0.0` and “York Hybrid Bridge
v3.0.0”; accepted source identifies Climate Bridge 1.0.0. This audit does not
authorize or perform alignment.

## Unverified controls

The following were not verified and must not be inferred from an empty or
successful API response:

- organization, enterprise, network, or account policies outside this
  repository;
- collaborator, team, deploy-key, GitHub App, OAuth grant, runner-group, or
  runner-host access;
- environment secrets or protection rules, because no environments existed;
- secret values, token provenance, credential rotation, or private evidence
  storage controls;
- external CI, package registries, deployment targets, DNS, MQTT, HVAC, or Home
  Assistant controls;
- audit-log history and whether a hosted setting changed after 2026-08-10; and
- effectiveness of a future protection/rules configuration not yet approved.

## Recommendations requiring separate approval

These are recommendations only. `AGENTS.md` requires Damien's explicit approval
before any implementation:

1. Protect `main` or apply an equivalent ruleset.
2. Require pull requests, at least one independent approval, stale-approval
   dismissal, conversation resolution, and protection from force-push/deletion.
3. Require the `Tests` and `Phase 6 Qualification` checks and require branches
   to be current before merge.
4. Consider signed commits, linear history, action allow-listing, immutable
   action SHA pinning, and an approved release environment with reviewers.
5. Review merge methods, branch deletion, security scanning, Dependabot,
   collaborators, apps, deploy keys, runners, and audit logs under a separately
   approved administrative plan.

Workflow success is evidence only. It never authorizes merge, physical testing,
tag creation, publication, deployment, or a repository-setting change.
