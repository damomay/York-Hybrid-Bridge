# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and this project follows [Semantic Versioning](https://semver.org/).

# [1.0.0-alpha.20] - 2026-07-27

## Changed

- Adopted Climate Bridge as the current product identity.
- Preserved York Hybrid Bridge as the historical project lineage.
- Established `VERSION` as the canonical application version source.
- Reconciled relay, guarded direct-mode, optional MQTT credential, and safe example configuration behaviour.

## Added

- Transport abstraction and guarded York-direct research scaffolding.
- York protocol capture, analysis, qualification, replay, request-hunting, and relay-extraction tooling.

---

# [3.0.0] - 2026-07-19

## York Hybrid Bridge — First Stable Release

York Hybrid Bridge reaches its first stable public release.

This release provides a reliable, production-ready bridge between York split-system air conditioners using the proprietary **TFIAC (Broadlink Device Type 20014)** protocol and Home Assistant through native MQTT Discovery.

---

## Added

### Home Assistant Integration

- Native Home Assistant Climate entity
- Automatic MQTT Discovery
- Automatic device registration
- Automatic entity creation
- Native Home Assistant device information

### Climate Control

- Power control
- HVAC mode control
- Target temperature
- Fan speed control
- Swing mode support
- Preset support
- Automatic state synchronisation

### Diagnostics

- Bridge health scoring
- Stability scoring
- Bridge summary sensor
- Health advisor sensor
- MQTT status monitoring
- Relay status monitoring
- Event reporting
- Performance metrics
- Poll timing metrics
- Command timing metrics
- Recovery statistics
- Uptime reporting

### Recovery

- Automatic relay recovery
- Automatic MQTT reconnection
- Recovery timing statistics
- Recovery reason reporting
- Automatic fault detection

### Deployment

- Docker support
- Synology Container Manager compatibility
- YAML-based configuration
- Production logging
- Automatic version reporting

---

## Improved

### Reliability

- Production-hardened bridge architecture
- Improved configuration validation
- Improved MQTT lifecycle management
- Improved relay communication
- Improved Home Assistant discovery publishing
- Improved diagnostics reporting
- Improved recovery management
- Improved health evaluation
- Improved error handling throughout the bridge

### Code Quality

- Consistent version management
- Comprehensive inline documentation
- Centralised configuration constants
- Improved readability
- Simplified maintenance
- Reduced code duplication
- Improved logging consistency

---

## Fixed

- MQTT reconnect handling
- Discovery publishing consistency
- Recovery timing accuracy
- Relay communication robustness
- Configuration validation edge cases
- Logging consistency
- Error reporting improvements
- Stability monitoring accuracy

---

## Testing

This release has been production hardened through continuous testing.

Core runtime modules were individually reviewed and refactored while maintaining a fully passing automated test suite throughout development.

### Runtime modules reviewed

- configuration.py
- bridge.py
- mqtt_manager.py
- relay_manager.py
- discovery_manager.py
- health_manager.py
- diagnostics_manager.py
- recovery_manager.py

### Test Status

- ✅ 18 automated tests passing
- ✅ No regressions introduced during refactoring
- ✅ Production-ready release

---

## Documentation

Added and improved documentation including:

- Professional project README
- Project overview
- Architecture documentation
- Feature documentation
- Installation guidance
- Configuration examples
- Changelog

---

## Notes

This release represents the first stable version of York Hybrid Bridge.

The bridge has been engineered for reliable long-term unattended operation with comprehensive diagnostics, automatic recovery, and seamless Home Assistant integration.

While this release focuses on York systems using the TFIAC (Broadlink Device Type 20014) protocol, the underlying architecture has been designed to evolve into a vendor-independent Hybrid Bridge framework capable of supporting additional HVAC manufacturers in future releases.

Future development will focus on expanding protocol support while maintaining the same standards of reliability, diagnostics, maintainability, and Home Assistant integration.

---

[3.0.0]: https://github.com/<YOUR_GITHUB_USERNAME>/York-Hybrid-Bridge/releases/tag/v3.0.0
