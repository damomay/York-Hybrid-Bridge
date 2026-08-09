# Sprint 3.2.1 / V1 source reconciliation

Status: DRAFT — repository review required.

## Authoritative inputs

- GitHub baseline: `main` at `4bf26e1`.
- Intended release source:
  `Climate_Bridge_1.0.0_Sprint_3_2_1_First_York_Stable_Release.zip`.
- Release-source SHA-256:
  `61ef4558ae00c4fde806f38f822e8b71a31c338be5d2156b430a37f90e3a34aa`.
- Three-way ancestor:
  `Climate_Bridge_1.0.0-alpha.20_Sprint_2_8_3_Relay_Command_Extraction.zip`.

## Reconciliation policy

Sprint 3.2.1 is the intended V1 runtime baseline. GitHub-only files and
same-path changes are retained when they represent validated repository
hygiene, compatibility, reconciliation evidence, CI, or later tablet-removal
discovery work. Source-only runtime and qualification evidence is imported.
Generated caches, bytecode, dashboard output, statistics output, timeline
output, local configuration, secrets, and machine-specific files are omitted.

Historical Sprint records are stored under `docs/history/` instead of being
restored to the repository root. The V1 upgrade guide is stored under `docs/`.

## Comparison results

The initial path/hash comparison found:

- 93 shared paths with different content;
- 162 source-only paths; and
- 116 repository-only paths.

Using alpha.20 as the common ancestor classified 69 shared files as
GitHub-only improvements and 24 as independently changed on both lines. Ten
of those 24 merged cleanly after line-ending normalization. Runtime conflicts
were resolved toward the validated V1 behavior while retaining compatibility
aliases and the repository's canonical `VERSION` reader.

## Validation

- Forced Python compilation: PASS.
- Declared V1 dependencies: installed successfully.
- Repository test collection: PASS after retaining the historical public
  `YorkBridge`, `ConfigError`, and `RelayTransport` imports.
- Repository tests: 103 passed, 35 failed.

The remaining failures are predominantly alpha.20/relay contract assertions
that conflict with V1's `1.0.0` identity and native-LAN runtime. They are not
silently rewritten in this reconciliation commit.

The supplied V1 archive is also internally incomplete for source validation:
its `release_verifier.py` requires multiple `test_sprint_*` files that are not
present in either the V1 archive or the immediately preceding Beta.1 archive.
This draft must not be merged until maintainers decide whether those tests
should be recovered from another validated source or the verifier inventory
should be corrected.
