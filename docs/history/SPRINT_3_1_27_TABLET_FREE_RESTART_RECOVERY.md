# Sprint 3.1.27 — Tablet-Free Restart and Recovery

Alpha.56 hardens the Alpha.55 Direct-State Authority path for operation while
Relay v2 is stopped. It does not add or broaden any native York write packet.

## Behaviour

- MQTT connection proves only that the bridge process is online.
- The Home Assistant climate entity remains unavailable until a fresh,
  authenticated direct LAN read succeeds after startup or MQTT reconnect.
- Repeated direct-read failures make the climate entity unavailable without
  making the container unhealthy or causing a restart loop.
- Successful direct polling automatically restores availability, current state
  and recovery diagnostics without reading Relay v2.
- Startup and health messages identify the direct LAN state source rather than
  describing a stopped tablet as the active state transport.
- Relay v2 remains optional command fallback for unqualified commands. A
  stopped fallback cannot overwrite the last authoritative direct state.

## Physical qualification sequence

1. Leave Relay v2 stopped.
2. Start Alpha.56 and confirm a direct authoritative read restores the entity.
3. Restart only the Alpha.56 container and confirm state returns unchanged.
4. Temporarily interrupt the York module's network connectivity and confirm the
   climate entity becomes unavailable after the configured failure threshold.
5. Restore connectivity and confirm the entity and correct state recover
   automatically.
6. Repeat the already-qualified Heat / 21.5 °C / Fan Low / Swing Off ↔
   Horizontal native command as a final regression check.

The AC network interruption is performed only after the clean container-restart
test passes. No command is issued while state authority is unavailable.
