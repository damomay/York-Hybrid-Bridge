# Climate Bridge 1.0.0

Sprint 3.2.1 promotes the exact accepted Beta.1 implementation as the first
stable York release. No protocol behaviour, command manager, packet encoder or
transport allowlist has been changed or widened.

The release provides guarded Home Assistant control of Power, Cool, Heat,
temperature, Fan Low/High and the physically qualified swing and restricted
mode-loop transitions. Direct authenticated unit reads remain authoritative,
including changes made with the physical remote.

Beta.1 passed the complete eight-step end-to-end acceptance sequence. The
bridge also demonstrated cumulative connection stability across repeated
12–16 hour overnight runs from Alpha.67 onward, with no recurring MQTT
disconnects, container restarts or unexplained loss of control.

See `V1_0_0_RELEASE_AND_UPGRADE_GUIDE.md`,
`V1_0_0_ACCEPTANCE_AND_STABILITY_EVIDENCE.md` and
`SPRINT_3_2_0_CAPABILITY_AUDIT_AND_BETA_SCOPE.md`.

## Previous release: 1.0.0-beta.1

Sprint 3.2.0 freezes the physically qualified first-unit feature boundary as a
single beta candidate. No packet encoding or transport allowlist is widened.

The Home Assistant discovery surface now matches the supported scope more
closely: Fan Medium is no longer advertised, and the unqualified Turbo, Eco,
Health, Display and Sleep command switches are removed. Those protocol fields
remain decoded and verified in every guarded transaction.

See `SPRINT_3_2_0_CAPABILITY_AUDIT_AND_BETA_SCOPE.md` and
`BETA_1_ACCEPTANCE_TEST.md`.

## Previous release: 1.0.0-alpha.92

Sprint 3.1.63 extends the general **Cool / Swing Off** temperature encoder from
Fan Auto to the three qualified fan states: **Auto, Low, and High**. The encoder
supports 16.0–31.0 °C in 0.5 °C increments and preserves the exact fan setting
present in both the cached state and fresh authoritative pre-read.

The transport accepts only the resulting 93 canonical complete-state frames.
Medium and unknown fan states remain blocked before client creation; unrelated
feature flags, swing, mode, and power changes remain outside this boundary.

See `SPRINT_3_1_63_GENERAL_COOL_QUALIFIED_FAN_TEMPERATURE_ENCODER.md`.

## Previous release: 1.0.0-alpha.91

Sprint 3.1.62 generalises the fully qualified **Cool / Fan Auto / Swing Off**
target-state rule to 16.0–31.0 °C in exact 0.5 °C increments. Production
selection no longer depends on a source→target edge registry. Exact cached and
fresh source checks, one write, four UDP sends, zero retries, no fallback,
immediate and delayed verification, and critical unexpected-Power-Off handling
remain mandatory.

See `SPRINT_3_1_62_GENERAL_COOL_FAN_AUTO_TEMPERATURE_ENCODER.md`.

## Alpha.90

Sprint 3.1.61 groups six official-SDK **Cool / Fan Auto / Swing Off**
temperature edges into one deployment and physical test sequence:
20→22.5→24→24.5→20.5→22→20 °C.

See `SPRINT_3_1_61_GROUPED_OFFICIAL_SDK_COOL_FAN_AUTO_TEMPERATURE_MATRIX.md`.

## Alpha.89

Sprint 3.1.60 adds Capture 12's exact **Cool 22.0 °C → 20.0 °C / Fan Auto /
Swing Off** edge. The write is authorised only from an exact nine-field cached
source and matching fresh pre-read. The target bytes are reused only after
those source guards pass, with one write, zero retries, delayed read-only
verification, and critical unexpected-Power-Off handling.

See `SPRINT_3_1_60_OFFICIAL_SDK_COOL_22_TO_20_FAN_AUTO_QUALIFICATION.md`.

## Alpha.88

Sprint 3.1.59 adds Capture 10's exact **Cool 20.0 °C → 22.0 °C / Fan Auto /
Swing Off** edge. The normal temperature selector authorises it only from the
exact nine-field source, repeats that check against a fresh authenticated
pre-read, performs one write with zero retries, and requires exact immediate
and delayed read-only verification. Unexpected Power Off remains critical.
All other uncaptured targets from the 20.0 °C source remain blocked.

See `SPRINT_3_1_59_OFFICIAL_SDK_COOL_20_TO_22_FAN_AUTO_QUALIFICATION.md`.

## Alpha.87

Sprint 3.1.58 adds Capture 11's exact **Cool 20.5 °C → 20.0 °C / Fan Auto /
Swing Off** official-parser frame. The command is available only from its exact
nine-field source, must pass a fresh authenticated pre-read, uses one write
with zero retries, and completes delayed read-only verification. Unexpected
Power Off remains critical.

Every other uncaptured Cool/Fan Auto target from the 20.5 °C source remains
blocked.

See `SPRINT_3_1_58_OFFICIAL_SDK_COOL_20_5_TO_20_FAN_AUTO_QUALIFICATION.md`.

## Alpha.86

Sprint 3.1.57 adds Capture 10's exact **Cool 20.0 °C → 20.5 °C / Fan Auto /
Swing Off** official-parser frame. The command is available only from its exact
nine-field source, must pass a fresh authenticated pre-read, uses one write
with zero retries, and completes delayed read-only verification. Unexpected
Power Off remains critical.

The reverse 20.5 → 20.0 °C edge and every other uncaptured Cool/Fan Auto
target remain blocked.

