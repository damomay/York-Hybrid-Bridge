# 1.0.0 — Sprint 3.2.1 First York Stable Release

- Promoted the exact functionally accepted Beta.1 command implementation.
- Added final supported-function, upgrade and post-deployment guidance.
- Recorded the successful eight-step acceptance test and cumulative connection
  stability evidence.
- Made no protocol, command-manager, packet-encoding or transport-allowlist
  expansion.

See `V1_0_0_RELEASE_AND_UPGRADE_GUIDE.md` and
`V1_0_0_ACCEPTANCE_AND_STABILITY_EVIDENCE.md`.

## 1.0.0-beta.1 — Sprint 3.2.0 Consolidated First-Unit Candidate

- Froze the physically qualified first-unit command boundary without widening
  packet or transport allowlists.
- Removed Fan Medium and five unqualified feature switches from Home Assistant
  discovery.
- Added the audited support matrix and one pre-checked end-to-end acceptance
  sequence.

See `SPRINT_3_2_0_CAPABILITY_AUDIT_AND_BETA_SCOPE.md`.

## 1.0.0-alpha.92 — Sprint 3.1.63 General Cool Qualified-Fan Temperature Encoder

- Extended the formula-derived Cool/Swing Off encoder to Fan Auto, Low, and High.
- Closed the transport allowlist to 93 canonical target-state frames.
- Preserved the source fan through cached-state, fresh-read, write, immediate
  verification, and delayed verification boundaries.
- Retained one write, four UDP sends, zero retries, no fallback, and critical
  unexpected-Power-Off handling.

## 1.0.0-alpha.91 — Sprint 3.1.62 General Cool/Fan Auto Temperature Encoder

- Replaced the temporary source-edge matrix with one formula-derived encoder.
- Added 16.0–31.0 °C support in exact 0.5 °C increments.
- Preserved exact cached/fresh nine-field guards, one write, four UDP sends,
  zero retries, no fallback, delayed verification, and critical Power Off.

See `SPRINT_3_1_62_GENERAL_COOL_FAN_AUTO_TEMPERATURE_ENCODER.md`.

# 1.0.0-alpha.88 — Sprint 3.1.59 Official-SDK Cool 20 to 22 °C Fan Auto Qualification

- Added Capture 10's exact official-SDK Cool 20.0 → 22.0 °C command.
- Preserved all nine controlled source and target fields.
- Retained fresh pre-read, one write, zero retries, delayed verification, and critical Power Off handling.
- Kept every other uncaptured target from the 20.0 °C source blocked.

See `SPRINT_3_1_59_OFFICIAL_SDK_COOL_20_TO_22_FAN_AUTO_QUALIFICATION.md`.

# 1.0.0-alpha.87 — Sprint 3.1.58 Official-SDK Cool 20.5 to 20 °C Fan Auto Qualification

- Added Capture 11's exact official-SDK Cool 20.5 → 20.0 °C command.
- Required the exact nine-field source and fresh authenticated pre-read.
- Preserved one write, zero retries, delayed read-only verification, and
  critical unexpected-Power-Off handling.
- Kept every other uncaptured target from the 20.5 °C source blocked.

See `SPRINT_3_1_58_OFFICIAL_SDK_COOL_20_5_TO_20_FAN_AUTO_QUALIFICATION.md`.

# 1.0.0-alpha.86 — Sprint 3.1.57 Official-SDK Cool 20 to 20.5 °C Fan Auto Qualification

- Added Capture 10's exact official-SDK Cool 20.0 → 20.5 °C command.
- Required the exact nine-field source and fresh authenticated pre-read.
- Preserved one write, zero retries, delayed read-only verification, and
  critical unexpected-Power-Off handling.
- Kept the reverse edge and all other uncaptured Cool/Fan Auto targets blocked.

See `SPRINT_3_1_57_OFFICIAL_SDK_COOL_20_TO_20_5_FAN_AUTO_QUALIFICATION.md`.

# 1.0.0-alpha.85 — Sprint 3.1.56 Official-SDK Auto/FEEL 20 °C to Cool Qualification

- Added Capture 9's exact Auto/FEEL 20 °C → Cool 20 °C frame generated
  offline by York's official native parser.
- Required exact nine-field authoritative, fresh pre-read and result shapes.
- Preserved Fan Auto, Swing Off, Display On and all optional-feature fields.
- Preserved one write, zero retries, no fallback, delayed read-only
  verification and critical unexpected-Power-Off detection.
- Kept every other uncaptured Auto source and Auto 20 °C exit blocked.

See `SPRINT_3_1_56_OFFICIAL_SDK_AUTO_FEEL_20_TO_COOL_QUALIFICATION.md`.

# 1.0.0-alpha.84 — Sprint 3.1.55 Auto/FEEL 20 °C Program Qualification

- Added the physically observed Auto/FEEL 20 °C post-write result to the
  explicit program allowlist for the existing Heat 23 °C → Auto edge.
- Preserved the exact official-SDK command, nine-field Heat source guard and
  eight exact non-temperature Auto result fields.
- Preserved one write, zero retries, no fallback, delayed read-only
  verification and critical unexpected-Power-Off detection.
- Kept arbitrary Auto values and every uncaptured Auto 20 °C exit blocked.

See `SPRINT_3_1_55_AUTO_FEEL_20_PROGRAM_QUALIFICATION.md`.

# 1.0.0-alpha.83 — Sprint 3.1.54 Official-SDK Cool 23 °C to 21 °C Fan Auto Qualification

- Added Capture 8's isolated Cool 23 °C → Cool 21 °C / Fan Auto / Swing Off
  command using the official native parser's target encoding.
- Required exact nine-field authoritative and fresh pre-read source guards.
- Preserved Fan Auto, Swing Off, Display On and all optional-feature fields.
- Added delayed read-only verification, one write, zero retries, no fallback
  and immediate critical failure on unexpected Power Off.
- Kept every other Fan Auto temperature target blocked.

