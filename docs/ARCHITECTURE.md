# Architecture

This document describes Climate Bridge `1.0.0-alpha.20`.

## Current working data path

```text
Home Assistant
    ↕ MQTT discovery, commands and state
Climate Bridge core (`bridge.py`)
    ↕ `TransportBase`
Relay transport (`transport/relay_transport.py`)
    ↕ HTTP JSON
Android York TFIAC Relay V2
    ↕ native York/TFIAC traffic
York Wi-Fi module and air conditioner
```

The Android application is a required part of the verified path. Relay
extraction can record the HTTP JSON sent by Climate Bridge and the relay's HTTP
response, but it cannot claim to contain the native York command created
inside the Android application.

## Runtime responsibilities

| Area | Current implementation |
| --- | --- |
| Coordination | `bridge.py` starts configuration, transport, MQTT, discovery, diagnostics, recovery, health and polling. |
| Configuration | `configuration.py` loads and normalizes the YAML file. `validate_config.py` applies startup safety validation. |
| MQTT | `mqtt_manager.py` handles broker lifecycle, state publication and command subscriptions. |
| Home Assistant | `discovery_manager.py` publishes retained MQTT Discovery definitions. |
| Transport | `transport/base.py` defines the interface; `transport/factory.py` selects relay or guarded York-direct transport. |
| York semantics | `adapters/york/` maps Home Assistant commands and decoded York state. |
| Reliability | `health_manager.py`, `diagnostics_manager.py` and `recovery_manager.py` report and recover runtime health. |
| Protocol evidence | `protocols/york/` stores sanitized observed evidence, fixtures, schemas and documentation. |

## Transport boundary

`transport.type: relay` and its compatibility alias `tablet_relay` select the
verified `RelayTransport`.

`transport.type: york_direct` and its compatibility alias `york` select
research scaffolding guarded by both configuration validation and packet
verification rules. Presence in the factory is not proof that the transport
is ready for operational use.

Observed `0xBB`-headed frames and all 14 approved decoder fixtures are device
state responses. The Phase 8 request hunter produced no eligible native
request candidates. Response classification never makes a packet executable.

## Repository boundaries

- `config.example.yml` is the committed sanitized example.
- `config.yml` is local deployment state and must remain untracked.
- `qualification-reports/` and protocol report directories retain only
  placeholder documentation; generated reports are ignored.
- Captures containing device identifiers or credentials must be sanitized
  before they enter the evidence store.
- `VERSION` is the canonical version source consumed by `version.py`.

## Current scalability boundary

The current runtime creates one `Config`, one transport, one York adapter and
one MQTT device identity. Multiple-device orchestration is not implemented.
The adapter/transport separation prepares for later work but must not be
described as completed multi-device or multi-vendor support.
