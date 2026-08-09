# Climate Bridge 1.0.0-alpha.92

Sprint 3.1.63 extends the general Cool temperature encoder across the qualified
Fan Auto, Low, and High states while keeping Swing Off and every established
safety gate. See `SPRINT_3_1_63_GENERAL_COOL_QUALIFIED_FAN_TEMPERATURE_ENCODER.md`.

Sprint 3.1.62 replaces the temporary Cool/Fan Auto source-edge matrix with a
guarded general **16.0–31.0 °C / 0.5 °C** target-state encoder. Exact cached
and fresh nine-field source checks, one write, four UDP sends, zero retries,
delayed verification, and critical unexpected-Power-Off handling remain
mandatory.

See `SPRINT_3_1_62_GENERAL_COOL_FAN_AUTO_TEMPERATURE_ENCODER.md`.

## Alpha.90

Sprint 3.1.61 adds one grouped official-SDK **Cool / Fan Auto / Swing Off**
temperature matrix: 20→22.5→24→24.5→20.5→22→20 °C. Each of the six steps
is an immutable source→target edge with exact nine-field cached-state and fresh
authenticated pre-read guards.

See `SPRINT_3_1_61_GROUPED_OFFICIAL_SDK_COOL_FAN_AUTO_TEMPERATURE_MATRIX.md`.

## Alpha.89

Sprint 3.1.60 adds Capture 12's exact official-SDK **Cool 22.0 °C →
20.0 °C / Fan Auto / Swing Off** edge. It requires the exact nine-field cached
source plus a matching fresh authenticated pre-read before reusing the SDK
frame that is byte-identical to the already qualified 20.5 → 20.0 °C target.
One control write, zero retries, delayed read-only verification, and critical
unexpected-Power-Off handling remain mandatory.

See `SPRINT_3_1_60_OFFICIAL_SDK_COOL_22_TO_20_FAN_AUTO_QUALIFICATION.md`.

## Alpha.88

Sprint 3.1.59 adds Capture 10's exact official-SDK **Cool 20.0 °C →
22.0 °C / Fan Auto / Swing Off** edge. It preserves exact nine-field source
and result checks, fresh authenticated pre-read, one write with zero retries,
delayed read-only verification, and critical unexpected Power Off handling.
Every other uncaptured target from the 20.0 °C source remains blocked.

See `SPRINT_3_1_59_OFFICIAL_SDK_COOL_20_TO_22_FAN_AUTO_QUALIFICATION.md`.

## Alpha.87

Sprint 3.1.58 adds Capture 11's exact official-SDK **Cool 20.5 °C →
20.0 °C / Fan Auto / Swing Off** edge. It preserves exact nine-field source
and result guards, one write, zero retries, and delayed read-only verification.
Every other uncaptured target from the 20.5 °C source remains blocked.

See `SPRINT_3_1_58_OFFICIAL_SDK_COOL_20_5_TO_20_FAN_AUTO_QUALIFICATION.md`.

## Alpha.86

Sprint 3.1.57 adds Capture 10's exact official-SDK **Cool 20.0 °C →
20.5 °C / Fan Auto / Swing Off** edge. It preserves exact nine-field source
and result guards, one write, zero retries, and delayed read-only verification.
The reverse edge and all other uncaptured Cool/Fan Auto targets remain blocked.

See `SPRINT_3_1_57_OFFICIAL_SDK_COOL_20_TO_20_5_FAN_AUTO_QUALIFICATION.md`.

## Alpha.85

Sprint 3.1.56 adds the exact official-SDK **Auto/FEEL 20 °C → Cool 20 °C**
mode edge from Capture 9. It is guarded by full nine-field source, fresh
pre-read and result checks, with one write, zero retries, delayed read-only
verification and no fallback. Every uncaptured Auto source or exit remains
blocked.

See `SPRINT_3_1_56_OFFICIAL_SDK_AUTO_FEEL_20_TO_COOL_QUALIFICATION.md`.

