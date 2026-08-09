# Architecture

This document describes the accepted Climate Bridge 1.0.0 runtime.

```text
Home Assistant ←→ MQTT ←→ Climate Bridge
                              ↕
                guarded native command boundary
                              ↕
                 York/TCL TFIAC Wi-Fi module
```

The Android York relay and Relay v2 were used during earlier discovery and
qualification. They are not part of the 1.0.0 runtime path.

## Responsibilities

| Area | Current implementation |
| --- | --- |
| Coordination | `bridge.py` starts configuration, transport, MQTT, discovery, diagnostics, recovery, health, and polling. |
| Configuration | `configuration.py` normalizes YAML; `validate_config.py` enforces startup safety. |
| MQTT/Home Assistant | `mqtt_manager.py` publishes state and receives commands; `discovery_manager.py` publishes retained discovery definitions. |
| Native transport | `transport/factory.py` selects the native runtime; `transport/native_command_boundary.py` admits only supported guarded commands. |
| York protocol | `adapters/york/` implements state and command semantics; `protocols/york/` holds protocol records and tooling. |
| Reliability | `health_manager.py`, `diagnostics_manager.py`, and `recovery_manager.py` report and recover runtime health. |

Authenticated native reads are the state authority. A command must satisfy the
implemented V1 state, capability, and verification guards before the native
boundary will send it. Unsupported, ambiguous, or failed operations stop
locally without relay fallback.

## Boundaries

- One `Config`, transport, York adapter, MQTT identity, and York unit are
  supported per runtime.
- Multiple-device orchestration and broader vendor adapters are not complete.
- `config.yml` is private deployment state and remains untracked.
- Captures and logs may contain sensitive device/network data and require
  sanitization before storage or sharing.
- `VERSION` is the canonical source version consumed by `version.py`.

Historical architecture descriptions under `docs/history/` and
`docs/reconciliation/` record earlier relay and qualification stages; they do
not override this current architecture.
