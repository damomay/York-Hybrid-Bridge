# Sprint 3.2.1 / V1 source reconciliation

Status: DRAFT — repository review required.

The reconciled result is being reviewed through a draft pull request; main is
not modified directly.

Newer validated GitHub work was preserved where it remained compatible with
the stable V1 safety boundary; conflicts were reviewed individually.

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
- Recovered V1 tests: 53 exact archive-derived modules, selected from the
  newest validated Sprint archive containing each test.
- Reconstructed evidence contracts: 14 verifier-named tests absent from every
  available validated archive, based on committed qualification records and
  immutable runtime allowlists.
- Obsolete relay runtime and its relay-only tests: removed as required by the
  V1 release verifier and Sprint 3.1.30 safety boundary.
- Complete repository and recovered V1 suite: 773 passed.
- Phase 6 tracked-tree gate: PASS.
- V1 release verifier: PASS.
- Example configuration validator: PASS (`native`).
- `git diff --check`: PASS.
