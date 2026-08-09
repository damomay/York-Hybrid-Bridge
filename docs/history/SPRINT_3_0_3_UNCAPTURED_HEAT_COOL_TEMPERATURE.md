# Sprint 3.0.3 — Uncaptured Heat/Cool Temperature Qualification

Alpha.28 tests the qualified York temperature generator against two live target
temperatures for which no matching Relay v2 target frame is used:

- Heat 23.5 °C to 22.5 °C
- Cool 25 °C to 24.5 °C

Both cases are hard-coded qualification targets. Each requires an exact 9/9
live precondition, its own confirmation token, one write, zero retries, and a
direct post-read. A failed precondition stops after authentication and the
pre-read, before the command is generated or transmitted.

Normal Climate Bridge control remains on Relay v2. The Alpha.28 tool is not
connected to MQTT, Home Assistant commands, container startup, or the normal
direct transport. Automatic restore remains disabled.

Offline validation:

```sh
python /app/york_uncaptured_temperature_qualification.py
```

This validates both cases without opening a socket. Only one live case is
executed at a time, after its offline output and starting state are reviewed.
