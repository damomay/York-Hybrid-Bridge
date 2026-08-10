# GitHub controls

## Accepted contribution path

Current fetched `origin/main` is the source authority. Work starts from that
commit on a focused branch, stays within approved scope, receives safe offline
verification, and enters `main` through a pull request. Never use a historical
tag, release, archive, generated package, or transcript as a source overlay.

Pull requests must identify purpose, exact files, checks and unrun checks,
limitations, risks, rollback, and the next permitted action. They must separate
offline verification from physical testing and link controlled records for any
separately approved live work.

## Automated workflows

- `Tests` runs the existing Python suite for pushes and pull requests to `main`,
  plus deliberate manual dispatches.
- `Network-free qualification` runs the existing static, metadata, test, clean
  tree, image-build, and network-disabled container gate for pull requests to
  `main`, plus deliberate manual dispatches.
- `Release controls` verifies semantic-version tags on tag push but publishes
  only after a manual `publish` dispatch and confirmation. Repository-level
  permissions are read-only; only the publication job receives `contents:
  write`.

Workflow success does not authorize merge, physical testing, a tag, release
publication, deployment, or repository-setting changes.

## Evidence and issue handling

Issues, pull requests, workflow logs, and committed records must contain only
sanitized, necessary information. Raw logs, captures, configurations, device
identifiers, network addresses, credentials, tokens, and private evidence stay
in an approved private location. Use opaque references and record SHA-256 values
only when calculated from originals. Preserve failed and inconclusive attempts.

## Administrative controls

Branch protection, rulesets, environments, permissions, secrets, repository
settings, merges, branch deletion, force-pushes, and history rewrites require
Damien's explicit approval. Read-only inspection does not grant authority to
change them. Follow `AGENTS.md`, `docs/TESTING.md`, and
`docs/RELEASE_PROCESS.md` when planning any controlled action.