See `SPRINT_3_1_57_OFFICIAL_SDK_COOL_20_TO_20_5_FAN_AUTO_QUALIFICATION.md`.

## Alpha.85

Sprint 3.1.56 adds Capture 9's exact **Auto/FEEL 20 °C → Cool 20 °C**
transition. York Write Packet Lab generated the immutable
`...44 03 0B...ED` frame offline through the official native parser and did
not transmit it.

Alpha.85 requires the complete nine-field Auto source on both the current
authoritative state and fresh authenticated pre-read, then requires all nine
Cool result fields. It performs one control write, zero automatic retries, no
fallback and delayed read-only verification. Unexpected Power Off remains a
critical failure. Other Auto-temperature sources and every other Auto 20 °C
exit remain blocked.

See `SPRINT_3_1_56_OFFICIAL_SDK_AUTO_FEEL_20_TO_COOL_QUALIFICATION.md`.

## Alpha.84

Sprint 3.1.55 adds the live-confirmed 20 °C result to the explicit Auto/FEEL
program allowlist for the existing Heat 23 °C → Auto edge. The Alpha.83 field
test showed that the unit remained on, entered Auto, preserved Fan Auto and
Swing Off, and returned `status_byte=0x04`; Home Assistant and the indoor
display both showed 20 °C while measured room temperature was 22 °C.

The exact `...44 08 08...E5` command is unchanged. Alpha.84 still requires the
exact nine-field Heat source, exact eight non-temperature Auto result fields,
one separately validated program value, one write, zero retries, no fallback,
delayed read-only verification and critical failure on unexpected Power Off.
All arbitrary Auto values and every uncaptured Auto 20 °C exit remain blocked.

See `SPRINT_3_1_55_AUTO_FEEL_20_PROGRAM_QUALIFICATION.md`.

## Alpha.83

Sprint 3.1.54 adds the one exact Cool 23 °C → Cool 21 °C / Fan Auto /
Swing Off edge needed to resume grouped acceptance after Alpha.82 safely
blocked that previously unqualified source shape. Capture 8's official parser
establishes native target byte `0x0A`; the immutable 31-byte command ends in
checksum `0xEC`.

The source and result each require all nine guarded fields. Alpha.83 performs
one control write, zero automatic retries, no fallback and delayed read-only
verification for up to 30 seconds. Unexpected Power Off remains an immediate
critical failure, and no other Fan Auto temperature transition is enabled.

See `SPRINT_3_1_54_OFFICIAL_SDK_COOL_23_TO_21_FAN_AUTO_QUALIFICATION.md`.

## Alpha.82

Sprint 3.1.53 replaces the narrow byte-17 room-temperature approximation with
the official TCL/York two-byte integer conversion. Capture 7's synchronized
`0x70 0x08` status now publishes 25 °C instead of the incorrect 27 °C, while
all earlier captured 14–17 °C observations remain exact.

Capture 7 also provides the exact official-SDK Auto/FEEL 23 °C → Cool 23 °C
frame. It is admitted only from the full nine-field Auto source, followed by
one control write, zero retries, nine-field Cool verification and the existing
critical unexpected-Power-Off stop. Auto 18 °C is recognized as a valid
program outcome but has no write exit until separately captured.

See `SPRINT_3_1_53_AUTO_FEEL_PROGRAM_AND_INDOOR_TEMPERATURE_CORRECTION.md`.

## Alpha.81

Sprint 3.1.52 consolidates the five physically qualified official-SDK mode
edges into one runtime registry, selector, allowlist, packet builder and
delayed-verification path. No packet or source/target combination was added.

See `SPRINT_3_1_52_QUALIFIED_MODE_LOOP_CONSOLIDATION.md`.

## Alpha.80

Sprint 3.1.51 qualifies one exact Cool 21 °C → Dry transition from York Write
Packet Lab Capture 6. The official native parser generated a 31-byte write
with native `mode=2`, retained `temp=10`, Fan Auto, both swing axes Off and
checksum `ED`. Dry has no selectable target temperature, so the retained byte
is excluded from Home Assistant target publication and result verification.

The source guard requires all nine exact Capture 6 Cool fields on both the
authoritative state and fresh pre-read. The Dry result must match the eight
applicable non-temperature fields. One control write, zero retries, delayed
read-only verification and critical Power Off detection remain mandatory. The
final Alpha.72 Dry command is removed from the production transport allowlist.

See `SPRINT_3_1_51_OFFICIAL_SDK_COOL_21_TO_DRY_QUALIFICATION.md`.

## Alpha.79

Sprint 3.1.50 qualifies one exact Auto/FEEL 21 °C → Cool 21 °C transition
from York Write Packet Lab Capture 5. The official native parser generated a
31-byte write with native `mode=3`, retained `temp=10`, Fan Auto, both swing
axes Off and checksum `EC`. Once Cool is active, that retained temperature is
an applicable 21 °C target setpoint.

The source guard requires the exact nine Capture 5 fields on the authoritative
state and fresh pre-read. The Cool result must match all nine fields. One
control write, zero retries, delayed read-only verification and critical Power
Off detection remain mandatory. Alpha.72's superseded Cool 22 °C command is
removed from the production transport allowlist.

See `SPRINT_3_1_50_OFFICIAL_SDK_AUTO_FEEL_21_TO_COOL_QUALIFICATION.md`.

## Alpha.78

