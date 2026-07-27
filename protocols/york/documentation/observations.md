# Observed York TFIAC protocol behaviour

## Source

These notes consolidate observations from the earlier York Protocol Explorer and TFIAC APK instrumentation work. They are useful research evidence, but they are not substitutes for the original full captures.

## Confirmed workflow observations

- The Broadlink JNI network layer successfully initialized against the vendor network service.
- A `probe_list` exchange identified a TAC device with type `20014`.
- A `device_add` exchange completed successfully.
- The application then polled repeatedly at approximately three-second intervals.
- Device data frames observed during controlled tests used a leading byte of `0xBB`.

## Controlled byte-change observations

The following changes were observed while using MARK annotations in York Protocol Explorer:

| Action | Observed change | Confidence | Limitation |
|---|---|---:|---|
| Power on at 20 °C | byte index 7 changed from `0x21` to `0x31`; checksum also changed | observed | Full frame and direction must be re-imported before encoder use |
| Set temperature to 20.5 °C | byte index 9 changed from `0x00` to `0x02` | observed | Temperature encoding needs additional captures across the supported range |

Byte indexes above are zero-based indexes as recorded during the earlier analysis. They must be checked against the original log before being treated as canonical.

## Known unknowns

- Exact full native state-request frame.
- Request sequencing/session fields.
- Checksum algorithm and checksum coverage.
- Whether polling requires prior discovery, authentication or device-add state.
- Complete mapping for power, mode, target temperature, current temperature, fan and swing.
- Packet direction and response correlation fields.

## Promotion rule

An observation may be promoted to a verified packet-library entry only after the complete raw frame, source log, action context and expected result have been added under `captures/`.