## Alpha.84

Sprint 3.1.55 recognises the physically observed **20 °C Auto/FEEL program**
returned by the already-qualified Heat 23 °C → Auto transition. The command,
source guard and all non-temperature result fields remain unchanged. Arbitrary
Auto values and every uncaptured Auto 20 °C exit remain blocked.

See `SPRINT_3_1_55_AUTO_FEEL_20_PROGRAM_QUALIFICATION.md`.

## Alpha.83

Sprint 3.1.54 qualifies one isolated **Cool 23 °C → Cool 21 °C** temperature
edge while preserving Fan Auto, both swing axes Off and all optional fields.
The command comes from Capture 8's official native-parser evidence and is
accepted only from the exact nine-field live source. Every other Fan Auto
temperature target remains blocked.

See `SPRINT_3_1_54_OFFICIAL_SDK_COOL_23_TO_21_FAN_AUTO_QUALIFICATION.md`.

## Alpha.82

Sprint 3.1.53 corrects the measured indoor-temperature decoder using the exact
two-byte TCL/York SDK conversion established by synchronized Capture 7. The
same capture adds one isolated Auto/FEEL 23 °C → Cool 23 °C qualification edge
for the unit's current latched cold-room program. Auto verification accepts
only the manual-defined 18/23 °C program values plus the earlier physically
observed 21 °C result; unknown Auto states and uncaptured exits remain blocked.

See `SPRINT_3_1_53_AUTO_FEEL_PROGRAM_AND_INDOOR_TEMPERATURE_CORRECTION.md`.

## Alpha.81

Sprint 3.1.52 consolidates the completed official-SDK five-mode loop into one
normal guarded mode-control path. One immutable registry, one exact selector,
one transport allowlist and one packet builder own the physically qualified
edges while preserving all fresh-read and delayed-verification safeguards.

See `SPRINT_3_1_52_QUALIFIED_MODE_LOOP_CONSOLIDATION.md`.

## Alpha.80

Sprint 3.1.51 enables one isolated **Cool 21 °C → Dry** qualification edge
from York Write Packet Lab Capture 6. It requires the exact live Cool source,
admits only the byte-exact official-SDK frame, performs one control write with
zero retries, and verifies the eight fields applicable in Dry mode. The
retained protocol temperature byte is not exposed as a Dry target setpoint;
Home Assistant continues showing only the genuine room temperature. The final
legacy Alpha.72 Dry frame is removed from the transport allowlist.

See `SPRINT_3_1_51_OFFICIAL_SDK_COOL_21_TO_DRY_QUALIFICATION.md`.

## Alpha.79

Sprint 3.1.50 enables one isolated **Auto/FEEL → Cool** qualification edge
from official-SDK Capture 5. The only accepted source is Power On / Auto/FEEL /
21 °C status / Fan Auto / Swing Off with optional features disabled and
Display On. The exact target is Cool / 21 °C / Fan Auto / Swing Off.

Alpha.79 performs one control write with zero retries and verifies all nine
Cool fields through the delayed read-only window. Unexpected Power Off aborts
critically. Alpha.72's older Cool 22 °C candidate and every nearby Auto/FEEL
source remain transport-blocked.

See `SPRINT_3_1_50_OFFICIAL_SDK_AUTO_FEEL_21_TO_COOL_QUALIFICATION.md`.

## Alpha.78

Sprint 3.1.49 enables one isolated **Heat → Auto/FEEL** qualification edge
from official-SDK Capture 4. The only accepted source is Power On / Heat /
23 °C / Fan Auto / Swing Off with optional features disabled and Display On.
The exact native target is Auto/FEEL with Fan Auto and both swing axes Off.

Alpha.78 performs one control write with zero retries, verifies the exact
power, mode, fan, swing and feature state through the delayed read-only window,
and accepts only a decoder-representable 16.0–31.5 °C dynamic Auto status
temperature. Unexpected Power Off aborts critically. The older Heat 25 °C
candidate and every nearby Heat source remain blocked.

