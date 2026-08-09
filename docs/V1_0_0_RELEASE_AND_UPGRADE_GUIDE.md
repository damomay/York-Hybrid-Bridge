# Climate Bridge v1.0.0 Release and Upgrade Guide

## Release boundary

Climate Bridge v1.0.0 is the stable promotion of the physically accepted
Beta.1 implementation. It adds no protocol behaviour and does not widen any
command or transport allowlist.

## Supported Home Assistant controls

- Power On and Off from qualified authoritative states.
- Normal Cool and Heat operation across qualified state shapes.
- Cool temperature control from 16.0–31.0 °C in 0.5 °C increments with Swing
  Off while preserving Fan Auto, Low or High.
- Previously qualified Heat temperature combinations.
- Guarded Fan Low to High and High to Low changes. Fan Auto is reported and
  preserved but is not selectable from Low or High.
- Guarded Swing Off, Vertical, Horizontal and Both changes only from their
  physically qualified Heat or Dry source states.
- Restricted Dry, Fan Only and Auto/FEEL mode-loop transitions from their exact
  qualified source states.
- Direct reporting of power, mode, setpoint, room temperature, fan, swing,
  availability, firmware and diagnostics. Physical-remote changes are read
  directly from the unit and reflected in Home Assistant.

Fan Medium and the Turbo, Eco, Health, Display and Sleep switches are not
advertised. Timer, general Auto/FEEL setpoint control, general Dry or Fan Only
setpoint control, arbitrary fan or swing combinations, a second York unit and
other AC adapters are outside v1.0.0.

## Upgrade from Beta.1

1. Stop the existing Climate Bridge project/container.
2. Preserve the working `config.yml`; it is deliberately not included in this
   archive.
3. Extract this archive so its single parent folder remains intact.
4. Copy the preserved `config.yml` into that folder beside
   `docker-compose.yml`. Use `config.example.yml` only as a reference.
5. Build and start the project using the same Synology Container Manager
   procedure used for Beta.1.
6. Keep the existing MQTT topics and Home Assistant device; no entity
   reconfiguration is required.

## Post-deployment confirmation

No formal physical retest is required. Confirm only:

1. The log reaches `Bridge READY`.
2. Home Assistant reports firmware `1.0.0`.
3. The existing AC state is read correctly.
4. One ordinary command succeeds and the resulting authoritative state is
   reported correctly.

If any of these checks fails, stop and retain the complete startup/command log
before issuing further commands.