Sprint 3.1.49 qualifies one exact Heat 23 °C → Auto/FEEL transition from York
Write Packet Lab Capture 4. The official native parser generated a 31-byte
write with native `mode=8`, retained `temp=8`, Fan Auto, both swing axes Off
and checksum `E5`.

The source guard compares all nine Heat fields. Auto/FEEL verification requires
the exact eight non-temperature fields and a decoder-representable dynamic
status temperature from 16.0–31.5 °C in 0.5 °C increments. One control write,
zero retries, delayed read-only verification and critical Power Off detection
remain mandatory. The older Heat 25 °C candidate remains outside this new
allowlist.

See `SPRINT_3_1_49_OFFICIAL_SDK_HEAT_23_TO_AUTO_FEEL_QUALIFICATION.md`.

## Alpha.77

Sprint 3.1.48 qualifies one exact Fan-only → Heat transition from York Write
Packet Lab Capture 3. The official native parser generated a 31-byte write with
native `mode=1`, `temp=8`, Fan Auto, both swing axes Off and checksum `EC`.
Once Heat is active, that temperature field is applicable and decodes to a
23 °C target.

The source guard compares eight applicable Fan-only fields and deliberately
ignores its non-applicable placeholder temperature. The Heat result must match
all nine fields. One control write, zero retries, delayed read-only
verification and critical Power Off detection remain mandatory. Every other
Fan-only exit stays blocked.

See `SPRINT_3_1_48_OFFICIAL_SDK_FAN_ONLY_TO_HEAT_QUALIFICATION.md`.

## Alpha.76

Sprint 3.1.47 fixes the MQTT publication defect observed during the Alpha.75
Dry test. Home Assistant's stale retained 23 °C target is now reset with its
documented `None` payload in both Dry and Fan-only, including on the first poll
after restart. The `23 → None` activity transition no longer invokes numeric
formatting, so authoritative reads remain successful rather than being counted
as poll failures. Heat and Cool continue publishing their real numeric
setpoints and restore the target automatically when either mode resumes.

The official-SDK Dry → Fan-only qualification boundary is unchanged: one
write, zero retries, eight applicable fields, delayed read-only verification
and critical Power Off detection. Temperature commands remain blocked in Dry
and Fan-only, and all Fan-only exits remain disabled.

See `SPRINT_3_1_47_MQTT_NON_APPLICABLE_SETPOINT_RESET.md`.

## Alpha.75

Sprint 3.1.46 extends the live temperature correction to Dry mode. The
physical remote and fresh official-SDK captures confirm that Dry and Fan-only
have no selectable target temperature. Climate Bridge therefore omits the
protocol/status temperature value in both modes, rejects temperature commands
before opening a control client, and continues publishing the independent
`indoorTemp` room measurement.

Dry / Fan Auto / Swing Off remains the only enabled source for the exact
official-SDK Fan-only frame. Source and result verification now compare the
eight applicable power, mode, fan, swing and feature fields. The control write
is still single-shot with zero retries, delayed read-only verification and an
immediate critical stop on unexpected Power Off. Fan-only exits remain
disabled. The latest Fan High capture also confirms native `wind=5` and the
SDK's whole-degree indoor-temperature result for odd raw status values.

See `SPRINT_3_1_46_DRY_AND_FAN_ONLY_TEMPERATURE_SEMANTICS.md`.

## Alpha.74

Sprint 3.1.45 corrects Fan-only temperature semantics using the live Write
Packet Lab Capture 2. Fan-only's protocol temperature placeholder is no longer
published or verified as a selectable setpoint. The independent `indoorTemp`
field is decoded and published as Home Assistant's current temperature.

Dry / 17 °C / Fan Auto / Swing Off remains the only enabled Fan-only entry.
Its fresh pre-read still verifies all nine source fields. The resulting
Fan-only state verifies the eight applicable power, mode, fan, swing and
feature fields, with one write, zero retries, delayed read-only polling and
immediate critical failure on unexpected Power Off. Fan-only temperature
commands and all Fan-only exits remain disabled.

See `SPRINT_3_1_45_FAN_ONLY_TEMPERATURE_SEMANTICS.md`.

## Alpha.73

Sprint 3.1.44 enables one exact Dry → Fan-only qualification edge using the
31-byte frame generated offline by York Write Packet Lab v1 through the
official TCL/Broadlink `setSplitAirconInfo()` parser. The captured source and
required live precondition are On / Dry / 17 °C / Fan Auto / Swing Off, with
Turbo, Eco and Health disabled and Display enabled.

The frame is isolated from the remaining-mode matrix and is validated again at
the encrypted production transport boundary. Alpha.73 sends it once, never
retries the write, and performs read-only verification for up to 30 seconds.
All nine guarded fields must match. Unexpected Power Off aborts immediately as
a critical failure. The retired Alpha.71 bytes remain rejected, and Fan-only →
Heat plus every other Fan-only transition remain disabled.

See `SPRINT_3_1_44_OFFICIAL_SDK_FAN_ONLY_QUALIFICATION.md`.

## Alpha.72

Sprint 3.1.43 is a containment release. It removes the unsafe historical
Fan-only command from every active candidate and transport allowlist after the
Alpha.71 Dry → Fan-only test eventually powered the unit Off. Dry → Fan-only
and Fan-only → Heat are disabled before client creation and produce zero UDP
traffic.

The three retained mode edges—Auto → Cool, Cool → Dry and Heat → Auto—now
perform repeated read-only verification for up to 30 seconds. Stale reads do
not cause another write. A valid delayed result may pass; an unexpected Power
Off result raises an immediate critical verification failure. Auto and Dry
retain their bounded dynamic status-temperature handling.