See `SPRINT_3_1_49_OFFICIAL_SDK_HEAT_23_TO_AUTO_FEEL_QUALIFICATION.md`.

## Alpha.77

Sprint 3.1.48 enables one isolated **Fan-only → Heat** qualification edge from
the exact official-SDK Capture 3 evidence. The only accepted source is Power
On / Fan-only / Fan Auto / Swing Off with optional features disabled and
Display On. The exact target is Heat / 23 °C / Fan Auto / Swing Off.

Fan-only source temperature remains non-applicable. Alpha.77 performs one
control write with zero retries, verifies all nine Heat fields through the
delayed read-only window, and aborts critically on unexpected Power Off. Every
other Fan-only exit remains disabled.

See `SPRINT_3_1_48_OFFICIAL_SDK_FAN_ONLY_TO_HEAT_QUALIFICATION.md`.

## Alpha.76

Sprint 3.1.47 clears stale Home Assistant target-temperature state when Dry or
Fan-only is active. The bridge now publishes Home Assistant's documented
retained `None` reset payload, safely handles numeric-to-non-applicable
transitions, and restores the genuine numeric setpoint on return to Heat or
Cool. The authoritative room temperature remains sourced from `indoorTemp`.

See `SPRINT_3_1_47_MQTT_NON_APPLICABLE_SETPOINT_RESET.md`.

## Alpha.75

Sprint 3.1.46 corrects Dry and Fan-only temperature handling from live Write
Packet Lab evidence. Neither mode has a selectable setpoint; both protocol
values are ignored, while the independent measured indoor temperature is
published to Home Assistant. The official-SDK Dry → Fan-only qualification
remains isolated with one write, zero retries, eight applicable fields and
critical Power Off detection. Temperature commands remain blocked in both
modes, every Fan-only exit remains disabled, and the retired Alpha.71 frame
remains rejected.

See `SPRINT_3_1_46_DRY_AND_FAN_ONLY_TEMPERATURE_SEMANTICS.md`.

## Alpha.73

Sprint 3.1.44 adds one isolated qualification edge using the exact Fan-only
frame generated offline by York Write Packet Lab v1 through the official
TCL/Broadlink SDK: **Dry / 17 °C / Fan Auto / Swing Off → Fan-only / 17 °C /
Fan Auto / Swing Off**. No other Dry temperature, fan, swing, feature shape or
Fan-only transition is enabled.

The retired Alpha.71 frame remains permanently rejected. Alpha.73 performs one
write with zero retries, then polls read-only for up to 30 seconds. Any
unexpected Power Off raises an immediate critical failure. Fan-only → Heat and
all other Fan-only exits remain disabled.

See `SPRINT_3_1_44_OFFICIAL_SDK_FAN_ONLY_QUALIFICATION.md`.

## Alpha.72

Sprint 3.1.43 contains the unsafe historical Fan-only candidate after live
Alpha.71 testing showed that Dry → Fan-only eventually switched the physical
unit Off. The old frame is now rejected by both the builder and production
transport boundary, and both mode edges involving Fan-only are paused pending
a fresh labelled TFIAC capture.

The remaining Auto → Cool, Cool → Dry and Heat → Auto edges use read-only
post-write verification polling across a full 30-second window. The control
write is never retried. A delayed valid state may pass, while any unexpected
Power Off observation raises an immediate critical verification failure.

See `SPRINT_3_1_43_FAN_ONLY_CONTAINMENT_DELAYED_VERIFICATION.md`.

## Alpha.71

Sprint 3.1.42 added bounded dynamic Dry status validation after the live
Cool → Dry transition returned Dry / 21 °C rather than the historical 16 °C
fixture. That release still authorised the historical Dry → Fan-only edge;
Alpha.72 supersedes and disables it following the physical Power Off result.

See `SPRINT_3_1_42_DRY_DYNAMIC_STATUS_MODE_MATRIX_CORRECTION.md`.

