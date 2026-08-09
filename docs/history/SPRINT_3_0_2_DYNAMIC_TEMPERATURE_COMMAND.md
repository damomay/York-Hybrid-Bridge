# Sprint 3.0.2 — Dynamic Temperature Command Qualification

Alpha.27 introduces an isolated, evidence-backed generator for York temperature
commands. It does not enable normal direct control.

The generator supports only the captured command shape for an AC that is on,
using Heat or Cool, Fan Low, Swing Off, Display On, and no auxiliary features.
It accepts 16–30 °C in 0.5 °C increments and creates the York XOR checksum.

The live qualification is deliberately narrower:

- required state: On / Heat / 24 °C / Fan Low / Swing Off
- generated target: Heat / 23.5 °C
- the generated 31-byte frame must match Relay v2 transactions 22 and 23
- exact confirmation token
- one write, zero retries
- direct pre-read and post-read
- no MQTT, startup, automatic restore, or normal transport integration

Offline validation:

```sh
python /app/york_dynamic_temperature_qualification.py
```

The offline command opens no socket. Only after reviewing its output may the
operator run:

```sh
python /app/york_dynamic_temperature_qualification.py \
  --execute \
  --confirm WRITE-GENERATED-HEAT-24-TO-23P5-ONCE
```