See `SPRINT_3_1_43_FAN_ONLY_CONTAINMENT_DELAYED_VERIFICATION.md`.

## Alpha.71

Sprint 3.1.42 corrects Dry status validation after Alpha.70 physically changed
Cool → Dry but returned a live Dry / 21 °C status instead of the historical
Dry / 16 °C fixture. Dry status comparisons now accept only the decoder's
bounded 16.0–31.5 °C half-degree range while all other fields remain exact.
The captured Dry command remains byte-for-byte unchanged, and Dry temperature
control remains unsupported.

See `SPRINT_3_1_42_DRY_DYNAMIC_STATUS_MODE_MATRIX_CORRECTION.md`.

## Alpha.70

Sprint 3.1.41 connected the five isolated remaining-mode candidates to the
production client transport boundary and added real-client integration tests.

## Alpha.69

Sprint 3.1.40 corrects Auto/FEEL status validation after live testing showed
the decoded temperature following room temperature from 22 °C to 23 °C. Auto
source and target verification now accept only the decoder's bounded 16.0–31.5
°C half-degree range while requiring exact matches for the other eight fields.
The captured Auto command, non-Auto states, ordered sequence, four-send limit,
zero retries and no-fallback policy remain unchanged.

Auto temperature commands remain unsupported.

See `SPRINT_3_1_40_AUTO_FEEL_DYNAMIC_AMBIENT_MODE_MATRIX.md`.

## Alpha.68

Sprint 3.1.39 corrects Alpha.67's Auto/FEEL state from 23 °C to the fixed 22 °C
value repeatedly returned by live authoritative reads. This applies to both
Auto → Cool source matching and Heat → Auto target verification. The four
non-Auto target states remain unchanged.

Auto temperature commands remain unsupported: the physical remote's ±2 °C
FEEL comfort adjustment did not change the Wi-Fi module's authoritative state.
Every edge still requires fresh nine-field pre/post reads, four UDP sends, zero
retries and no fallback.

See `SPRINT_3_1_39_AUTO_FEEL_22C_MODE_MATRIX_CORRECTION.md`.

## Alpha.67

Sprint 3.1.38 added the isolated, ordered Auto → Cool → Dry → Fan-only → Heat
→ Auto qualification matrix from the labelled TFIAC Modes log. Alpha.68
supersedes only its Auto / 23 °C endpoint assumption.

## Alpha.66

Sprint 3.1.37 addresses Alpha.65's controlled Step 5 rejection without
weakening the general fan allowlist. Only the exact authoritative
Heat / 22.5 °C / Low / decoded Horizontal source may use the existing exact
High / Off frame. A fresh nine-field pre-read and nine-field post-read remain
mandatory, with four UDP sends, zero retries and no fallback.

The next Home Assistant Fan High command therefore both qualifies the observed
post-swing compatibility edge and requires the packet state to normalise to
Swing Off. Fan High → Low then uses Alpha.63 unchanged.

See `SPRINT_3_1_37_POST_SWING_FAN_COMPATIBILITY.md`.

## Alpha.65

Sprint 3.1.36 adds one guarded, ordered Heat / 22.5 °C / Fan Low swing matrix:
Off → Vertical → Both → Horizontal → Off. The case-specific targets reuse only
the independently qualified Vertical state, Horizontal command flag,
Horizontal-only state and 22.5 °C temperature delta.

Every command requires its exact source state, fresh nine-field pre-read, one
write, four UDP sends, zero retries and nine-field post-read. Skipped edges and
all nearby state shapes remain fail-closed. The final Low↔High fan pair reuses
the physically verified Alpha.64 path with Swing Off.

See `SPRINT_3_1_36_GROUPED_SWING_QUALIFICATION_MATRIX.md`.

# Climate Bridge 1.0.0-alpha.64

Sprint 3.1.35 adds the guarded Cool / 22.5 °C / Fan Low↔High / Swing Off pair
to the physically verified Alpha.63 Heat pair. The Cool frames change only the
already proven Heat↔Cool mode byte and checksum; the verified Low/High fan and
Swing Off bytes remain unchanged.

The grouped six-command acceptance sequence uses Alpha.63 fan control,
Alpha.62 running-mode control and the new Cool fan pair in one continuous
session. Every command retains its own fresh nine-field pre-read, four UDP
sends, zero retries, and nine-field post-read. Any mismatch stops that command
without authorising the next step.

See `SPRINT_3_1_35_GROUPED_FAN_QUALIFICATION_MATRIX.md`.

# Climate Bridge 1.0.0-alpha.63

Sprint 3.1.34 adds one guarded Fan High / Swing Off qualification at the exact
physically verified Heat / 22.5 °C / Fan Low / Swing Off handoff state. The
candidate keeps all known fields fixed and applies only the fan delta already
proven by the Heat/Vertical Low↔High captures. A matching exact Low/Off frame
provides the guarded return path.

The candidate is isolated from the immutable captured replay allowlist. Every
nearby state remains fail-closed before writing. Eligible execution retains a
fresh nine-field pre-read, one write, four UDP sends, zero retries and a
nine-field post-read.

See `SPRINT_3_1_34_FAN_HIGH_OFF_QUALIFICATION.md`.

# Climate Bridge 1.0.0-alpha.62