## Alpha.68

Sprint 3.1.39 corrects both Auto/FEEL endpoints in the five-edge remaining-mode
matrix to the live-confirmed fixed 22 °C authoritative state. Cool, Dry,
Fan-only and Heat targets remain unchanged. Each edge keeps nine-field pre/post
verification, four UDP sends, zero retries and fail-closed ordered guards.

See `SPRINT_3_1_39_AUTO_FEEL_22C_MODE_MATRIX_CORRECTION.md`.

## Alpha.67

Sprint 3.1.38 introduced the isolated Auto → Cool → Dry → Fan-only → Heat →
Auto qualification sequence. Alpha.68 supersedes its Auto / 23 °C assumption.

## Alpha.66

Sprint 3.1.37 adds one tightly guarded compatibility edge for Alpha.65's
post-swing source: **Heat / 22.5 °C / Fan Low / decoded Horizontal → Fan High /
Swing Off**. It uses the existing exact High/Off frame, requires fresh
nine-field source confirmation and verifies all nine target fields with four
UDP sends and zero retries. The ordinary High/Off → Low/Off return remains the
physically qualified Alpha.63 path.

See `SPRINT_3_1_37_POST_SWING_FAN_COMPATIBILITY.md`.

## Alpha.65

Sprint 3.1.36 adds the guarded **Heat / 22.5 °C / Fan Low** ordered swing
matrix: **Off → Vertical → Both → Horizontal → Off**. Each Home Assistant
command remains a separate transaction with an exact authoritative source,
fresh nine-field pre-read, one write, four UDP sends, zero retries and a
nine-field post-read.

The Both and Horizontal 22.5 °C candidates combine only the axis fields and
temperature delta independently proven by Alpha.50 and Alpha.53. They remain
case-specific and outside the immutable captured replay allowlist. Skipped
edges and nearby states remain fail-closed.

See `SPRINT_3_1_36_GROUPED_SWING_QUALIFICATION_MATRIX.md`.

## Alpha.64

Sprint 3.1.35 groups the physically verified Heat fan pair with one guarded
**Cool / 22.5 °C / Fan Low↔High / Swing Off** qualification pair. The Cool
candidate applies only the mode transformation already proven by Alpha.62 to
Alpha.63's verified fan frames.

Each command independently requires the exact authoritative source state and a
fresh nine-field direct pre-read. Each uses one write, four UDP sends, zero
retries and a nine-field post-read. The six-step acceptance sequence can run in
one deployment and one continuous log without weakening any command guard.

See `SPRINT_3_1_35_GROUPED_FAN_QUALIFICATION_MATRIX.md`.

## Alpha.63

Sprint 3.1.34 physically qualified Heat / 22.5 °C / Fan Low↔High / Swing Off.
Both louvre axes remained stationary in both directions.

See `SPRINT_3_1_34_FAN_HIGH_OFF_QUALIFICATION.md`.

## Alpha.62

Sprint 3.1.33 adds guarded parameterised Heat↔Cool control while the unit is
running. Both the current and target complete states must be canonical shapes
already qualified by Alpha.60. The command preserves the authoritative target
temperature, fan and swing, including the physically verified 22.5 °C / Fan
Low / Swing Off state.

Every eligible transition retains the fresh nine-field pre-read and post-read,
four UDP sends, zero retries and no fallback. Unsupported or changed states
stop before the write. Historical captured replay allowlists remain immutable.

See `SPRINT_3_1_33_PARAMETERISED_RUNNING_MODE_CONTROL.md`.

## Alpha.61

Sprint 3.1.32 adds guarded parameterised On→Off control while preserving the
authoritative mode, target temperature, fan and swing. The command clears only
the captured York power bit and recalculates the checksum.

See `SPRINT_3_1_32_PARAMETERISED_POWER_OFF_CONTROL.md`.

## Alpha.60

Sprint 3.1.31 adds guarded parameterised Off→On control from authoritative
stored state, preserving whole- or half-degree temperature, fan and swing.