See `SPRINT_3_1_54_OFFICIAL_SDK_COOL_23_TO_21_FAN_AUTO_QUALIFICATION.md`.

# 1.0.0-alpha.79 — Sprint 3.1.50 Official-SDK Auto/FEEL 21 °C to Cool Qualification

- Added Capture 5's exact 31-byte Auto/FEEL → Cool frame generated offline by
  York Write Packet Lab v1 through the official TCL/Broadlink SDK.
- Enabled only Power On / Auto/FEEL / 21 °C / Fan Auto / Swing Off → Cool /
  21 °C / Fan Auto / Swing Off with all optional fields unchanged.
- Required all nine source and target fields, including the exact live
  Auto/FEEL status value and restored applicable Cool setpoint.
- Preserved one write, zero retries, delayed read-only verification and
  immediate critical failure on unexpected Power Off.
- Removed Alpha.72's superseded Cool 22 °C frame from the transport allowlist.

See `SPRINT_3_1_50_OFFICIAL_SDK_AUTO_FEEL_21_TO_COOL_QUALIFICATION.md`.

# 1.0.0-alpha.78 — Sprint 3.1.49 Official-SDK Heat 23 °C to Auto/FEEL Qualification

- Added the exact 31-byte Heat → Auto/FEEL frame generated offline by York
  Write Packet Lab v1 through the official TCL/Broadlink SDK.
- Enabled only Power On / Heat / 23 °C / Fan Auto / Swing Off → Auto/FEEL /
  Fan Auto / Swing Off with all optional fields unchanged.
- Required all nine Heat source fields and bounded Auto's dynamic status
  temperature to the native 16.0–31.5 °C half-degree representation.
- Preserved one write, zero retries, delayed read-only verification and
  immediate critical failure on unexpected Power Off.
- Kept the older Heat 25 °C candidate and every nearby Heat source blocked.

See `SPRINT_3_1_49_OFFICIAL_SDK_HEAT_23_TO_AUTO_FEEL_QUALIFICATION.md`.

# 1.0.0-alpha.77 — Sprint 3.1.48 Official-SDK Fan-only to Heat Qualification

- Added the exact 31-byte Fan-only → Heat frame generated offline by York
  Write Packet Lab v1 through the official TCL/Broadlink SDK.
- Enabled only Power On / Fan-only / Fan Auto / Swing Off → Heat / 23 °C /
  Fan Auto / Swing Off with all optional fields unchanged.
- Kept Fan-only's source temperature non-applicable while requiring all nine
  target fields once Heat becomes authoritative.
- Preserved one write, zero retries, delayed read-only verification and
  immediate critical failure on unexpected Power Off.
- Kept every other Fan-only exit and the retired Alpha.71 packet blocked.

See `SPRINT_3_1_48_OFFICIAL_SDK_FAN_ONLY_TO_HEAT_QUALIFICATION.md`.

# 1.0.0-alpha.76 — Sprint 3.1.47 MQTT Non-applicable Setpoint Reset

- Reset Home Assistant's target setpoint with the documented retained `None`
  payload whenever Dry or Fan-only is authoritative.
- Apply the reset on the first poll after restart as well as live mode changes.
- Prevent `NoneType.__format__` warnings during numeric-to-non-applicable
  temperature transitions.
- Restore numeric target state and activity publication in Heat and Cool.
- Preserve the current-temperature, command-containment and one-write safety
  behavior qualified in Alpha.75.

See `SPRINT_3_1_47_MQTT_NON_APPLICABLE_SETPOINT_RESET.md`.

# 1.0.0-alpha.75 — Sprint 3.1.46 Dry and Fan-only Temperature Semantics

- Confirmed from new Write Packet Lab captures that neither Dry nor Fan-only
  exposes a user-adjustable target temperature.
- Removed target temperature from publication, control and Dry → Fan-only
  source/result verification in both non-temperature modes.
- Preserved the exact official-SDK Fan-only write, live Fan Auto source state,
  eight applicable verification fields, one write and zero retries.
- Confirmed Fan-only High as native `wind=5` / status nibble `0x30`.
- Corrected odd indoor-temperature status bytes to match the SDK's observed
  whole-degree result (`0x57` → 15 °C).

See `SPRINT_3_1_46_DRY_AND_FAN_ONLY_TEMPERATURE_SEMANTICS.md`.

# 1.0.0-alpha.74 — Sprint 3.1.45 Fan-only Temperature Semantics

- Confirmed from Write Packet Lab Capture 2 that native Fan-only reports no
  selectable target temperature; its decoded 23 °C field is a placeholder.
- Excluded target temperature from Fan-only publication and from the eight-field
  Fan-only post-write verification while retaining the exact nine-field Dry
  source guard.
- Decoded the independent SDK `indoorTemp` status field and publishes the
  measured room temperature to Home Assistant.
- Kept Fan-only temperature commands fail-closed, one write, zero retries, the
  30-second read-only verification window and critical Power Off detection.

See `SPRINT_3_1_45_FAN_ONLY_TEMPERATURE_SEMANTICS.md`.

# 1.0.0-alpha.73 — Sprint 3.1.44 Official-SDK Fan-only Qualification

- Added the exact 31-byte Fan-only frame generated offline by York Write
  Packet Lab v1 through the official TCL/Broadlink SDK.
- Enabled only Dry / 17 °C / Fan Auto / Swing Off → Fan-only with the other
  six guarded feature/power fields unchanged.
- Kept the frame in a dedicated qualification allowlist rather than the
  historical remaining-mode matrix.
- Required one write, zero retries, nine-field post-read verification and the
  existing 30-second delayed polling window.
- Preserved immediate critical failure for unexpected Power Off.
- Kept the retired Alpha.71 frame permanently blocked and every Fan-only exit
  disabled.

See `SPRINT_3_1_44_OFFICIAL_SDK_FAN_ONLY_QUALIFICATION.md`.

## 1.0.0-alpha.72 — Sprint 3.1.43 Fan-only Containment and Delayed Verification

- Retired the historical Fan-only candidate after the live Alpha.71 command
  eventually switched the physical unit Off.
