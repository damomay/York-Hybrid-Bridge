# Climate Bridge 1.0.0-alpha.20

Climate Bridge `1.0.0-alpha.20` is the reconciled development baseline joining
the proven York Hybrid Bridge relay runtime and polished repository with the
newer Climate Bridge protocol-engineering work.

## Working transport

The Android York TFIAC Relay V2 is the only verified operational transport.
Home Assistant communicates with Climate Bridge through MQTT; Climate Bridge
sends local HTTP JSON to the Android relay; the Android application constructs
the native York/TFIAC command.

Native direct control is research only, disabled by default and guarded against
unverified transmission. Tablet removal is not part of this release.

## Reconciliation results

- Canonical identity and version: Climate Bridge `1.0.0-alpha.20`.
- Complete automated suite: 117/117 tests passed at Gate 8.
- Original polished repository baseline: 18/18 tests retained.
- Clean Docker build, network-free health check and clean shutdown passed.
- One-device Android-relay live regression passed for discovery, state,
  power, modes, 22 °C setpoint, fan speeds, vertical swing and restart safety.
- York decoder qualification: 14/14 approved fixtures passed.
- Existing observed library: 23 state responses, zero eligible native request
  candidates and zero verified/executable records.

## Protocol evidence boundary

Relay extraction records the bridge-to-relay HTTP JSON and relay response. It
does not expose the native command unless the Android relay itself returns
those bytes. Observed response packets remain non-executable evidence.

## Known limitations

- Android relay required.
- One configured/live-qualified York device only.
- No verified native command or direct-control path.
- No multiple-device or multi-vendor operation.
- Alpha status; preserve a working deployment and configuration for rollback.

## Next milestone

After reconciliation is closed, work proceeds in this order: native command
discovery and tablet removal, direct-communication qualification, controlled
single-device direct testing, then multiple-device support.

See `README.md`, `ROADMAP.md`, `CHANGELOG.md` and `docs/` for installation,
configuration, testing and troubleshooting.
