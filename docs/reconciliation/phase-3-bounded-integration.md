# Phase 3 — Bounded alpha.20 integration

Status: PASS.

## Scope

Phase 3 selectively integrated the alpha.20 engineering payload in three
independent slices. It did not replace the repository with the ZIP, remove the
tablet relay, enable native York control, add multiple-device support, or alter
`main`.

## Slice 3A — Runtime and transport

Commit: `2b41583` (`Integrate runtime transport abstraction`)

- Preserved the validated configuration errors and legacy `relay` aliases.
- Kept the Android relay as the default transport.
- Added the transport interface and York adapter modules.
- Preserved the established MQTT, discovery, diagnostics, health, recovery and
  command behaviour.
- Kept `RelayError` and `RelayManager` available to existing callers.
- Added readiness and heartbeat lifecycle files.
- Blocked York-direct construction unless `direct_device.enabled` is explicit.
- Used reserved example endpoints and a fabricated locally administered MAC in
  committed tests.

Checks:

- Import and compile: PASS.
- Original repository tests: 18/18 PASS.
- Targeted runtime/transport command: 24/24 PASS at the Slice 3A checkpoint.
- Sanitized example configuration: relay default; York direct disabled.

## Slice 3B — Protocol research and analysis

Commit: `1b0636b` (`Add York protocol analysis stack`)

- Added the capture importer, packet library, decoder qualification, packet
  classifier, XML parser and protocol dashboard.
- Added only manifest-approved source, documentation and observed packet
  records.
- Omitted generated dashboards, import reports, timelines, statistics,
  quarantine output and qualification reports.
- Kept the research stack outside normal bridge startup.

Checks:

- Research module imports performed no network call or evidence write: PASS.
- Approved fixture imported deterministically across repeat runs: PASS.
- Repeat classification and decode result: PASS.
- Targeted protocol checks: 25/25 PASS.
- Combined checkpoint: 49/49 PASS.

## Slice 3C — Guarded transmission research

Commit: `51484d9` (`Add guarded York transmission research`)

- Added replay, transmission logging, request hunting and relay-command
  extraction.
- Relay extraction remains disabled by default.
- Native probe and replay require both `direct_device.enabled: true` and the
  deliberate `--confirm-transmit` runtime flag.
- `--validate-only` opens no socket and transmits no packet.
- Unverified, incomplete and wrong-purpose records remain non-executable.
- Relay extraction reports state that captured HTTP JSON is not proof of a
  native York packet.

Checks:

- Guard and dry-run subset: 21/21 PASS at the Slice 3C checkpoint.
- Default configuration performs no experimental transmission: PASS.
- Candidate rejection checks: PASS.
- Sensitive fixture scan: PASS.
- Combined checkpoint: 64/64 PASS.

## Final local Gate 3 verification

Baseline tested: local reconciliation branch at `51484d9`, based on the
remote validated Phase 2 shell commit `30e52db`.

- Python compile check over runtime, adapters, transports and protocol tools:
  PASS.
- Original repository baseline subset: 18/18 PASS.
- Complete reconciled suite: 64/64 PASS.
- Sanitized configuration load: PASS.
- Relay default and experimental actions disabled: PASS.
- GitHub workflow YAML parse: PASS.
- `git diff --check`: PASS.
- Generated/cache files tracked: none.
- `main` changed: no.

The bounded Phase 3 commits `2b41583`, `1b0636b`, `51484d9` and `5787725`
were published to `feature/climate-bridge-reconciliation` and remotely
verified before Phase 4 began. `main` remained unchanged.

Gate 3: PASS.
