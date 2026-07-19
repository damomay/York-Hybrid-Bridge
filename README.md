# York-Hybrid-Bridge

[![Python](https://img.shields.io/badge/Python-3.11-blue.svg)]()
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED.svg)]()
[![Home Assistant](https://img.shields.io/badge/Home%20Assistant-MQTT%20Discovery-41BDF5.svg)]()
[![License](https://img.shields.io/badge/License-MIT-green.svg)]()
[![Release](https://img.shields.io/github/v/release/<YOUR_GITHUB_USERNAME>/York-Hybrid-Bridge)]()

Many York split-system air conditioners use Broadlink/TFIAC WiFi modules that are unsupported by Home Assistant. **York Hybrid Bridge** fills that gap by providing a reliable bridge between the proprietary **TFIAC (Broadlink Device Type 20014)** protocol and Home Assistant using MQTT Discovery.

Built with a strong focus on **reliability**, **automatic recovery**, **comprehensive diagnostics**, and **long-term unattended operation**, the bridge has been engineered for users who want their HVAC system to integrate seamlessly into Home Assistant without relying on cloud services or unsupported mobile apps.

Whether you're running Home Assistant on a Raspberry Pi, a Docker host, or a Synology NAS, York Hybrid Bridge provides a robust, production-ready solution for bringing your York air conditioner into your smart home.

---

## Home Assistant Devcice info

![Device Info]|(screenshots/device_info.png)|(screenshots/controls.png)|

---

# Project Goal

York Hybrid Bridge was created to provide a **stable, maintainable, open-source solution** for integrating York split-system air conditioners that use proprietary TFIAC/Broadlink WiFi modules with Home Assistant.

Beyond supporting York systems, the long-term vision is to evolve the project into a **vendor-independent Hybrid Bridge framework** capable of supporting additional HVAC manufacturers that use proprietary communication protocols. By separating device-specific protocol handling from the core bridge architecture, new vendors can be added with minimal changes while sharing the same reliable MQTT, diagnostics, recovery, and Home Assistant integration.

The project's guiding principles are:

- **Reliability first** – designed for continuous 24/7 unattended operation.
- **Local control** – no cloud dependency or vendor lock-in.
- **Maintainability** – clean architecture, comprehensive documentation and thorough testing.
- **Extensibility** – modular architecture that supports additional HVAC vendors in future releases.
- **Transparency** – comprehensive diagnostics, health monitoring and recovery reporting.

York Hybrid Bridge is intended to be more than a device integration—it is the foundation of a robust, extensible platform for connecting proprietary HVAC systems to Home Assistant.

---

# Features

- Automatic Home Assistant MQTT Discovery
- Native Home Assistant Device support
- Real-time climate control
- Automatic recovery from communication failures
- Health monitoring
- Stability monitoring
- Comprehensive diagnostics
- Performance metrics
- MQTT retained discovery
- Automatic MQTT reconnect handling
- Docker deployment
- Synology Container Manager compatible
- Production-tested architecture

---

# Supported Hardware

## Currently Supported

| Device | Status |
|---------|:------:|
| York Split System Air Conditioner | ✅ |
| Broadlink / TFIAC WiFi Module (Device Type 20014) | ✅ |

Future releases will expand support to additional HVAC manufacturers using the Hybrid Bridge architecture.

---

# Architecture

```
                   Home Assistant
                         │
                  MQTT Discovery
                         │
                  Mosquitto Broker
                         │
                 York Hybrid Bridge
                         │
                HTTP Tablet Relay API
                         │
             TFIAC WiFi Module (20014)
                         │
                York Split System AC
```

---

# Key Capabilities

## Climate Control

York Hybrid Bridge provides full Home Assistant climate entity support including:

- Power control
- Operating mode
- Target temperature
- Fan speed
- Swing control
- Presets
- State synchronisation

---

## Diagnostics

The bridge continuously publishes operational metrics including:

- Health score
- Stability score
- Bridge status
- MQTT status
- Relay status
- Poll statistics
- Command timing
- Recovery metrics
- Event history
- Uptime
- Error reporting

---

## Reliability

Designed for continuous unattended operation.

Features include:

- Automatic relay recovery
- Automatic MQTT reconnect
- Connection health monitoring
- Failure detection
- Performance monitoring
- Graceful degradation
- Automatic state recovery

---

# Requirements

- Python 3.11 or later
- Docker (recommended)
- MQTT Broker (Mosquitto recommended)
- Home Assistant
- York split-system air conditioner
- Broadlink / TFIAC WiFi module

---

# Installation

Detailed installation instructions are provided later in this document.

Supported installation methods include:

- Docker
- Docker Compose
- Synology Container Manager

---

# Configuration

Example configuration:

```yaml
mqtt:
  host: mqtt.local
  port: 1883
  username: mqtt
  password: secret

bridge:
  poll_interval: 5

relay:
  url: http://tablet-relay.local
```

A complete configuration reference is provided later in this document.

---

# Home Assistant

York Hybrid Bridge automatically creates all required Home Assistant entities using MQTT Discovery.

No manual MQTT entity configuration is required.

Automatically created entities include:

- Climate entity
- Bridge status
- Health sensors
- Stability sensors
- Recovery statistics
- Performance metrics
- Diagnostic sensors

---

# Project Status

**Current Version**

**v3.0.0**

**Status**

✅ Stable

The bridge has been production hardened with:

- Comprehensive error handling
- Automatic recovery
- Continuous diagnostics
- Production-ready Docker deployment
- Fully documented architecture
- Comprehensive testing

---

# Roadmap

## Version 3.1

Planned improvements include:

- Multi-vendor Hybrid Bridge framework
- Additional HVAC manufacturer support
- Automatic relay discovery
- Native web diagnostics interface
- Enhanced performance monitoring
- Additional Home Assistant entities

---

# Contributing

Contributions are welcome.

If you would like to improve York Hybrid Bridge, please read **CONTRIBUTING.md** before submitting pull requests.

Bug reports, feature requests and suggestions are always appreciated.

---

# License

York Hybrid Bridge is released under the **MIT License**.

See the **LICENSE** file for details.

---

# Acknowledgements

This project would not have been possible without:

- The Home Assistant community
- MQTT and Mosquitto developers
- Docker
- The many users who reverse-engineer unsupported hardware to keep local home automation alive

Special thanks to everyone who believes home automation should remain **local, reliable and under the user's control.**Local Home Assistant bridge for York air conditioners using Broadlink/TFIAC Wi-Fi modules with MQTT discovery, diagnostics and automatic recovery.