Sprint 3.1.33 adds guarded parameterised Heat-to-Cool and Cool-to-Heat control
from the fresh authoritative On state. Both the source and target complete
states must be canonical shapes already qualified through Alpha.60. Eligible
mode changes preserve target temperature, fan and swing, including 0.5 °C
setpoints. Unsupported shapes still stop before client creation, with no write,
retry or fallback.

The new builder reproduces the two historical 25 °C / High / Vertical running
mode anchors exactly without changing the immutable captured replay allowlist.
Alpha.60 parameterised power-on and Alpha.61 parameterised power-off remain
unchanged.

See `SPRINT_3_1_33_PARAMETERISED_RUNNING_MODE_CONTROL.md`.

# Climate Bridge 1.0.0-alpha.61

Sprint 3.1.32 adds guarded parameterised power-off from the fresh authoritative
On state. The command preserves the live mode, target temperature, fan and
swing inside the same complete Heat/Cool target shapes qualified for Alpha.60,
including 0.5 °C setpoints. Unsupported shapes still stop before client
creation, with no write, retry or fallback.

The Power-Off generator clears only the power bit proven by the captured Heat
and Cool On/Off pairs, then recalculates the York XOR. The captured Heat / 25 °C
/ High / Vertical Power-Off frame is reproduced exactly. Historical replay
allowlists remain immutable.

See `SPRINT_3_1_32_PARAMETERISED_POWER_OFF_CONTROL.md`.

# Climate Bridge 1.0.0-alpha.60

Sprint 3.1.31 adds guarded parameterised power-on from the fresh authoritative
Off state. The command preserves the stored target temperature, fan and swing
inside previously qualified Heat/Cool target shapes, including 0.5 °C
setpoints. Unsupported shapes still stop before client creation, with no write,
retry or fallback.

The observed Off / Heat / 21.5 °C / Fan Low / Swing Off state now selects the
exact previously captured Heat / 21.5 °C / Fan Low / Swing Off frame. All
Alpha.59 native-only polling, command rejection and Relay-runtime removal
boundaries remain unchanged.

See `SPRINT_3_1_31_PARAMETERISED_POWER_ON_CONTROL.md`.

# Climate Bridge 1.0.0-alpha.59

Sprint 3.1.30 removes the dormant Relay HTTP client, extraction logger and
fallback execution branches from the production runtime. Existing Alpha.58
configuration remains migration-compatible: `relay` and `tablet_relay` are
accepted as aliases for native LAN, while Relay endpoint and fallback fields
are ignored. New configurations use `transport.type: native` and contain no
Relay URL or fallback setting.

Qualified native packet envelopes, direct-state authority, command guards,
four-send/zero-retry behaviour, polling, restart recovery and MQTT recovery are
unchanged. Historical Relay captures and qualification documents remain as
protocol provenance only.

See `SPRINT_3_1_30_LEGACY_RELAY_RUNTIME_REMOVAL.md`.

# Climate Bridge 1.0.0-alpha.58

Sprint 3.1.29 removes Relay v2 from the live command path for the verified
direct-authority configuration. Alpha.57's working `config.yml` can be copied
unchanged, but guarded native safe-stops and unqualified controls now fail
closed without an HTTP request or automatic command retry.

All previously qualified native packet envelopes and direct read, availability,
recovery, MQTT reconnect, and failure-counter behavior remain unchanged.

See `SPRINT_3_1_29_RELAY_FREE_COMMAND_BOUNDARY.md`.

# Climate Bridge 1.0.0-alpha.57

Sprint 3.1.28 corrects the threshold-facing poll-failure counter observed in
Alpha.56 during a long York-module network interruption. Logs and retry
diagnostics no longer display values above the configured limit, and a
successful direct read resets the next outage sequence cleanly.

No timeout threshold, availability transition, recovery timing, native packet,
command allowlist or Relay fallback boundary changed.

See `SPRINT_3_1_28_POLL_FAILURE_COUNTER_CORRECTION.md`.

## Alpha.56

Sprint 3.1.27 hardens tablet-free startup and recovery. After startup or MQTT
reconnect, Home Assistant availability now waits for a fresh authenticated
direct LAN read. Direct-read interruption and recovery are reported as York
module state-source events rather than tablet failures, and recovery completes
without Relay v2 state access.

No native packet or Alpha.55 command allowlist changed. Relay v2 remains an
optional command fallback for unqualified requests.

See `SPRINT_3_1_27_TABLET_FREE_RESTART_RECOVERY.md`.

## Alpha.55

Sprint 3.1.26 makes the authenticated direct LAN read authoritative for normal
Home Assistant state, availability and every command guard when direct read is
enabled. Relay v2 is no longer polled for state, and Relay command responses
cannot replace direct HVAC state.

Relay v2 remains command-fallback only for unqualified requests. Existing
Alpha.54 native write envelopes and their fresh pre/post reads are unchanged.

See `SPRINT_3_1_26_DIRECT_STATE_AUTHORITY.md`.

## Alpha.54

Sprint 3.1.25 promotes Alpha.53's physically qualified Heat / 21.5 °C / Fan
Low Swing Off → Horizontal and Horizontal → Off transitions into normal
guarded Home Assistant control.

The exact qualified frames retain nine-field pre/post verification, one write,
four UDP sends and zero retries. Every other Horizontal/Both request retains
Relay v2 fallback, and Alpha.53's one-shot tool is removed from the executable
container.

See `SPRINT_3_1_25_NATIVE_HEAT_HORIZONTAL_AXIS_CONTROL.md`.

## Alpha.53