See `SPRINT_3_1_31_PARAMETERISED_POWER_ON_CONTROL.md`.

## Alpha.58

Sprint 3.1.29 removes Relay v2 from the live command path used with
authenticated direct-state authority. The Alpha.57 configuration remains
accepted unchanged, while unqualified commands now stop at a local native
safety boundary instead of contacting the tablet.

See `SPRINT_3_1_29_RELAY_FREE_COMMAND_BOUNDARY.md`.

## Alpha.57

Sprint 3.1.28 corrects the poll-failure counter shown during an extended York
module outage. Threshold-facing logs and retry diagnostics remain capped at
the configured limit, while a successful direct read resets the next displayed
sequence to its first failure. Availability and recovery behaviour are
unchanged from Alpha.56.

See `SPRINT_3_1_28_POLL_FAILURE_COUNTER_CORRECTION.md`.

## Alpha.56

Sprint 3.1.27 adds tablet-free restart and recovery hardening to the
authenticated direct-state authority introduced in Sprint 3.1.26. It keeps the
Home Assistant entity unavailable until a fresh direct read succeeds after
startup or MQTT reconnect, and automatically restores state without Relay v2.

Sprint 3.1.26 makes authenticated direct LAN reads authoritative whenever
`direct_read.enabled` is true. Normal Home Assistant polling and every command
guard now start from the York module itself; Relay v2 `/state` is not used.

Relay v2 remains command-fallback only for unqualified requests in this stage.
Its returned HVAC state is discarded and replaced by a fresh direct read before
publication. All Alpha.54 native write envelopes remain unchanged.

See `SPRINT_3_1_26_DIRECT_STATE_AUTHORITY.md`.

## Alpha.54

Sprint 3.1.25 enables normal guarded Home Assistant control for the two
Heat / 21.5 °C / Fan Low Horizontal-only transitions physically qualified in
Alpha.53: Off → Horizontal and Horizontal → Off.

Each eligible command requires exact nine-field Relay and direct pre-reads,
one write, four UDP sends, zero retries, and a matching nine-field post-read.
All other Horizontal/Both requests retain Relay v2 fallback. Alpha.53's
qualification tool is removed from the executable container.

See `SPRINT_3_1_25_NATIVE_HEAT_HORIZONTAL_AXIS_CONTROL.md`.

## Alpha.53

Sprint 3.1.24 adds guarded one-shot native qualification for Heat / 21.5 °C /
Fan Low **Off → Horizontal → Off** control. It uses the exact Relay v2 frames
with the independent command-side Horizontal flag `0x08` and preserves all
other state fields.

Normal Home Assistant Horizontal routing remains on Relay v2. Each live case
requires an exact nine-field pre-read and post-read, one write, four UDP sends,
zero retries and an explicit case-specific confirmation token.

See `SPRINT_3_1_24_HEAT_HORIZONTAL_AXIS_QUALIFICATION.md`.

## Alpha.52

Sprint 3.1.23 enables normal guarded Home Assistant control for the two
Dry / 21 °C / Fan Low Horizontal-axis transitions physically qualified in
Alpha.51: Vertical → Both and Both → Vertical.

Each eligible command requires exact nine-field Relay and direct pre-reads,
one write, four UDP sends, zero retries, and a matching nine-field post-read.
All other Horizontal/Both requests retain Relay v2 fallback.

See `SPRINT_3_1_23_NATIVE_DRY_HORIZONTAL_AXIS_CONTROL.md`.

## Alpha.51

Sprint 3.1.22 physically qualified the independent Horizontal axis at the
observable Dry / 21 °C / Fan Low state using guarded one-shot Vertical → Both
and Both → Vertical writes.

## Alpha.50

Sprint 3.1.21 adds a guarded one-shot qualification for the independent
Horizontal axis at 21.5 °C / Heat / Fan Low. It enables Horizontal while
preserving Vertical (`vertical → both`), then removes only Horizontal
(`both → vertical`). Normal Home Assistant Horizontal and Both requests remain
on Relay v2 until physical qualification succeeds.

