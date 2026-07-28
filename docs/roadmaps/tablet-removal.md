# Tablet removal implementation roadmap

Status: NOT STARTED.

Starting baseline:
`137b509b5dadd6459b43f70c5a8295beba477d5c`

The working production path remains:

```text
Home Assistant → MQTT → Climate Bridge → Android relay → York AC
```

The Phase 11 Synology deployment remains the rollback path throughout native
protocol work.

## Stage 1 — Native command discovery

Objective: obtain a complete, traceable controller-to-device request without
promoting relay JSON or device state responses into native commands.

Required work:

1. Capture or instrument the Android application at the point where it
   constructs the native York request.
2. Preserve direction, endpoint, timestamp, action marker, raw bytes and
   source provenance.
3. Import evidence through the existing guarded capture pipeline.
4. Keep candidate records `observed` and `safe_to_transmit: false`.
5. Independently verify checksum, framing and expected state relationship.

Exit condition: at least one complete controller request has reproducible
provenance and independent human verification. No transmission is authorized
by this stage.

## Stage 2 — Direct communication qualification

Objective: qualify the complete native connection and state path offline
before replacing any relay behaviour.

Required work:

1. Verify discovery, addressing, connection, session and timeout behaviour.
2. Verify request encoding and response decoding against captured fixtures.
3. Prove one-shot, no-retry and no-startup-command safety controls.
4. Add deterministic failure, recovery and rollback tests.
5. Keep `direct_device.enabled: false` as the default.

Exit condition: deterministic tests and captured evidence support a bounded
single-device candidate, with no change to the running relay deployment.

## Stage 3 — Controlled single-device direct test

Objective: test one verified request at a time against one York unit.

Required work:

1. Obtain explicit approval for the exact command and expected physical state.
2. Preserve the running relay deployment and configuration backup.
3. Send once with automatic retry disabled.
4. Observe the physical unit and returned state.
5. Stop immediately on mismatch, timeout, duplicate action or unexpected
   startup behaviour.

Exit condition: the approved power, mode, temperature, fan, swing, off and
restart matrix passes without repeats or unexpected commands.

## Stage 4 — Tablet removal

Objective: make the qualified native path operational without the Android
relay while retaining a reversible relay fallback.

Required work:

1. Promote direct transport only after Stage 3 passes.
2. Preserve explicit transport selection and relay rollback.
3. Re-run clean build, MQTT discovery, live control and restart recovery.
4. Update user documentation only to the behaviour actually verified.

Exit condition: one York unit operates reliably after tablet removal and
returns safely to relay mode when requested.

## Stage 5 — Multiple-device support

This stage is locked until tablet-free single-device operation passes.

Required work:

1. Add explicit per-device configuration and stable unique MQTT identifiers.
2. Isolate connection lifecycle, state, diagnostics and recovery per unit.
3. Verify the two available York units independently.
4. Prove one unit cannot command, overwrite or destabilize the other.

Exit condition: both units operate and recover independently, including
container restart and one-device failure containment.

## Later work

Broader HVAC adapter framework work remains locked until York device
boundaries are proven through the stages above.

## Continuing safety rules

- Reliability before feature count.
- No inferred or generated packet becomes executable.
- No real device address, MAC, credential, private path or raw private capture
  enters the tracked repository.
- Every live command requires an expected result and rollback.
- The Android relay remains the default until the native gate explicitly
  passes.