Sprint 3.1.24 adds an explicitly confirmed, qualification-only native path for
Heat / 21.5 °C / Fan Low Swing Off → Horizontal and Horizontal → Off.

The command pair uses exact Relay v2 frames, nine-field pre/post verification,
one write, four UDP sends, zero retries and no automatic restore. The failed
Alpha.49 status-bit candidate remains rejected. Normal Home Assistant
Horizontal routing remains on Relay v2 pending physical qualification.

See `SPRINT_3_1_24_HEAT_HORIZONTAL_AXIS_QUALIFICATION.md`.

## Alpha.52

Sprint 3.1.23 promotes Alpha.51's physically qualified Dry / 21 °C / Fan Low
Vertical → Both and Both → Vertical transitions into normal guarded Home
Assistant control.

Each eligible command requires exact nine-field Relay and direct pre-reads,
sends one write through four UDP transmissions with zero retries, and requires
an exact nine-field post-read. Every other Horizontal/Both request retains
Relay v2 fallback.

See `SPRINT_3_1_23_NATIVE_DRY_HORIZONTAL_AXIS_CONTROL.md`.

## Alpha.51

Sprint 3.1.22 qualified the independent Horizontal axis natively at the
physically observable Dry / 21 °C / Fan Low state using guarded one-shot
Vertical → Both and Both → Vertical writes.

## Alpha.50

Sprint 3.1.21 adds offline validation and explicitly confirmed one-shot cases
for independently toggling the Horizontal axis at 21.5 °C / Heat / Fan Low:
Vertical → Both and Both → Vertical. The exact Relay frame uses command-side
Horizontal flag `0x08`; Alpha.49's failed `0x20` status-bit candidate is
excluded from execution and the write allowlist.

Each case retains fresh nine-field pre/post reads, one write, four UDP sends,
zero retries and no automatic restore. Normal Horizontal and Both routing
remains on Relay v2 pending physical qualification.

See `SPRINT_3_1_21_INDEPENDENT_HORIZONTAL_AXIS_QUALIFICATION.md`.

## Alpha.49

Alpha.49's inferred Horizontal write candidate physically commanded Swing Off.
That negative result is retained as protocol evidence, but the unsafe tool and
frame have been removed from executable release paths.

## Alpha.48

Alpha.48 enables guarded native Swing Vertical ↔ Off control while the York
unit is On / Heat / Fan Low. The command reuses the previously qualified
complete Vertical (`0x3A`) and Off (`0x02`) target-state frames at the current
16–30 °C setpoint, including half-degrees.

Normal control retains fresh nine-field pre/post verification, one write,
four UDP sends, zero automatic retries and Relay v2 fallback. Horizontal,
Both, Fan High and unqualified states remain on Relay v2.

See `SPRINT_3_1_19_GUARDED_NATIVE_SWING_CONTROL.md`.

## Alpha.47

Alpha.47 enables guarded native Fan Low ↔ High control while the York unit is
On / Heat / Swing Vertical. The command reuses the previously qualified
complete Low (`0x3A`) and High (`0x3D`) target-state frames at the current
16–31 °C setpoint, including half-degrees.

Normal control retains fresh nine-field pre/post verification, one write,
four UDP sends, zero automatic retries and Relay v2 fallback. Auto and Medium
remain on Relay v2.

See `SPRINT_3_1_18_GUARDED_NATIVE_FAN_CONTROL.md`.

## Alpha.46

Alpha.46 enables native 0.5 °C increments across 16–31 °C for both qualified
Heat temperature shapes: Fan High/Swing Vertical and Fan Low/Swing Vertical.

The generators retain byte 9 as `31 - whole temperature`, set byte 11 to
`0x02` only for half-degree targets, preserve state bytes `0x3D` and `0x3A`,
and recalculate the York XOR checksum. Invalid increments and out-of-range
targets stop before socket creation.

Normal control retains fresh nine-field pre/post verification, one write,
four UDP sends, zero automatic retries and Relay v2 fallback.

See `SPRINT_3_1_17_HALF_DEGREE_TEMPERATURE_CONTROL.md`.

## Alpha.45

Alpha.45 promotes the Alpha.44 Heat/Fan Low/Swing Vertical whole-degree
generator into normal guarded Home Assistant control across 16–31 °C.

The normal path retains exact pre/post state checks, one write, four UDP sends,
zero automatic retries and Relay v2 fallback. Alpha.44 already validated all
sixteen frames offline and physically proved 25 → 26 → 25 °C without changing
Fan Low or Swing Vertical.

See `SPRINT_3_1_16_PARAMETERISED_LOW_VERTICAL_CONTROL.md`.

## Alpha.44

Alpha.44 adds a qualification-only parameterised Low/Vertical temperature
generator across 16–31 °C. It preserves the exact captured 24 and 25 °C frames,
validates all sixteen whole-degree frames and exposes only the comfortable
25 → 26 → 25 °C live sequence.

Normal Home Assistant Low/Vertical routing remains bounded to the physically
qualified 24 ↔ 25 °C transitions from Alpha.43. Every other target still uses
Relay v2 fallback.

See `SPRINT_3_1_15_PARAMETERISED_LOW_VERTICAL_TEMPERATURE.md`.

## Alpha.43

Alpha.43 enables normal guarded Home Assistant control for the two
Heat/Fan Low/Swing Vertical transitions physically qualified in Alpha.42:
25 → 24 °C and 24 → 25 °C.