- Removed the retired frame from every production transport allowlist.
- Disabled Dry → Fan-only and Fan-only → Heat before client creation.
- Retained only Auto → Cool, Cool → Dry and Heat → Auto in the active matrix.
- Added read-only post-write polling across a full 30-second window for those
  retained edges without retrying the control write.
- Added an immediate critical verification failure for unexpected Power Off.
- Preserved bounded dynamic Auto and Dry status handling and all previously
  qualified power, Heat/Cool, temperature, fan and swing paths.

See `SPRINT_3_1_43_FAN_ONLY_CONTAINMENT_DELAYED_VERIFICATION.md`.

## 1.0.0-alpha.71 — Sprint 3.1.42 Dry Dynamic Status Correction

- Accepts bounded decoder-representable Dry status temperatures from
  16.0–31.5 °C in half-degree steps.
- Corrects both Cool → Dry post-read verification and Dry → Fan-only source
  validation for the live Dry / 21 °C state.
- Keeps the canonical Dry command unchanged and all other fields exact.
- Keeps Dry temperature commands unsupported.
- Retains four UDP sends, zero retries, no fallback and real-client transport
  boundary verification.

See `SPRINT_3_1_42_DRY_DYNAMIC_STATUS_MODE_MATRIX_CORRECTION.md`.

## 1.0.0-alpha.70 — Sprint 3.1.41 Real-Client Mode Transport Integration

- Connected only the five validated remaining-mode candidates to the real
  Broadlink power-write client through a dedicated byte-exact boundary.
- Kept those candidates separate from immutable captures and general
  parameterised power-command sets.
- Revalidates membership and XOR integrity when the encrypted write packet is
  constructed.
- Added production-client regressions covering construction, authenticated
  pre-read, exact encrypted write, delayed verification read and four sends.
- Retains Alpha.69's bounded dynamic Auto/FEEL ambient validation, ordered
  edges, zero retries and no fallback.

# 1.0.0-alpha.69 — Sprint 3.1.40 Auto/FEEL Dynamic Ambient Matrix

- Reclassified Auto/FEEL's decoded temperature as a dynamic ambient/status
  field after live reads followed the room from 22 °C to 23 °C.
- Range-validates only that Auto field from 16.0–31.5 °C in 0.5 °C increments.
- Keeps the other eight Auto fields and all nine non-Auto fields exact.
- Keeps the captured Auto command and every non-Auto target unchanged.
- Retains ordered edges, four UDP sends, zero retries and no fallback.
- Keeps Auto temperature commands unsupported.

# 1.0.0-alpha.68 — Sprint 3.1.39 Auto/FEEL 22 °C Matrix Correction

- Corrected both Auto/FEEL matrix endpoints from 23 °C to the live-confirmed
  fixed 22 °C authoritative state.
- Updated the canonical Auto command from temperature byte `0x08` to `0x09`
  and recalculated its XOR checksum.
- Required the live Auto source to decode with `status_byte=0x06`; the obsolete
  23 °C source remains a zero-write safety stop.
- Kept Cool, Dry, Fan-only and Heat target shapes unchanged.
- Retained exact ordered edges, nine-field pre/post verification, four UDP
  sends, zero retries and no fallback.
- Kept Auto temperature commands unsupported because FEEL comfort adjustments
  were not represented by the Wi-Fi module's authoritative state.

# 1.0.0-alpha.67 — Sprint 3.1.38 Grouped Remaining Modes Matrix

- Added the exact ordered Auto → Cool → Dry → Fan-only → Heat → Auto matrix.
- Anchored every complete target state to the labelled TFIAC Modes log.
- Required exact nine-field sources, fresh pre/post reads, four sends and zero
  retries for each edge.
- Kept skipped edges, altered settings and feature flags fail-closed.
- Isolated candidate frames from immutable captured replay allowlists pending
  physical acceptance.

# 1.0.0-alpha.66 — Sprint 3.1.37 Post-Swing Fan Compatibility Qualification

- Added one exact Heat / 22.5 °C / Low / decoded Horizontal → High / Off edge
  for Alpha.65's observed post-swing source.
- Reuses the fingerprint-locked Alpha.63 High / Off target frame.
- Requires exact nine-field relay/direct source agreement and nine-field target
  verification with four sends, zero retries and no fallback.
- Keeps every nearby state and Horizontal / High → Low outside the allowlist.
- Corrected the startup swing capability banner to describe the grouped Heat
  matrix.

# 1.0.0-alpha.65 — Sprint 3.1.36 Grouped Swing Qualification Matrix

- Added the exact ordered Off → Vertical → Both → Horizontal → Off path at
  On / Heat / 22.5 °C / Fan Low.
- Derived case-specific targets only from independently qualified axis fields
  and the proven 21.5→22.5 °C temperature delta.
- Required exact source edges; skipped swing transitions remain fail-closed.
- Retained fresh nine-field pre/post reads, four UDP sends, zero retries and no
  fallback for every command.
- Kept the 22.5 °C Both and Horizontal candidates outside the immutable
  capture-replay allowlist pending physical acceptance.
- Reused Alpha.64's physically verified Low↔High / Swing Off fan pair for the
  final two acceptance steps.

# 1.0.0-alpha.64 — Sprint 3.1.35 Grouped Fan Qualification Matrix

- Added exact Cool / 22.5 °C / Low↔High / Swing Off qualification frames.
- Derived Cool frames only through Alpha.62's proven Heat↔Cool mode delta.
- Preserved Alpha.63's physically verified Heat fan pair unchanged.
- Added a six-command continuous acceptance sequence with per-command guards.
- Retained nine-field pre/post reads, four UDP sends, zero retries and no
  fallback for every individual transition.
- Kept all other Cool fan, temperature, swing and feature shapes fail-closed.
- Kept immutable capture-replay allowlists unchanged.

# 1.0.0-alpha.63 — Sprint 3.1.34 Fan High / Swing Off Qualification

