# Sprint 1 Completion Notes

## Completed

- Renamed the application to Climate Bridge.
- Reset versioning to `1.0.0-alpha.1`.
- Added `TransportBase`.
- Added `RelayTransport` using the proven tablet HTTP relay.
- Added the `YorkDirectTransport` scaffold.
- Added a transport factory selected from configuration.
- Reworked the bridge core to use `self.transport` rather than `self.relay`.
- Generalized bridge diagnostics from relay status to transport status.
- Preserved `relay_manager.py` as a compatibility import for older tooling.
- Preserved legacy `relay:` configuration parsing.
- Updated Docker identity and documentation.

## Deliberately not included

- Native York packet transmission.
- Native York state polling.
- Removal of the tablet runtime.
- Multiple-device support.

These belong to Sprint 2 and later phases.

## Hotfix 1

Corrected container startup validation to accept the new `transport:` configuration section while retaining legacy `relay:` compatibility.