Each command requires the exact nine-field Relay state and matching live
direct pre-read, sends one direct write with zero automatic retries, and
requires a matching nine-field post-read. Any other Low/Vertical transition
continues through Relay v2 fallback.

See `SPRINT_3_1_14_GUARDED_LOW_VERTICAL_TEMPERATURE_CONTROL.md`.

## Alpha.42

Alpha.42 adds bounded direct-write qualification for Heat/Fan Low/Swing
Vertical at the two physically captured targets, 24 °C and 25 °C.

Relay v2 transactions #1 and #2 on 2026-07-30 changed the physical unit
25 → 24 °C and 24 → 25 °C while preserving Fan Low and Swing Vertical. The
target frames are fingerprint-locked and expose only matching one-shot cases
with exact nine-field pre/post verification, one write and zero retries.

Normal Home Assistant Low/Vertical temperature routing remains on Relay v2.
See `SPRINT_3_1_13_LOW_VERTICAL_TEMPERATURE_QUALIFICATION.md`.

## Alpha.41

Alpha.41 integrates the Alpha.40-qualified whole-degree
Heat/High/Vertical generator into normal Home Assistant control. Eligible
commands accept targets from 16 through 31 °C, require matching nine-field
Relay and direct preconditions, send one write with zero retries, and require a
matching nine-field post-read.

The earlier Low/Swing Off temperature path remains unchanged. Every other
shape, including Heat/23 °C/Fan Low/Swing Vertical, safely uses Relay v2
fallback without opening a direct client.

## Alpha.40

Alpha.40 confirms and bounds the York unit's complete whole-degree setpoint
range at 16 through 31 °C. Relay v2 captures at 16, 17, 30 and 31 °C all
succeeded and retained the Alpha.39 formula:

`setpoint byte = 31 - temperature`

Offline validation now checks every supported whole-degree target. Live
qualification is limited to the two endpoints, 30 → 31 °C and 31 → 16 °C,
with exact nine-field pre/post verification, one write and zero retries.
Normal MQTT temperature routing remains unchanged and Relay v2 fallback stays
active.

## Alpha.39

Alpha.39 adds capture-backed one-shot qualification for Heat temperature
changes at 24, 25 and 26 °C while preserving normal MQTT temperature routing
and Relay v2 fallback unchanged.

Sprint 3.1.9 integrates the two running mode transitions physically qualified
in Alpha.37 into normal Home Assistant control:

- Heat to Cool
- Cool to Heat

Both cases reuse their exact captured 31-byte target-state frames and SHA-256
fingerprints. The complete nine-field Relay state selects the distinct Power
On or running-mode case before a direct client is created. A matching
nine-field direct pre-read is then required before the single write, followed
by a nine-field post-read. Direct writes retain zero automatic retries.

Any unqualified or ambiguous state, safe stop, or verification failure falls
back to Relay v2 when configured. Fan, swing, features and pending-temperature
power-on requests remain on Relay v2.

## Alpha.37

Sprint 3.1.8 adds qualification-only direct writes for running Heat to Cool and
Cool to Heat transitions at 25 °C / High / Vertical. Relay v2 transactions #4
and #5 on 2026-07-30 verified the physical changes and read-backs.

The two captured packets exactly match the existing qualified target-state
frames for Power On + Cool and Power On + Heat. Alpha.37 does not infer,
generate, or broaden either frame.

Normal MQTT mode changes remain on Relay v2. Existing guarded direct power and
temperature control is unchanged.

Sprint 3.1.7 integrates the Alpha.35-qualified Power Off-from-Heat frame into
normal Home Assistant MQTT control. A `{"power": false}` request now selects
the exact Cool-off or Heat-off fixture using the complete nine-field Relay
state, then confirms the same starting state through the direct pre-read.

The Heat-off path retains the qualified 31-byte frame and SHA-256 fingerprint,
performs one direct write with zero automatic retries, and requires a matching
9/9 direct post-read. An unqualified state, ambiguous state, safe stop, or
verification failure continues to fall back automatically to Relay v2 when
configured. Native Heat/Cool mode changes are not added in Alpha.36.

## Alpha.35 qualification

Sprint 3.1.6 adds an operator-run, one-shot qualification case for the exact
Power Off-from-Heat command captured in successful Relay v2 transaction #7 on
2026-07-30:

```text
BB 00 01 03 19 01 00 40 01 06 3D 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 DB
```

The `off-heat` case requires the exact On/Heat/25 °C/High/Vertical nine-field
live state, its own confirmation token, one direct write, zero retries, and a
9/9 post-read.

## Alpha.34 baseline

Sprint 3.1.5 integrates the exact Power Off, Power On + Heat, and Power On +
Cool cases into normal MQTT control behind the separately disabled
`direct_control.power_enabled` switch. Each eligible request must match its
qualified nine-field relay state and live direct pre-read, uses one captured
31-byte write with zero retries, and requires a matching direct post-read. Any
safe stop or direct failure records its reason and falls back to Relay v2 when
configured. Deferred-temperature power-on requests and all other command
shapes remain on Relay v2.

# Climate Bridge 1.0.0-alpha.33

Sprint 3.1.4 adds an isolated combined Power On + Cool qualification from
successful Relay v2 transaction #4 recorded on 2026-07-29. The exact 31-byte
frame is fingerprinted and may execute only from
Off/Heat/25 °C/High/Vertical with the explicit `on-cool` case and confirmation
token. It permits one write, zero retries, no automatic restore, and requires
a direct nine-field post-read. It does not claim power-only support. Normal
MQTT power and mode commands remain on Relay v2.