- Added one exact Heat / 22.5 °C / Low / Off → High / Off qualification.
- Derived candidate command byte `0x05` only from the independently proven
  Low/Off byte `0x02` and Vertical Low→High delta `0x03`.
- Isolated the candidate from the immutable captured replay allowlist.
- Added the exact canonical Low/Off return frame for the matching High state.
- Retained nine-field pre/post guards, four UDP sends, zero retries and no
  fallback.
- Kept every nearby mode, setpoint, swing, fan and feature shape fail-closed.

# 1.0.0-alpha.62 — Sprint 3.1.33 Parameterised Running Mode Control

- Added native running Heat↔Cool control from qualified authoritative states.
- Preserved target temperature, fan and swing in complete York target frames.
- Required both source and target states to match canonical qualified shapes.
- Reproduced both captured 25 °C / High / Vertical running-mode anchors.
- Retained nine-field pre/post guards, four UDP sends, zero retries and no
  fallback.
- Kept unqualified, changed and same-mode requests fail-closed before writing.
- Kept immutable capture-replay allowlists unchanged.

# 1.0.0-alpha.61 — Sprint 3.1.32 Parameterised Power-Off Control

- Added native On → Off control from qualified authoritative live states.
- Preserved mode, target temperature, fan and swing in complete York frames.
- Cleared only the captured power bit and recalculated the York frame XOR.
- Reproduced the captured Heat / 25 °C / High / Vertical Power-Off anchor.
- Retained nine-field pre/post guards, four UDP sends, zero retries and no
  fallback.
- Kept unqualified state shapes fail-closed before client creation.
- Kept immutable capture-replay allowlists unchanged.

# 1.0.0-alpha.60 — Sprint 3.1.31 Parameterised Power-On Control

- Added native Off → On control from qualified authoritative stored states.
- Preserved target temperature, fan and swing in complete York target frames.
- Reused the exact captured Heat / 21.5 °C / Low / Off command for the
  Alpha.59 physical baseline.
- Retained nine-field pre/post guards, four UDP sends, zero retries and no
  fallback.
- Kept unqualified state shapes fail-closed before client creation.
- Replaced stale power-path `relay state` diagnostics with `authoritative
  direct state`.

# 1.0.0-alpha.58 — Sprint 3.1.29 Relay-Free Command Boundary

- Replace the live Relay HTTP command transport with a local fail-closed
  boundary whenever authenticated direct state authority is enabled.
- Reject native safe-stops and unqualified commands without Relay calls or
  retries, then republish the last confirmed direct state.
- Accept the physically verified Alpha.57 configuration unchanged while
  treating its Relay fallback field as migration-only metadata.
- Preserve all native packet allowlists, direct-state authority, polling,
  outage recovery and failure-counter behavior.

# 1.0.0-alpha.57 — Sprint 3.1.28 Poll-Failure Counter Correction

- Cap threshold-facing poll-failure logs and retry diagnostics at the
  configured offline threshold during an extended outage.
- Reset the displayed failure sequence after a successful direct read.
- Preserve Alpha.56 timeout, availability, recovery, native-control and Relay
  fallback behaviour unchanged.

## 1.0.0-alpha.56 — Sprint 3.1.27 Tablet-Free Restart and Recovery

- Keep the Home Assistant climate entity unavailable until a fresh direct LAN
  state read succeeds after process startup or MQTT reconnect.
- Recover availability and state automatically without Relay v2 state access.
- Report direct-state interruption accurately in health and recovery sensors.
- Preserve every Alpha.55 native packet, allowlist and Relay fallback boundary.

## 1.0.0-alpha.55 — Sprint 3.1.26 Direct-State Authority

- Made authenticated direct LAN reads authoritative for Home Assistant state.
- Removed Relay v2 `/state` polling from the direct-enabled runtime path.
- Required a fresh direct read before command deferral, routing or guards.
- Discarded Relay command HVAC state and refreshed from the York module before
  publishing command results.
- Retained Relay v2 only as command fallback for unqualified requests.
- Preserved every Alpha.54 native write envelope without packet changes.

# 1.0.0-alpha.54 — Sprint 3.1.25 Native Heat Horizontal Axis Control

- Enabled normal guarded Home Assistant Off → Horizontal and Horizontal → Off
  control at Heat / 21.5 °C / Fan Low.
- Reused the two exact frames physically qualified in Alpha.53.
- Preserved nine-field Relay/direct guards, one write, four UDP sends, zero
  retries and nine-field post-write verification.
- Retained Relay v2 fallback for every other Horizontal/Both state or request.
- Removed the Alpha.53 qualification tool from the executable container.

# 1.0.0-alpha.53 — Sprint 3.1.24 Heat Horizontal Axis Qualification

- Added guarded one-shot Heat / 21.5 °C / Fan Low Off → Horizontal and
  Horizontal → Off native qualification cases.
- Locked the exact Relay v2 `0x08` Horizontal-axis and return-to-Off frames.
- Preserved nine-field pre/post reads, one write, four UDP sends, zero retries,
  no automatic restore and separate confirmation tokens.
- Kept normal Home Assistant Horizontal routing on Relay v2.
- Kept Alpha.49's rejected `0x20` status-bit frame outside the write allowlist.

# 1.0.0-alpha.52 — Sprint 3.1.23 Native Dry Horizontal Axis Control

- Enabled normal guarded Home Assistant Vertical → Both and Both → Vertical
  control at Dry / 21 °C / Fan Low.
- Reused the two exact frames physically qualified in Alpha.51.
- Preserved nine-field Relay/direct guards, one write, four UDP sends, zero
  retries and nine-field post-write verification.
- Retained Relay v2 fallback for every other Horizontal/Both state or request.
- Removed the Alpha.51 qualification tool from the executable container.

# 1.0.0-alpha.51 — Sprint 3.1.22 Dry-Mode Horizontal Axis Qualification

- Added guarded one-shot Vertical → Both and Both → Vertical cases at
  Dry / 21 °C / Fan Low using exact, physically confirmed Relay v2 frames.
