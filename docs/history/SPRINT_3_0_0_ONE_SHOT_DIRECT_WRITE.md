# Sprint 3.0.0 — One-Shot Direct-Write Qualification

Alpha.25 adds one operator-run qualification tool. It does not connect direct
writes to MQTT, Home Assistant, bridge startup, or the normal transport.

## Fixed qualification

- Required live state: On, Cool, 22 °C, Fan Low, Swing Off, Turbo Off, Eco Off,
  Health Off, Display On.
- Fixed result: the same state at 25 °C.
- Command source: the official York/TCL Android SDK output captured by York
  TFIAC Relay v2 transaction 2 and verified there by the subsequent state.
- Command frame: `BB 00 01 03 19 01 00 44 03 06 02 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 E2`.

The tool authenticates once, reads and checks all nine decoded fields, sends
the exact command once, then reads and checks all nine fields again. Any
precondition mismatch stops before the command. There are no retries and no
automatic restore command.

## Operator commands

Validation opens no socket:

```sh
python /app/york_one_shot_write_qualification.py
```

Execution requires both flags and the exact token:

```sh
python /app/york_one_shot_write_qualification.py \
  --execute \
  --confirm WRITE-COOL-22-TO-25-ONCE
```

Relay v2 remains available for manual restoration after the result has been
recorded.
