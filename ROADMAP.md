# Climate Bridge roadmap

## Current baseline

Climate Bridge `1.0.0-alpha.20` is a reconciliation alpha.

The verified operational path is:

```text
Home Assistant → MQTT → Climate Bridge → Android relay → York AC
```

The Android relay remains required. Native York command transmission,
tablet removal, multiple-device operation and broader vendor support are not
current features.

## Reconciliation

The active reconciliation joins:

- the proven York Hybrid Bridge 3.0 RC5 relay runtime;
- the polished York Hybrid Bridge repository and 18-test baseline; and
- Climate Bridge alpha.20 architecture and protocol-evidence tooling.

Before reconciliation closes, the repository must have one accurate identity,
green automated and container gates, a passed one-device relay regression,
qualified protocol claims, consolidated documentation, an approved pull
request and a reproducible post-merge result.

Feature work remains frozen until those gates pass. In particular, no
reconciliation change may silently enable native transmission.

## Locked order after reconciliation

### 1. Native command discovery and tablet removal

Identify complete native controller requests from traceable captures or
authorized Android instrumentation. Keep responses, relay JSON and native
requests as separate evidence types. No packet advances without capture
provenance and a documented safety decision.

**Exit condition:** a complete native request/response path is verified
offline, with rollback and no-send defaults preserved.

### 2. Direct-device communication qualification

Qualify discovery, connection lifecycle, authentication/session behaviour,
polling, decoding, timeouts, recovery and packet checksums without replacing
the working relay deployment.

**Exit condition:** deterministic tests and captured evidence support a
bounded direct-communication candidate.

### 3. Controlled single-device direct testing

Test one York unit, one command at a time, with physical observation, returned
state and a working relay rollback path.

**Exit condition:** the approved control matrix passes without repeats,
unexpected changes or startup commands.

### 4. Multiple-device support

Only after direct single-device behaviour is qualified, add explicit
per-device configuration, unique MQTT identity, lifecycle isolation and
failure containment. Validate both of the available York units without
allowing one device to affect the other.

**Exit condition:** two devices operate independently and recover
independently.

### 5. Broader HVAC adapter framework

Generalize shared bridge services only after York boundaries are proven. Add
vendor adapters through explicit capability models rather than speculative
abstraction.

**Exit condition:** a second adapter can share MQTT, discovery, diagnostics
and recovery without York-specific leakage.

## Continuing priorities

Across every milestone:

- reliability before feature count;
- local operation and transparent dependencies;
- evidence-backed protocol conclusions;
- reversible, bounded changes;
- sanitized captures and logs;
- tests that preserve meaningful assertions; and
- documentation that matches the verified code and hardware evidence.

## Not promised by alpha.20

- tablet-free control;
- native command transmission;
- automatic device discovery;
- multiple York devices in one runtime;
- support for another HVAC vendor;
- a web diagnostics interface; or
- automatic release/update management.

These may be planned directions, but they must not be presented as shipped
features before their gates pass.