- Preserved the independent command-side Horizontal flag `0x08` while avoiding
  Heat-mode firmware masking of physical Vertical movement.
- Removed the Alpha.50 Heat-specific tool from the executable container.
- Retained nine-field pre/post reads, one write, four UDP sends, zero retries,
  no automatic restore, and Relay v2 normal routing.

# 1.0.0-alpha.50 — Sprint 3.1.21 Independent Horizontal Axis Qualification

- Replaced the failed Alpha.49 status-bit inference with the exact Relay v2
  command-side Horizontal flag `0x08`.
- Added guarded one-shot Vertical → Both and Both → Vertical cases at
  Heat / 21.5 °C / Fan Low.
- Preserved Vertical while enabling or disabling only the Horizontal axis.
- Removed Alpha.49's failed candidate from the write allowlist and executable
  package paths.
- Retained nine-field pre/post reads, one write, four UDP sends, zero retries,
  no automatic restore, and Relay v2 normal routing.

# 1.0.0-alpha.49 — Sprint 3.1.20 Horizontal Swing Qualification

- Tested an inferred one-shot candidate for Heat / 21.5 °C / Fan Low /
  Vertical → Horizontal; physical qualification showed it commanded Off.
- Added the already-qualified 21.5 °C Vertical return frame.
- Locked exact confirmation tokens, nine-field pre/post reads, one write,
  four UDP sends and zero retries.
- Kept normal Horizontal and Both Home Assistant routing on Relay v2.

# 1.0.0-alpha.48 — Sprint 3.1.19 Guarded Native Swing Control

- Enabled normal guarded Swing Vertical ↔ Off control for On/Heat/Fan Low.
- Reused the qualified `0x3A` Vertical and `0x02` Off complete-state frames at
  the current 16–30 °C whole- or half-degree setpoint.
- Preserved temperature and Fan Low with exact nine-field pre/post
  verification.
- Retained one write, four UDP sends, zero automatic retries and Relay v2
  fallback.
- Kept Horizontal, Both, Fan High and unqualified operating states on Relay v2.

# 1.0.0-alpha.47 — Sprint 3.1.18 Guarded Native Fan Control

- Enabled normal guarded Fan Low ↔ High control for On/Heat/Swing Vertical.
- Reused the qualified `0x3A` Low and `0x3D` High complete-state frames at the
  current 16–31 °C whole- or half-degree setpoint.
- Preserved temperature and Vertical swing with exact nine-field pre/post
  verification.
- Retained one write, four UDP sends, zero automatic retries and Relay v2
  fallback.
- Kept Auto, Medium and all unqualified operating states on Relay v2.

# 1.0.0-alpha.46 — Sprint 3.1.17 Half-Degree Temperature Control

- Enabled guarded native 0.5 °C targets across 16–31 °C for qualified
  Heat/High/Vertical and Heat/Low/Vertical states.
- Reused the established byte-11 `0x02` half-degree flag while preserving
  state bytes `0x3D` and `0x3A`.
- Retained nine-field pre/post verification, one write, four UDP sends, zero
  automatic retries and Relay v2 fallback.
- Rejected quarter-degree and out-of-range targets before client/socket use.

# 1.0.0-alpha.45 — Sprint 3.1.16 Parameterised Low/Vertical Control

- Enabled normal guarded Heat/Fan Low/Swing Vertical temperature control for
  whole-degree targets from 16 through 31 °C.
- Promoted the Alpha.44 parameterised generator after offline 16/16 validation
  and successful physical 25 → 26 → 25 °C qualification.
- Retained exact nine-field pre/post verification, one write, four UDP sends
  and zero automatic retries.
- Retained Relay v2 fallback for invalid targets, live-state mismatches and
  direct-path failures.

# 1.0.0-alpha.44 — Sprint 3.1.15 Parameterised Low/Vertical Temperature

- Extended the Heat/Fan Low/Swing Vertical generator across whole-degree
  targets from 16 through 31 °C.
- Preserved byte-for-byte matches with the Alpha.42 24 and 25 °C captures.
- Added comfortable guarded one-shot cases for 25 → 26 °C and 26 → 25 °C.
- Kept normal Home Assistant Low/Vertical routing limited to 24 ↔ 25 °C.
- Retained one write, four UDP sends, zero retries and exact nine-field
  pre/post verification for each live case.

# 1.0.0-alpha.43 — Sprint 3.1.14 Guarded Low/Vertical Temperature Control

- Integrated the physically qualified 25 → 24 °C and 24 → 25 °C
  Heat/Fan Low/Swing Vertical transitions into normal Home Assistant control.
- Retained nine-field Relay and direct guards, one write, four UDP sends, zero
  retries, and nine-field post-write verification.
- Preserved Relay v2 fallback for every other Low/Vertical transition.
- Kept the Alpha.42 one-shot qualification tool isolated from normal routing.

# 1.0.0-alpha.42 — Sprint 3.1.13 Low/Vertical Temperature Qualification

- Added exact physically verified Relay fixtures for Heat/Fan Low/Swing
  Vertical transitions 25 → 24 °C and 24 → 25 °C.
- Locked both 31-byte frames, SHA-256 fingerprints and York XOR checksums.
- Added two guarded one-shot live cases with nine-field pre/post verification,
  one write, zero retries and no automatic restore.
- Kept normal Low/Vertical Home Assistant temperature commands on Relay v2.

# 1.0.0-alpha.41 — Sprint 3.1.12 Guarded Temperature Control

- Integrated the qualified 16–31 °C Heat/High/Vertical generator into normal
  Home Assistant temperature control.
- Retained exact nine-field Relay and direct guards, one write, zero retries,
  and nine-field post-write verification.
- Preserved the earlier Low/Swing Off temperature path.
- Added explicit zero-client Relay fallback coverage for the occupied-room
  Heat/23 °C/Fan Low/Swing Vertical state.

# 1.0.0-alpha.40 — Sprint 3.1.11 Temperature Boundary Qualification

