# Changelog

All notable changes are recorded here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and versions follow
[Semantic Versioning](https://semver.org/).

## [1.0.0-alpha.20] - 2026-07-27

### Added

- Transport abstraction with the proven Android relay as the default.
- Guarded York-direct research scaffolding that rejects unverified
  transmission.
- York capture import, evidence provenance, packet classification, decoder
  qualification, request hunting, replay safety and relay extraction tools.
- Reconciliation tests and evidence for repository structure, identity,
  configuration, packaging, Docker qualification and protocol safety.
- Contributor documentation for architecture, configuration, testing,
  troubleshooting, release status and the post-reconciliation roadmap.

### Changed

- Adopted Climate Bridge as the current product identity while retaining York
  Hybrid Bridge as historical lineage.
- Established `VERSION` as the canonical application version source.
- Reconciled optional MQTT credentials and the safe relay example
  configuration.
- Organized all approved alpha.20 tests in `tests/` without removing the
  original 18-test polished baseline.
- Preserved source fingerprints, capture context and transformation metadata
  in imported protocol evidence.
- Required complete, unambiguous controller-to-device provenance before the
  request hunter can rank a candidate as eligible.

### Qualified

- Complete Gate 8 suite: 117/117 tests passed.
- Docker build, network-free container health and clean shutdown passed.
- One-device Android-relay live regression passed for discovery, state,
  power, modes, setpoint, fan, swing and restart safety.
- Decoder qualification: 14/14 approved fixtures passed.
- Observed library: 23 state responses, zero eligible request candidates and
  zero verified/executable native records.

### Known limitations

- The Android York TFIAC Relay V2 is still required.
- Native direct control and tablet removal are not achieved.
- The current runtime configures one York device only.
- Multiple-device and multi-vendor operation remain future work.

## Historical lineage

### [York Hybrid Bridge 3.0.0] - 2026-07-19

The polished York Hybrid Bridge repository recorded its first stable release.
That historical milestone supplied the runtime, MQTT Discovery, recovery,
diagnostics, Docker deployment, repository structure and 18-test baseline
retained during reconciliation.

#### Added

- Home Assistant climate entity and automatic MQTT Discovery.
- Power, HVAC mode, target temperature, fan, swing, preset and state
  synchronisation support through the Android relay.
- Health, stability, MQTT, relay, event, performance, recovery and uptime
  diagnostics.
- Automatic relay and MQTT recovery.
- Docker and Synology Container Manager deployment.

#### Relationship to Climate Bridge

Climate Bridge began from the proven York Hybrid Bridge 3.0 RC5 runtime. The
polished repository subsequently recorded 3.0.0 while the engineering stream
advanced through Climate Bridge alpha releases. Reconciliation retained the
useful work from both histories. York Hybrid Bridge 3.0.0 is not the current
application version.

[1.0.0-alpha.20]: https://github.com/damomay/York-Hybrid-Bridge/compare/v3.0.0...feature/climate-bridge-reconciliation
[York Hybrid Bridge 3.0.0]: https://github.com/damomay/York-Hybrid-Bridge/releases/tag/v3.0.0