The exact Relay command-side Horizontal flag is `0x08`. Alpha.49's rejected
`0x20` status-bit candidate is no longer executable or write-allowlisted.

See `SPRINT_3_1_21_INDEPENDENT_HORIZONTAL_AXIS_QUALIFICATION.md`.

## Alpha.49 evidence

Alpha.49 proved that the status-response Horizontal bit cannot be copied into
a write command. Its candidate commanded Swing Off and is retained only as
rejected historical evidence. Relay v2 subsequently supplied the exact write
frames used by Alpha.50.

## Alpha.48 baseline

Sprint 3.1.19 enables guarded native Swing Vertical ↔ Off control for the
qualified On / Heat / Fan Low state. It switches between the already qualified
`0x3A` Vertical and `0x02` Off complete-state frames while preserving the
current whole- or half-degree setpoint.

Each eligible command retains exact nine-field Relay and live preconditions,
one native write, four UDP sends, zero retries and a matching post-read.
Horizontal, Both, Fan High, unqualified setpoints and direct failures retain
Relay v2 fallback.

Physical confirmation is limited to one normal Home Assistant
Vertical → Off → Vertical sequence at Heat / 21 °C / Fan Low. See
`SPRINT_3_1_19_GUARDED_NATIVE_SWING_CONTROL.md`.

## Alpha.47

Sprint 3.1.18 enables guarded native Fan Low ↔ High control for the qualified
Heat/Swing Vertical state. It selects the already qualified `0x3A` Low or
`0x3D` High complete-state frame at the current whole- or half-degree
setpoint.

Each eligible command retains exact nine-field Relay and live preconditions,
one native write, four UDP sends, zero retries and a matching post-read.
Temperature and Vertical swing must remain unchanged. Auto, Medium,
unqualified states and direct failures retain Relay v2 fallback.

Physical confirmation is limited to one normal Home Assistant
Low → High → Low sequence at Heat / 25 °C / Swing Vertical. See
`SPRINT_3_1_18_GUARDED_NATIVE_FAN_CONTROL.md`.

## Alpha.46

Sprint 3.1.17 enables native 0.5 °C temperature control from 16 through 31 °C
for the guarded Heat/High/Vertical and Heat/Low/Vertical paths. It uses the
already captured byte-11 half-degree flag while preserving each path's
qualified operating-state byte and the existing nine-field pre/post guards,
one-write/four-send execution, zero retries and Relay v2 fallback.

Physical confirmation is limited to one comfortable normal Home Assistant
25 → 25.5 → 25 °C sequence at Heat / Fan Low / Swing Vertical. See
`SPRINT_3_1_17_HALF_DEGREE_TEMPERATURE_CONTROL.md`.

## Alpha.45

Sprint 3.1.16 enables normal guarded Home Assistant temperature control for
Heat / Fan Low / Swing Vertical across the whole-degree 16–31 °C range.
Alpha.44 validated all sixteen generated frames and physically qualified the
comfortable 25 → 26 → 25 °C sequence.

Eligible commands retain a fresh authenticated pre-read, exact nine-field
state guard, one native write, four UDP sends, zero automatic retries and an
exact post-read. Relay v2 remains available when a guard or direct operation
fails. See `SPRINT_3_1_16_PARAMETERISED_LOW_VERTICAL_CONTROL.md`.

## Alpha.44

Sprint 3.1.15 adds qualification-only parameterised Heat/Fan Low/Swing
Vertical temperature generation across the York whole-degree 16–31 °C range.
It preserves the exact Alpha.42 24 and 25 °C capture anchors and validates all
16 generated frames offline.

Live qualification is limited to the comfortable 25 → 26 → 25 °C sequence.
Normal Home Assistant routing remains unchanged from Alpha.43: only 24 ↔ 25 °C
uses the native Low/Vertical path, and all other targets retain Relay v2
fallback until physical qualification is complete. See
`SPRINT_3_1_15_PARAMETERISED_LOW_VERTICAL_TEMPERATURE.md`.