- Confirmed the physical setpoint range is 16 through 31 °C inclusive.
- Added exact Relay-backed boundary fixtures for 16, 17, 30 and 31 °C.
- Extended the whole-degree generator across all sixteen supported setpoints.
- Added two guarded live endpoint cases: 30 → 31 °C and 31 → 16 °C.
- Kept normal MQTT temperature control and Relay v2 fallback unchanged.

# 1.0.0-alpha.39 — Sprint 3.1.10 Temperature Encoding Qualification

- Added exact Relay-backed Heat temperature fixtures for 24, 25 and 26 °C.
- Added a capture-bounded generator proving byte 9 equals `31 - setpoint`.
- Added guarded one-shot qualification with nine-field pre/post verification.
- Kept normal MQTT temperature control and Relay v2 fallback unchanged.

# 1.0.0-alpha.38 — Sprint 3.1.9 Guarded Running Mode Control

- Integrates the Alpha.37-qualified Heat to Cool and Cool to Heat transitions
  into normal Home Assistant MQTT control.
- Reuses the exact captured and fingerprint-locked target-state frames.
- Selects Power On versus running-mode cases from the complete nine-field Relay
  state before opening a direct client.
- Retains the direct nine-field pre-read, one write, zero retries, and 9/9
  post-read verification.
- Preserves automatic Relay v2 fallback for every unqualified state or direct
  failure.
- Keeps fan, swing, feature, pending-temperature power-on, and all other
  unqualified commands on Relay v2.

# 1.0.0-alpha.37 — Sprint 3.1.8 Running Mode Change Qualification

- Adds qualification-only `heat-to-cool` and `cool-to-heat` cases.
- Locks the exact Relay v2 transaction #4 and #5 frames from 2026-07-30.
- Confirms those frames exactly reuse the already qualified Cool and Heat
  target-state commands.
- Requires exact nine-field live preconditions and post-write verification.
- Keeps one write, zero retries, no automatic restore, and case-specific
  confirmation tokens.
- Keeps both cases disconnected from normal MQTT mode control.

# 1.0.0-alpha.36 — Sprint 3.1.7 Guarded Power Off from Heat Control

- Integrates the Alpha.35-qualified `off-heat` frame into normal Home Assistant
  MQTT power control.
- Selects the distinct Cool-off or Heat-off fixture from the exact nine-field
  Relay state before opening a direct client.
- Retains the direct nine-field pre-read, one write, zero retries, and 9/9
  post-read verification.
- Preserves automatic Relay v2 fallback for every unqualified state or direct
  failure.
- Does not add native Heat/Cool mode-change support.

# 1.0.0-alpha.35 — Sprint 3.1.6 Power Off from Heat Qualification

- Adds the exact 31-byte Power Off-from-Heat command captured and physically
  verified by Relay v2 transaction #7 on 2026-07-30.
- Adds a separate `off-heat` one-shot case requiring the exact
  On/Heat/25 °C/High/Vertical nine-field precondition.
- Requires the exact `WRITE-QUALIFIED-POWER-OFF-HEAT-ONCE` confirmation token.
- Preserves one write, zero retries, direct pre/post reads, and 9/9 verification.
- Keeps `off-heat` disconnected from normal MQTT control; Alpha.34's existing
  guarded power cases and Relay v2 fallback remain unchanged.

# 1.0.0-alpha.34 — Sprint 3.1.5 Guarded Direct Power Control

- Integrated the three qualified power cases into normal Home Assistant MQTT
  control behind a separate disabled-by-default `power_enabled` switch.
- Retained exact 31-byte captured frames, exact nine-field relay and direct
  preconditions, one write, zero retries, and nine-field post-read verification.
- Added automatic Relay v2 fallback with an explicit recorded reason.
- Kept deferred-temperature power-on requests and all unqualified state shapes
  on Relay v2.
- Kept fan, swing, feature, and unqualified mode transitions on Relay v2.

# 1.0.0-alpha.33 — Sprint 3.1.4 Power On + Cool Qualification

- Added the exact 31-byte combined Power On + Cool frame from successful
  Relay v2 transaction #4 recorded on 2026-07-29.
- Locked its length, XOR checksum, SHA-256 fingerprint, starting state, and
  expected nine-field result.
- Requires `--case on-cool` and a distinct exact confirmation token.
- Retained one write, zero retries, no automatic restore, and direct post-read.
- Kept the proven Power Off and Power On + Heat cases unchanged.
- Kept normal MQTT power and mode commands on Relay v2.
- Explicitly does not generalize either combined frame as power-only support.

# 1.0.0-alpha.32 — Sprint 3.1.3 Power On + Heat Qualification

- Added the exact 31-byte combined Power On + Heat frame from the fresh
  successful Relay v2 transaction recorded on 2026-07-29.
- Locked its length, XOR checksum, SHA-256 fingerprint, starting state, and
  expected nine-field result.
- Requires `--case on-heat` and a distinct exact confirmation token.
- Retained one write, zero retries, no automatic restore, and direct post-read.
- Kept Alpha.31's corrected Power Off case unchanged.
- Kept normal MQTT power and mode commands on Relay v2.
- Explicitly does not generalize the combined frame as power-only support.

# 1.0.0-alpha.31 — Sprint 3.1.2 Corrected Power Off Qualification

- Replaced Alpha.30's rejected 32-byte Power Off frame with the successful
  31-byte frame from Relay v2 transaction 46.
- Removed the extra zero byte immediately before checksum `D9`.
- Locked the corrected frame length and SHA-256 fingerprint.
- Exposed only Power Off for live execution; Power On remains deferred.
- Retained the nine-field pre-read, one write, zero retries, and post-read.
- Kept normal MQTT power and mode commands on Relay v2.

# 1.0.0-alpha.30 — Sprint 3.1.1 Power One-Shot Qualification

- Attempted separate Power Off and Power On qualification cases.
- The 32-byte Power Off frame was rejected by the module with `0xFFFB`.
- Superseded by Alpha.31's fresh transaction 46 evidence.

# 1.0.0-alpha.29 — Sprint 3.1.0 Guarded Direct Temperature Control

