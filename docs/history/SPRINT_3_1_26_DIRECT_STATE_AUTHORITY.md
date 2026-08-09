# Sprint 3.1.26 — Direct-State Authority

## Objective

Make the authenticated York LAN read the only HVAC state source used by Home
Assistant and guarded command selection. This removes the runtime dependency on
Relay v2 state without expanding any native write boundary.

## Runtime boundary

- With `direct_read.enabled: true`, every normal poll performs one authenticated
  direct read from the York module.
- Relay v2 `/state` is never called by normal polling.
- Every MQTT command begins with a fresh direct read before defer, route or
  guard decisions.
- A failed direct refresh stops command selection; Relay state is not used as a
  substitute.
- Relay v2 remains available only for command fallback in this stage.
- After a Relay fallback command, its HVAC state payload is discarded. A fresh
  direct read is published instead; if that refresh fails, the last confirmed
  direct state is retained and marked stale in transaction diagnostics.

## Preserved safety boundary

Alpha.55 does not add, infer or modify a York write packet. All qualified native
power, mode, temperature, fan and swing paths from Alpha.54 retain their exact
pre-read, write, post-read, send-count and zero-retry rules. Unqualified commands
continue to use Relay v2 command fallback until the separate fallback-removal
stage.

## Qualification

The focused tests prove that false or conflicting Relay state cannot be
published, cannot select a native case and cannot satisfy a command guard. They
also prove that direct-read failure prevents Relay command transmission, while a
successful Relay fallback is followed by direct-state publication.

Physical deployment should keep Relay v2 running. After startup, verify normal
Home Assistant state tracking, then stop only the Relay v2 application for a
read-only observation window. Do not issue an unqualified command while Relay v2
is stopped; fallback removal is not part of Alpha.55.
