# Repository working instructions

These rules apply to every person or automated agent working in this repository.

## Authority and orientation

- The fetched GitHub `main` branch is the authoritative accepted project state.
  Tags and GitHub releases identify published versions; they do not override
  newer accepted source on `main`.
- Before changing anything, verify the repository and remote, GitHub
  authentication, branch, clean status, current `origin/main`, repository
  instructions, `PROJECT_STATUS.md`, and the documents relevant to the task.
- Never rebuild or overlay a checkout from an old ZIP, generated package, chat
  transcript, or remembered audit. Such material may be evidence only after it
  is explicitly identified, hashed where appropriate, and compared with `main`.

## Branches, review, and handover

- Never change `main` directly. Create a focused branch from current
  `origin/main` and use a pull request into `main`.
- Preserve unrelated work. Keep commits and pull requests limited to their
  approved scope.
- Document purpose, files changed, verification, unrun checks, limitations,
  risks, rollback considerations, and the next permitted action.
- Keep current documentation concise and move or link useful superseded detail
  as clearly labelled history; do not rewrite historical evidence as though it
  described the present.

## Testing and evidence boundaries

- Run safe offline checks relevant to the change. Tests do not authorize live
  device writes, network capture, deployment, or physical qualification.
- Physical evidence must identify the approved device/case, operator,
  observation, expected result, actual result, and provenance. Stop on any
  unexpected command, retry, state change, or disagreement between reported and
  physical state.
- Treat logs, captures, configurations, device identifiers, network addresses,
  credentials, and tokens as sensitive. Store only sanitized, necessary
  evidence; never publish raw private material.

## Release safety and explicit approval

Tags, releases, package publication, version changes, branch protection,
rulesets, repository settings, branch deletion, merging, force-pushing, history
rewrites, live HVAC commands, physical qualification, credential use beyond
normal configured tooling, and destructive or irreversible operations require
Damien's explicit approval. A checklist or passing test is not release approval.

Runtime, protocol, configuration behaviour, tests, Docker, workflows, and
release assets must not change during documentation-only work.
