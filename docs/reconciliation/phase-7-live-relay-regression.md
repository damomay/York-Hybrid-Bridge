# Phase 7 — One-device Android-relay live regression

Status: PASS.

## Scope

Phase 7 tested the existing Android-relay path with one York air conditioner.
It did not enable native transmission, remove the tablet or test a second
device.

The deployed source was the exact Phase 6-qualified commit
`9eb05bf813ebec54e2308c3f4a3e7ae5a688efe3`.

## Results

Every command agreed across Home Assistant, returned MQTT state and physical
behaviour:

1. startup, MQTT connection and 64 discovery entities;
2. state reporting while the unit was off;
3. power on;
4. heat-to-cool mode change at 24 °C;
5. target change to 22 °C;
6. low fan command, high fan confirmation and high-to-low physical comparison;
7. vertical swing on and off;
8. power off; and
9. Climate Bridge container restart.

The restart produced a clean signal-15 shutdown, reconnected MQTT and relay,
republished discovery, resumed polling and returned Home Assistant to the
correct Off state. The physical unit remained off throughout, and startup sent
no command.

No duplicate commands, unexpected setting changes, state disagreements,
recovery loops or native/direct activity were observed.

## Decision

The current one-device Android-relay path passed its controlled live
regression. This result does not qualify native control or multiple-device
operation.
