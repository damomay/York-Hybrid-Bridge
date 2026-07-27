# Phase 9 — Documentation and release evidence

Status: local Gate 9 checks passed; remote publication pending.

## Scope

Phase 9 makes the repository tell one accurate Climate Bridge
`1.0.0-alpha.20` story. It changes documentation and documentation/package
verification only. Runtime behaviour, relay protocol logic, native
transmission guards, device count and `main` remain unchanged.

## Verified story

- Android York TFIAC Relay V2 is the current working transport.
- The Android application still builds the native York command.
- Native direct control, tablet removal and multiple-device operation are not
  achieved.
- The one-device Android-relay path passed the Phase 7 live regression.
- Phase 8 qualified 14/14 decoder fixtures, 23 observed state responses, zero
  eligible request candidates and zero verified/executable native records.
- Climate Bridge evolved from the York Hybrid Bridge 3.0 RC5 runtime and
  polished York Hybrid Bridge repository.

## Documentation set

- `README.md`: contributor entrypoint, install, safe configuration, testing,
  limitations, lineage and next milestone.
- `CHANGELOG.md`: one current release entry plus preserved historical lineage.
- `RELEASE_NOTES.md`: alpha.20 evidence and limitations.
- `ROADMAP.md`: reconciliation freeze and locked post-reconciliation order.
- `docs/ARCHITECTURE.md`: current data path and component boundaries.
- `docs/CONFIGURATION.md`: current YAML keys and safe defaults.
- `docs/TESTING.md`: reproducible local, Docker, protocol and live gates.
- `docs/TROUBLESHOOTING.md`: evidence-preserving operational diagnosis.
- `CONTRIBUTING.md` and `SECURITY.md`: current gate and privacy requirements.

## Gate evidence

Baseline:
`26261290d326bf6838ac4e36c32672d68ec4babe`

Results:

- Phase 9 documentation contract: 5/5 passed.
- Complete reconciled suite: 122/122 passed.
- York decoder qualification: 14/14 passed.
- Python forced compilation: passed.
- Release/package verification: passed for `1.0.0-alpha.20`.
- Example configuration: validated as `relay`.
- Staged-tree privacy/generated-material scan: passed across 173 files.
- README local-link resolution: passed.
- Documented Python command/help checks: passed.
- Documentation identity, limitation and roadmap searches: passed.
- Staged `git diff --check`: passed.
- Docker commands: checked against committed Compose, Dockerfile and workflow;
  the local runtime has no Docker executable. The remote Gate 6 Docker run is
  the verified image/startup/health/shutdown evidence.
- Runtime or relay protocol files changed: no.
- Native transmission enabled or safety guard weakened: no.
- `main` changed: no.

The bounded documentation commit still requires publication to
`feature/climate-bridge-reconciliation` and exact remote verification before
Gate 9 can be marked PASS. Phase 10 remains locked.