- Added a disabled-by-default normal-control path for qualified York
  temperature commands.
- Requires exact nine-field relay and direct precondition matching.
- Uses one write with zero direct retries and verifies the post-read.
- Automatically falls back to Relay v2 on any direct-path failure.
- Keeps all power, mode, fan, swing, and feature commands on Relay v2.

# 1.0.0-alpha.28 — Sprint 3.0.3 Uncaptured Heat/Cool Qualification

- Added two isolated, hard-coded qualification cases whose target frames are
  generated without using matching Relay v2 target captures.
- Heat case: 23.5 °C to 22.5 °C.
- Cool case: 25 °C to 24.5 °C.
- Added independent 31-byte fixtures and SHA-256 fingerprints for both targets.
- Each case retains a 9/9 live precondition, distinct confirmation token, one
  write, zero retries, direct post-read, and no automatic restore.
- Kept generated writes disconnected from MQTT, startup, and normal transport.

# 1.0.0-alpha.27 — Sprint 3.0.2 Dynamic Temperature Command Qualification

- Added a canonical York temperature-command generator for Heat and Cool.
- Cross-validated whole- and half-degree generation against Relay v2 captures.
- Added a guarded Heat 24 °C to 23.5 °C generated-command qualification.
- Requires an exact captured-frame match, 9/9 live precondition, explicit
  confirmation, one write, zero retries, and a post-read.
- Kept dynamic writes disconnected from MQTT, startup, and the normal direct
  transport.

# 1.0.0-alpha.25 — Sprint 3.0.0 One-Shot Direct-Write Qualification

- Adds one separate operator-run direct-write qualification tool.
- Accepts only the exact official SDK command captured in Relay v2 transaction 2.
- Requires an exact live 9/9 precondition and an explicit confirmation token.
- Sends the command once, with no retry and no automatic restore.
- Performs direct reads immediately before and after the command.
- Does not connect direct writes to MQTT, Home Assistant, startup, or the normal
  Climate Bridge transport.

# 1.0.0-alpha.24 — Sprint 2.9.3 Target Temperature Qualification

- Decodes evidence-backed target temperature from York status bytes 8 and 9.
- Adds target temperature as the ninth relay/direct comparison field.
- Publishes relay and direct temperatures in retained native diagnostics.
- Rejects the known `direct_read`-under-`logging` indentation error at startup.
- Reports direct-read enabled/disabled status during configuration validation.
- Keeps Relay v2 as the only command path; direct LAN remains read-only.

# 1.0.0-alpha.23 — Sprint 2.9.2 Fan Status Mapping Fix

- Corrected York status nibble `0` from Low to Auto.
- Corrected York status nibble `1` from Auto to Low.
- Preserved nibble `2` as Medium and nibble `3` as High.
- Added live-mapping regression coverage for all four fan states.
- Updated offline decoder fixture expectations to match verified live evidence.
- Kept Relay v2 as the only command path; direct LAN remains read-only.

# 1.0.0-alpha.22 — Sprint 2.9.1 Fan Status Diagnostics

- Publishes the exact direct York status frame on the existing retained
  `diagnostic/native_state` topic.
- Publishes status byte 8, its fan nibble, and both relay/direct fan labels.
- Adds explicit fan values and status codes to the direct-read log line.
- Leaves the status decoder mapping and all control paths unchanged.

# 1.0.0-alpha.21 — Sprint 2.9.0 Direct LAN Read Integration

- Integrates the qualified Broadlink authentication and York state-query
  envelope into the main Climate Bridge container.
- Adds a disabled-by-default `direct_read` shadow observer beside Relay.
- Uses one authentication send and one fixed state-query send per scheduled
  observation, with zero automatic retries.
- Compares eight evidence-backed direct fields with relay state.
- Keeps all direct control writes unavailable.

# 1.0.0-alpha.20 — Sprint 2.8.3 Relay Command Extraction

- Records the exact JSON command Climate Bridge sends to York TFIAC Relay V2.
- Records relay HTTP responses, timing, hashes and correlation IDs.
- Adds offline extraction summary utility.
- Does not claim to expose the Android relay's internal native York packet.
- No replay or verification safety rules changed.

## 1.0.0-alpha.19

- Added the York Request Hunter for offline controller-request candidate ranking.
- Added shared York analysis loaders and conservative response-exclusion scoring.
- Added optional non-executable candidate records for human review.
- Current 23 imported packets remain classified as state responses; no packet is verified or transmitted.

## 1.0.0-alpha.17

- Added transport-agnostic TX instrumentation.
- York Replay Engine logs exact outbound bytes immediately before send.
- Added JSON/Markdown transmission records and correlation IDs.

# Climate Bridge 1.0.0-alpha.14

Sprint 2.7 adds Qualification Report V2 and the guarded one-shot native York state probe with decoder and relay comparison.

## 1.0.0-alpha.26

- Added a guarded Heat 23 °C to 24 °C one-shot qualification using the exact
  official SDK frame captured in Relay v2 transaction 25.
- Retained the 9/9 precondition, exact confirmation token, one write, zero
  retries, and mandatory post-read.
- Kept direct writes disconnected from MQTT, Home Assistant commands, normal
  bridge startup, and the standard direct transport.

## 1.0.0-alpha.13

- Added Sprint 2.6 offline York decoder qualification.
- Added 14 evidence-backed Protocol Explorer fixtures.
- Added JSON and Markdown qualification report generation.
- Added regression tests for fixture matching and mismatch reporting.
- Kept native transmission disabled and unresolved fields unset.

## 1.0.0-alpha.11

- Added root-level `qualification-reports/` required by Docker Compose.
- Made startup directory creation portable on Alpine `/bin/sh`.
- Added release and regression checks for report directories.

# Changelog

## 1.0.0-alpha.2
- Added credential-free startup banner.
- Began Sprint 2 native York transport foundation.
- Added direct device host/MAC configuration and validation.
- Added native UDP socket lifecycle and regression tests.
- Relay remains the default production transport.

# Changelog

