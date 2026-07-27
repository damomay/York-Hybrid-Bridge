# Roadmap

Climate Bridge has grown from the York Hybrid Bridge protocol reverse-engineering project into a reliable Home Assistant integration for York split-system air conditioners using proprietary TFIAC/Broadlink WiFi modules.

While York support remains the primary focus today, the long-term vision is much broader.

The goal is to develop a vendor-independent Hybrid Bridge framework capable of integrating a wide range of proprietary HVAC systems with Home Assistant while maintaining the project's core principles:

- Reliability
- Local control
- Maintainability
- Extensibility
- Transparency

This roadmap outlines the planned direction of the project. Features and priorities may change as the project evolves and community feedback is received.

---

# Current Release

## Version 1.0.0-alpha.20

**Status:** Reconciliation alpha

### Highlights

- Native Home Assistant Climate integration
- MQTT Discovery
- Automatic device registration
- Comprehensive diagnostics
- Health monitoring
- Stability monitoring
- Automatic recovery
- Production-ready Docker deployment
- Synology Container Manager compatibility

---

# Version 3.1 – User Experience

**Status:** Planned

The focus of Version 3.1 is improving usability, visibility, and day-to-day operation.

### Planned Features

- Multi-device support
- Improved diagnostics dashboard
- Enhanced Home Assistant entities
- Historical performance metrics
- Additional health sensors
- Improved configuration validation
- Automatic relay discovery
- Enhanced logging
- Performance optimisations
- Expanded documentation

---

# Version 3.2 – Platform Improvements

**Status:** Planned

Version 3.2 begins separating vendor-specific functionality from the bridge core.

### Planned Features

- Vendor abstraction layer
- Device capability model
- Shared protocol interfaces
- Improved configuration architecture
- Plugin-based protocol adapters
- Simplified bridge startup
- Expanded automated testing
- Improved configuration migration

---

# Version 4.0 – Hybrid Bridge Framework

**Status:** Future Vision

Version 4 represents the transition from a York-specific bridge to a vendor-independent Hybrid Bridge platform.

### Goals

- Generic bridge framework
- Multiple HVAC vendor support
- Shared diagnostics engine
- Shared MQTT implementation
- Shared recovery engine
- Vendor-specific protocol adapters
- Unified configuration
- Improved deployment options

Supported vendors may include:

- York
- TCL / TFIAC
- Additional proprietary Broadlink-based systems
- Community-developed adapters

---

# Long-Term Vision

The long-term objective is to create a flexible platform capable of supporting multiple proprietary HVAC systems through a common architecture.

The core bridge will provide:

- MQTT integration
- Home Assistant Discovery
- Diagnostics
- Health monitoring
- Recovery
- Logging
- Configuration
- Performance monitoring

Each HVAC manufacturer will be supported through an independent protocol adapter while sharing the same reliable bridge infrastructure.

---

# Future Ideas

The following ideas are under consideration.

## Home Assistant

- Dashboard package
- Blueprint support
- Device diagnostics page
- Service call helpers
- Improved entity grouping

## Diagnostics

- Web diagnostics interface
- Performance graphs
- Event history
- Recovery history
- System statistics
- Health timeline

## Deployment

- Automatic updates
- Container health checks
- Backup and restore
- Installation wizard
- Configuration validation tools

## Development

- GitHub Actions CI/CD
- Automated release builds
- Expanded test coverage
- Performance benchmarking
- Developer documentation

---

# Guiding Principles

Every new feature should support at least one of the following goals:

- Improve reliability
- Improve maintainability
- Improve diagnostics
- Improve performance
- Improve user experience
- Simplify deployment
- Enable future vendor support

Features that significantly increase complexity without providing meaningful user value are unlikely to be accepted.

---

# Community Contributions

Community feedback plays an important role in shaping the future of Climate Bridge.

Suggestions, bug reports, feature requests, protocol research, testing, and documentation improvements are all welcome.

Contributors interested in supporting additional HVAC manufacturers are especially encouraged to participate as the project evolves toward a vendor-independent Hybrid Bridge framework.

---

# Project Vision

Climate Bridge is more than a Home Assistant integration.

It is the foundation of a reliable, extensible platform for bringing proprietary HVAC systems into the Home Assistant ecosystem without cloud dependencies.

Every release moves the project closer to that vision.
