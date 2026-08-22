# Controlled release notes

Future publication notes are reviewed source-control inputs, not text generated
during publication. Name each record `vX.Y.Z.md`, place it directly in this
directory, and ensure the filename matches the exact existing release tag.

Each record must contain exactly one of every heading below:

- `## Release scope`
- `## Supported functions`
- `## Known limitations`
- `## Installation or upgrade`
- `## Rollback`

Resolve all placeholders before review. Record only sanitized software facts;
keep raw logs, device/network identifiers, credentials, configurations, and
private test evidence outside Git. Acceptance of notes does not approve a tag,
workflow dispatch, publication, deployment, or operational change.