## 1.0.0-alpha.82

- Replaced the byte-17-only indoor-temperature approximation with the official
  two-byte TCL/York SDK integer conversion.
- Added Capture 7's exact Auto/FEEL 23 °C → Cool 23 °C qualification edge.
- Limited Heat → Auto verification to the manual-defined 18/23 °C programs and
  the earlier physically observed 21 °C result.
- Preserved one write, zero retries, delayed verification, exact state guards
  and critical unexpected-Power-Off detection.

## 1.0.0-alpha.81

- Consolidated the five physically qualified official-SDK mode edges into one
  normal guarded control path.
- Removed the obsolete legacy mode-matrix runtime and per-release mode modules.
- Preserved exact source guards, one write, zero retries, delayed verification,
  temperature semantics and critical unexpected-Power-Off detection.

## 3.0.0-rc.5

Release-hardening candidate based on the qualified 3.0.0-rc.4.4.1 runtime.

- Centralized application version metadata.
- Added OCI Docker image labels.
- Added graceful init and shutdown settings to Compose.
- Added persisted qualification reports.
- Bundled the fixed RC4 qualification suite.
- Consolidated documentation and removed historical update clutter from the distribution.
- No changes to York protocol logic, MQTT topics, entity identifiers, command behavior, polling, health scoring or recovery logic.

## 3.0.0-rc.4.4.1

- Meaningful York AC activity entities.
- Deferred target-temperature changes while the AC is off.
- Correct command outcome statistics.
- Last state-change timestamp disabled by default to reduce activity noise.

## 1.0.0-alpha.3 — Sprint 2.2

- Added York adapter architecture: connection, session, encoder, decoder and state model.
- Added captured `0xBB` frame validation harness.
- Added configurable direct UDP port.
- Improved startup banner transport labels.
- Kept direct packet transmission disabled pending validated protocol fixtures.

## 1.0.0-alpha.3 — Sprint 2.2 packaging hotfix

- Include the new `adapters/` Python package in the Docker image.
- Correct Docker image version metadata.
- Add a packaging regression test covering both `transport/` and `adapters/`.

## 1.0.0-alpha.7

- Docker health now checks the Climate Bridge process, READY marker, and main-loop heartbeat.
- Legacy relay availability no longer directly controls Docker container health.
- Startup banner now uses the user-facing transport name `Relay (Legacy)`.
- Home Assistant device model changed from `Tablet Relay Edition` to `York TFIAC Adapter`.
- Remaining health messages use transport-neutral terminology.

## 1.0.0-alpha.7

- Added the version-controlled York TFIAC protocol reference under `protocols/york/`.
- Added capture, packet-library, schema and documentation structure.
- Recorded known Protocol Explorer observations with explicit confidence and limitations.
- Added tests preventing unverified packet records from becoming executable fixtures.
- Updated release verification to require the protocol reference.

## 1.0.0-alpha.7

- Added verified York packet-library loading and executable-record gating.
- Added safe native probe selection by packet record ID.
- Added validate-only mode that never opens a socket.
- Added import-ready native response capture reports.

## 1.0.0-alpha.11

- Added the York Protocol Lab static dashboard.
- Added direct DOCX capture import.
- Imported the recovered York Protocol Explorer evidence: 4 captures, 23 unique frames and 127 occurrences.
- Added automatic feature-coverage reporting and dashboard refresh.
- Added redacted source-copy behaviour with explicit raw-copy opt-in.
- Restored and auto-created the `qualification-reports` directory.
- Hardened Docker runtime directory creation.

## 1.0.0-alpha.11

- Added the first evidence-backed York TFIAC status decoder.
- Added XOR checksum validation for captured 21-byte status frames.
- Added decoding for power, mode, fan, swing, turbo, eco, health and display.
- Kept temperature and sleep unresolved rather than guessing their encoding.
- Added regression tests using frames recovered from Protocol Explorer logs.

## 1.0.0-alpha.13

- Integrated 14-frame York decoder qualification into `qualification_suite.py`.
- Standard qualification now reports 8 checks rather than 7.
- Packaged `york_decoder_qualification.py` in the Docker image.
- Renamed qualification report headings from the legacy York Hybrid Bridge name to Climate Bridge.

## 1.0.0-alpha.15
- Added the York Packet Classifier.
- Classifies observed 21-byte York status frames as device-to-controller state responses.
- Matches exact qualified decoder fixtures and records confidence/reasons.
- Generates JSON and Markdown classification reports.
- Never verifies records, makes packets executable, or transmits packets.

## 1.0.0-alpha.16

- Added guarded York replay engine.
- Added York XML `Declaration` and `statusUpdateMsg` parser/listener.
- Added expected-state metadata support to verified packet records.
- Added replay JSON reporting under `/reports/replay`.
# 1.0.0-alpha.89 — Sprint 3.1.60 Official-SDK Cool 22 to 20 °C Fan Auto Qualification

- Added Capture 12's exact official-SDK Cool 22.0 → 20.0 °C command edge.
- Required the exact nine-field cached source and matching fresh pre-read.
- Preserved one write, zero retries, delayed verification, and critical Power Off handling.
- Kept every other uncaptured target from the 22.0 °C source blocked.

See `SPRINT_3_1_60_OFFICIAL_SDK_COOL_22_TO_20_FAN_AUTO_QUALIFICATION.md`.

# 1.0.0-alpha.90 — Sprint 3.1.61 Grouped Official-SDK Cool/Fan Auto Temperature Matrix

- Grouped six exact Cool / Fan Auto / Swing Off temperature edges into one release.
- Added 20→22.5→24→24.5→20.5→22→20 °C as the ordered qualification sequence.
- Retained exact cached and fresh nine-field source guards for every edge.
- Retained one write, four UDP sends, zero retries, delayed verification, and critical Power Off handling per step.
- Kept every source→target pair outside the immutable matrix blocked.

See `SPRINT_3_1_61_GROUPED_OFFICIAL_SDK_COOL_FAN_AUTO_TEMPERATURE_MATRIX.md`.
