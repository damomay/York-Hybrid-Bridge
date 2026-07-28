# Tablet removal Phase 1 — Native command discovery

Status: LOCAL EXIT GATE PASS — publication pending.

Canonical starting commit:
`3b12087471156d0c69f6908f8394488ab169eff1`

The working `climate_bridge_1a20p11` relay deployment remains unchanged and is
the rollback path.

## Evidence audit

- The 23 imported `0xBB` records are device state responses.
- The request hunter has zero eligible native controller-request candidates.
- Relay extraction records Bridge-to-Android HTTP JSON, not the native York
  bytes constructed inside Android.
- Re-running the request hunter on the same evidence cannot satisfy Phase 1.

## First bounded implementation

Phase 1 adds a structured Android capture contract and guarded importer. A
capture is accepted only when it preserves:

- controller-to-device direction;
- UTC timestamp;
- the observed transport boundary (UDP/TCP endpoint or Broadlink SDK target);
- action marker and expected state;
- exact raw frame bytes; and
- source artifact digest, tool and hook point.

Every imported record is forced to `observed` and
`safe_to_transmit: false`. The importer opens no sockets and sends no packets.
Private capture outputs default to `/reports/york-native-evidence` and must not
be committed.

## Recovered Relay v2 evidence

The recovered **York TFIAC Relay v2** source implements `POST /command` and
`GET /transactions`. Its transaction history preserves the native request
immediately after `setSplitAirconInfo()` and before the existing Broadlink SDK
passthrough call. Relay exports use timezone-naive tablet-local timestamps, so
the importer requires an explicit IANA source timezone. The SDK target MAC is
preserved as the endpoint boundary; no unobserved device IP or port is invented.

The Phase 11 transaction export contains five successfully verified commands:

1. power on in cool mode at 22 °C;
2. target temperature 25 °C;
3. high fan;
4. vertical swing; and
5. power off.

All five official-parser frames are 31 bytes, start with `0xBB`, and have a
final byte equal to the XOR of the preceding 30 bytes. Each SDK response has
code zero, and every requested state matches the subsequent read-back. The
offline importer admitted all five while reporting zero sockets and zero
packets transmitted.

The recovered pure-Python prototype reproduces the content and checksum of all
five frames but currently inserts one extra zero byte, producing 32 bytes.
That prototype is historical evidence only and must not be used for live
transmission until its length defect is corrected and separately qualified.

## Exit gate

Phase 1 remains open until at least one complete controller-to-device request:

1. has reproducible source provenance;
2. imports through the guarded pipeline;
3. remains non-executable;
4. has framing and checksum independently reviewed; and
5. correlates with one marked action and the resulting device state.

No live native transmission is authorized by Phase 1.

## Gate result

The local Phase 1 exit gate passes:

- recovered Relay v2 source identifies the exact native-parser and SDK hook;
- the running relay export is content-addressed and imports reproducibly;
- five controller requests remain `observed` and non-executable;
- all five 31-byte frames pass independent framing and XOR review; and
- the user-observed physical actions agree with the SDK read-back verification.

An exact binary hash comparison with the APK installed on the tablet has not
been performed. The recovered source is therefore corroborating source
provenance, not a claim of binary identity. Stage 2 remains locked until the
Phase 1 branch is reviewed and merged.