## Alpha.43

Sprint 3.1.14 integrates the two physically qualified Heat/Fan Low/Swing
Vertical transitions into normal guarded Home Assistant control: 25 → 24 °C
and 24 → 25 °C. Every other Low/Vertical transition continues through Relay
v2 fallback. See
`SPRINT_3_1_14_GUARDED_LOW_VERTICAL_TEMPERATURE_CONTROL.md`.

## Alpha.42

Sprint 3.1.13 adds a bounded one-shot qualification for the occupied-room
Heat/Fan Low/Swing Vertical temperature shape. Exact Relay v2 captures for
25 → 24 °C and 24 → 25 °C were physically verified while Fan remained Low and
Swing remained Vertical.

Normal Home Assistant temperature routing is unchanged: Low/Vertical still
uses Relay v2. See `SPRINT_3_1_13_LOW_VERTICAL_TEMPERATURE_QUALIFICATION.md`.

## Alpha.41

Sprint 3.1.12 integrates the physically qualified 16–31 °C whole-degree
Heat/High/Vertical generator into normal guarded Home Assistant temperature
control. Each eligible command requires exact nine-field Relay and live direct
preconditions, one write, zero retries and a matching nine-field post-read.
Every unqualified shape uses Relay v2 fallback.

The occupied-room Heat/23 °C/Fan Low/Swing Vertical state is intentionally
ineligible for direct writes, so a temperature request preserves Fan Low by
falling back before a direct client is created.

See `SPRINT_3_1_12_GUARDED_TEMPERATURE_CONTROL.md`.

## Alpha.40

Sprint 3.1.11 confirmed the complete 16–31 °C whole-degree range and physically
qualified both endpoint transitions.

## Alpha.39

Sprint 3.1.10 established the whole-degree encoding from exact 24, 25 and
26 °C Relay captures.

## Alpha.38

Sprint 3.1.9 integrates both Alpha.37-qualified running mode changes into
normal guarded Home Assistant control. Heat to Cool and Cool to Heat reuse the
exact captured target-state frames, but each requires its distinct nine-field
running precondition, one write, zero retries, and a matching nine-field
post-read. Unqualified states continue through Relay v2. See
`SPRINT_3_1_9_GUARDED_RUNNING_MODE_CONTROL.md`.

## Alpha.37

Sprint 3.1.8 adds guarded one-shot qualification for both running mode
directions: Heat to Cool and Cool to Heat. Both cases use exact Relay v2
captures, exact nine-field pre/post verification, one write, zero retries, and
distinct confirmation tokens. Normal MQTT mode handling remains on Relay v2.

Sprint 3.1.7 integrates the physically qualified `off-heat` case into normal
Home Assistant guarded power control. The Relay and live direct state select
the distinct Heat-off or Cool-off captured frame. Every eligible request still
uses one write, zero retries, nine-field pre/post verification, and automatic
Relay v2 fallback. See `SPRINT_3_1_7_GUARDED_POWER_OFF_HEAT_CONTROL.md`.

## Alpha.35

Sprint 3.1.6 qualified the exact Power Off-from-Heat frame captured by Relay v2
transaction #7 on 2026-07-30. See
`SPRINT_3_1_6_POWER_OFF_HEAT_QUALIFICATION.md`.

## Alpha.34

Sprint 3.1.5 integrates the three power cases proven through Alpha.33 into
normal Home Assistant MQTT control. Power control has its own
`direct_control.power_enabled` switch. Eligible requests use one exact captured
write, zero retries, direct nine-field pre/post verification, and automatic
Relay v2 fallback. See `SPRINT_3_1_5_GUARDED_DIRECT_POWER_CONTROL.md`.

## Alpha.33

