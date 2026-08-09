# Sprint 3.0.1 — Heat One-Shot Direct-Write Qualification

Alpha.26 adds a second operator-run qualification tool for one captured
Heat-mode command. It does not connect direct writes to MQTT, Home Assistant,
bridge startup, or the normal transport. The proven Alpha.25 Cool tool remains
available but is unchanged.

## Fixed qualification

- Required live state: On, Heat, 23 °C, Fan Low, Swing Off, Turbo Off, Eco Off,
  Health Off, Display On.
- Fixed result: the same state at 24 °C.
- Command source: the official York/TCL Android SDK output captured by York
  TFIAC Relay v2 transaction 25 and verified there by the subsequent state.
- Command frame: `BB 00 01 03 19 01 00 44 01 07 02 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 E1`.

The tool authenticates once, reads and checks all nine decoded fields, sends
the exact command once, then reads and checks all nine fields again. Any
precondition mismatch stops before the command. There are no retries and no
automatic restore command.

## Operator commands

Validation opens no socket:

```sh
python /app/york_heat_one_shot_write_qualification.py
```

Execution requires both flags and the exact token:

```sh
python /app/york_heat_one_shot_write_qualification.py \
  --execute \
  --confirm WRITE-HEAT-23-TO-24-ONCE
```

Relay v2 remains available for manual restoration after the result has been
recorded.
