# Phase 8 — Protocol evidence and safety qualification

## Scope

Phase 8 qualifies the reconciled offline protocol tooling. It does not enable
native York transmission, remove the Android tablet, or add multiple-device
support.

## Evidence boundary

- The approved decoder fixtures are observed device state responses.
- A response signature or fixture match may classify a frame as a response, but
  classification never verifies it or makes it executable.
- Relay extraction records contain HTTP JSON sent to the Android relay. They do
  not contain the native York packet built inside the Android application.
- The Android application still constructs the native York command. Tablet
  removal is not achieved.

## Phase 8 changes

- Imported records now preserve source SHA-256, size, timestamp provenance,
  source locations and the transformations applied during import.
- An approved, credential-free excerpt from the historical `Modes log` capture
  is tracked for deterministic offline qualification.
- The classifier records evidence traces and explicitly labels its conclusions
  as inference rather than verification.
- The request hunter rejects missing, incomplete or ambiguous provenance and
  requires an explicit controller-to-device occurrence before eligibility.
- Executable packet records require verified status, an explicit transmit-safe
  decision, prior successful-response evidence and an identified source
  capture.
- Relay extraction JSON carries a machine-readable evidence type and explicitly
  states that no native York packet was extracted.

## Manual evidence review

Representative frame `yrk-observed-df4fc29e4226` was checked against the
historical Google Drive document `Modes log`:

- Source event: sample 009 at `2026-07-13 16:48:36.357`.
- Frame: `BB 01 00 03 0F 01 00 31 06 00 00 00 00 00 00 00 00 5F 00 00 DF`.
- Context: immediately follows the operator mark `mode cooling`.
- Decoder fixture: `cool-low`.
- Conclusion: observed state response used for offline decoding; not a native
  request or command candidate.

The source document contains reusable device credentials in unrelated
initialization records. Those values are deliberately excluded from the tracked
sanitized excerpt and from this evidence record.

## Gate results

- Targeted protocol, provenance and no-send checks: **33/33 passed**.
- Complete reconciled test suite: **117/117 passed**.
- Decoder qualification: **14/14 approved fixtures passed**.
- Existing observed library: **23 state responses**, **0 state requests**,
  **0 eligible request candidates**, **0 verified/executable records**.
- Release verification, Python compilation, example relay configuration,
  diff checks and tracked-tree credential scan: **passed**.
- Approved excerpt SHA-256:
  `99970120f512209bb499a562e9291d4029692478ab24bcb34e9e71993853e4b8`.
- Decoder fixture SHA-256:
  `988fd590bc4a84e5c5268d7094351c69eb535ff6c710f30016485bc2c521ec27`.

## Gate decision

Commit `26261290d326bf6838ac4e36c32672d68ec4babe` was published as the
exact head of `feature/climate-bridge-reconciliation` and remotely verified.
Its parent is the qualified Phase 6 commit `9eb05bf…`; no additional commits
were introduced and `main` remained unchanged at `97fb20b…`.

Gate 8: PASS.