# Climate Bridge 1.0.0-alpha.32

Sprint 3.1.3 adds an isolated combined Power On + Heat qualification from the
fresh successful Relay v2 transaction recorded on 2026-07-29. The exact
31-byte frame is fingerprinted and may execute only from
Off/Cool/25 °C/High/Vertical with the explicit `on-heat` case and confirmation
token. It permits one write, zero retries, no automatic restore, and requires
a direct nine-field post-read. It does not claim power-only support. Normal
MQTT power and mode commands remain on Relay v2.

# Climate Bridge 1.0.0-alpha.31

Sprint 3.1.2 corrects the isolated Power Off qualification using the fresh
31-byte command verified by Relay v2 transaction 46. It removes the single
extra zero byte before checksum `D9` in Alpha.30's rejected frame, locks the
new SHA-256 fingerprint, and requires the same exact nine-field precondition,
one write, zero retries, and direct post-write verification. Power On is not
executable in this package. Normal power and mode commands remain on Relay v2.

# Climate Bridge 1.0.0-alpha.30

Sprint 3.1.1 attempted isolated Power Off and Power On qualifications. The
32-byte Power Off frame was rejected by the Wi-Fi module with `0xFFFB` and is
superseded by Alpha.31.

# Climate Bridge 1.0.0-alpha.29

Sprint 3.1.0 adds a disabled-by-default guarded direct temperature path to
normal MQTT control. It performs a nine-field live precondition, one write,
zero retries, and a nine-field post-read. Any failure falls back to Relay v2.
All non-temperature commands continue to use Relay v2.

Sprint 3.0.3 added isolated Heat and Cool qualification targets that are not
matched to captured Relay v2 target frames. Heat 23.5→22.5 °C and Cool
25→24.5 °C each require a separate explicit token, exact 9/9 pre-read, one
write with zero retries, and a 9/9 post-read. The tool remains disconnected
from MQTT, Home Assistant commands, startup, and the normal direct transport.

# Climate Bridge 1.0.0-alpha.27

Sprint 3.0.2 adds an isolated generator for York Heat and Cool temperature
commands in 0.5 °C increments. The first live qualification is restricted to
Heat 24 °C to 23.5 °C and requires the generated frame to match Relay v2
transactions 22/23 exactly before execution. One write, zero retries, 9/9
pre/post verification, and separation from MQTT and startup remain mandatory.

# Climate Bridge 1.0.0-alpha.26

Sprint 3.0.1 adds a second tightly guarded one-shot direct-write qualification
for the captured Heat 23 °C to 24 °C command from Relay v2 transaction 25.
It preserves the 9/9 pre-read, exact confirmation token, one-write/no-retry
policy, post-read verification, and complete separation from MQTT and startup.
The Alpha.25 Cool qualification remains available and unchanged.

# Climate Bridge 1.0.0-alpha.25

Sprint 3.0.0 adds the first tightly guarded direct-write qualification. It is a
separate operator-run tool that accepts one exact official SDK command:
Cool/22 °C/Low/Off to Cool/25 °C/Low/Off. It requires a matching direct read,
an exact confirmation token, sends once without retry, and performs a second
direct read. The normal bridge still uses Relay v2 for every Home Assistant
command; no direct-write MQTT or startup path exists.

# Climate Bridge 1.0.0-alpha.24

Sprint 2.9.3 adds evidence-backed York target-temperature decoding to the
read-only direct observer. Relay/direct comparison now covers nine fields when
both states contain target temperature. Startup validation also rejects the
known `direct_read` indentation error. Relay v2 remains responsible for every
command, and direct LAN remains read-only.

# Climate Bridge 1.0.0-alpha.21

Sprint 2.9.0 adds the first read-only direct-LAN integration to the main
container. It is disabled by default and runs only as a shadow observer beside
the existing relay. Direct control remains unavailable.

# 1.0.0-alpha.20 — Sprint 2.8.3 Relay Command Extraction

- Records the exact JSON command Climate Bridge sends to York TFIAC Relay V2.
- Records relay HTTP responses, timing, hashes and correlation IDs.
- Adds offline extraction summary utility.
- Does not claim to expose the Android relay's internal native York packet.
- No replay or verification safety rules changed.

# Climate Bridge 1.0.0-alpha.19

Sprint 2.8.2 Phase 2 adds the offline York Request Hunter. It ranks only records with positive controller-to-device evidence and excludes known state responses. With the current imported evidence, `NO_REQUEST_CANDIDATES` is the expected result. No packets are verified, made executable, or transmitted.

# Climate Bridge 1.0.0-alpha.14

Sprint 2.7 adds Qualification Report V2 and the guarded one-shot native York state probe with decoder and relay comparison.

# Climate Bridge 1.0.0-alpha.13

## Sprint 2.6 — York Decoder Qualification

This release adds offline, evidence-backed qualification for the York state decoder.

- Adds 14 recovered Protocol Explorer fixtures.
- Validates power, modes, fan speeds, swing, turbo, eco, health and display decoding.
- Produces JSON and Markdown qualification reports in `qualification-reports/`.
- Uses the production decoder, including frame length and XOR checksum checks.
- Does not send any network packets or change the active Relay (Legacy) transport.
- Leaves temperature, sleep, timer and clock unresolved rather than guessing.

## 1.0.0-alpha.13 — Integrated Qualification

Run `python /app/qualification_suite.py`. A healthy bridge should report `PASS (8/8)`, including `York decoder fixtures: 14/14`.
