# Sprint 3.1.29 — Relay-Free Command Boundary

Alpha.58 removes Relay v2 from the live command path used by direct-authority
installations. The physically verified Alpha.57 configuration remains valid,
including its historical `transport: relay` and `fallback_to_relay: true`
fields, but the runtime constructs a local fail-closed command boundary instead
of a Relay HTTP transport.

## Runtime boundary

- Authenticated direct LAN reads remain authoritative for state and every
  command guard.
- Existing guarded native power, mode, temperature, fan, and swing managers
  retain their exact packet allowlists and verification rules.
- A native safe-stop is reported as a rejected command and never becomes a
  Relay request.
- Commands without a qualified native path are rejected after a fresh direct
  read, without HTTP calls or command retries.
- The last confirmed direct state is republished after an MQTT command
  rejection so Home Assistant cannot retain an optimistic unverified value.

Relay extraction code and historical qualification references remain available
as engineering evidence. They are not constructed or contacted by the
direct-authority runtime.

## Non-goals

Alpha.58 adds no packet, state shape, mode, feature, temperature, fan, or swing
combination to the native allowlist. It does not change polling, availability,
recovery timing, MQTT reconnect behavior, or the Alpha.57 failure counter.