Sprint 3.1.4 adds a bounded combined Power On + Cool qualification using the
successful 31-byte Relay v2 transaction #4 recorded on 2026-07-29. It requires
the exact Off/Heat/25 °C/High/Vertical precondition and verifies the resulting
On/Cool state. This is not a power-only command. The proven Power Off and
Power On + Heat cases remain unchanged. Normal MQTT power and mode commands
remain on Relay v2. See `SPRINT_3_1_4_POWER_ON_COOL_QUALIFICATION.md`.

## Alpha.32

Sprint 3.1.3 adds a bounded combined Power On + Heat qualification using the
fresh successful 31-byte Relay v2 frame recorded on 2026-07-29. It requires the
exact Off/Cool/25 °C/High/Vertical precondition and verifies the resulting
On/Heat state. This is not a power-only command. Alpha.31's corrected Power Off
case remains unchanged. Normal MQTT power and mode commands remain on Relay v2.
See `SPRINT_3_1_3_POWER_ON_HEAT_QUALIFICATION.md`.

Sprint 3.1.0 introduces guarded normal temperature control using the qualified
York LAN generator. It is disabled by default, limited to the exact proven
state shape, and falls back to Relay v2 on any direct-path failure.

Sprint 3.0.3 qualified generated York temperature targets beyond matching
Relay v2 captures. Alpha.28 contains separate guarded Heat 23.5→22.5 °C and
Cool 25→24.5 °C cases. Each retains the 9/9 pre-read, exact per-case
confirmation token, one-write/no-retry policy, and post-read verification.

Unqualified Home Assistant commands continue to use Relay v2. See
`SPRINT_3_0_3_UNCAPTURED_HEAT_COOL_TEMPERATURE.md` for the qualification
boundary.

## Alpha.24 baseline

Sprint 2.9.3 adds evidence-backed target-temperature decoding to the direct
read-only comparison. The relay remains the active state and control path.

## Active architecture

```text
Home Assistant ← MQTT ← Climate Bridge ← authenticated direct York state
                                 │
                                 ├────→ qualified native York command
                                 └────→ Relay v2 command fallback only
```

When `direct_read.enabled` is true, direct York state is authoritative. Relay v2
is never polled for HVAC state and cannot overwrite Home Assistant state. It is
retained only as command fallback until the later fallback-removal stage.

## Safety boundary

- `direct_read.enabled` must remain `true` for Alpha.56 tablet-free restart and
  recovery operation.
- Direct observations use `0x65 → 0xE9 → 0x6A → 0xEE`.
- The only York request is `BB000104020100BD`.
- Each observation uses two UDP sends and zero automatic retries.
- Direct write generation is available only to isolated operator-run
  qualification tools and the guarded temperature manager.
- Guarded power/mode control is separately disabled by default and accepts only
  the six exact physically qualified cases.
- Direct-read failures drive availability and block command selection because
  Relay state is no longer trusted.
- Unqualified Home Assistant commands continue through Relay v2.

## Configuration

Keep the working relay settings and add:

```yaml
direct_read:
  enabled: true
  host: 192.0.2.1
  mac: "02:00:00:00:00:01"
  port: 80
  timeout_seconds: 3
  poll_seconds: 30
```

To opt into guarded power control after verifying its safe baseline:

```yaml
direct_control:
  enabled: true
  power_enabled: true
  fallback_to_relay: true
  post_write_delay_seconds: 2
```

The host and MAC above are documentation-only placeholders. Replace both with
the York module values before deployment.

## Direct-state diagnostics

The diagnostic entities report:

- Native probe status
- Native authority status
- Native response length
- Last native probe

The decoded authoritative state is retained at
`<base_topic>/diagnostic/native_state`.

A healthy observation reports `authoritative (9 decoded fields)` and publishes
`state_source=direct_lan_authoritative`.

## Deployment boundary

Do not run this package as a second bridge against the same MQTT topics. Stop
the previous Climate Bridge container before rebuilding the project with this
release. Keep York TFIAC Relay v2 running because it remains command fallback
for unqualified requests during this sprint.
