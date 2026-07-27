# York Hybrid Bridge RC4 Qualification Guide

This package uses the stable **3.0.0-rc.3.5** bridge as the production baseline. The qualification tools do not alter AC settings and do not replace the normal bridge process.

## 1. Automated safe self-test

Run this inside the `york-hybrid-bridge` container terminal:

```sh
python /app/qualification_suite.py /config/config.yml
```

The safe suite checks:

1. Configuration parsing and credentials.
2. All bridge Python modules import correctly.
3. MQTT broker TCP reachability.
4. Authenticated MQTT connection using a separate temporary client ID.
5. Live bridge and AC availability topics.
6. Tablet relay `/state` response and basic AC-state schema.
7. Home Assistant discovery generation and AC/bridge device ownership.

Reports are written to the Synology project folder under:

```text
qualification-reports/
```

A successful result ends with:

```text
RESULT: PASS (7/7 checks passed)
```

## 2. Manual functional qualification

Record PASS or FAIL in `RC4_TEST_RESULTS.md`.

- Change target temperature and verify the physical AC responds.
- Change HVAC mode and verify the physical AC responds.
- Change fan mode.
- Toggle Display, Eco, Health, Sleep and Turbo where supported.
- Confirm command result, duration, transaction ID and counters update on York Hybrid Bridge.
- Confirm York AC2 state returns to the actual physical state after each command.

## 3. Controlled failure qualification

Perform one test at a time and allow the bridge to return to `ready` before continuing.

### Tablet relay interruption

1. Stop the tablet relay for 30 seconds.
2. Confirm relay status and health change appropriately.
3. Restart the relay.
4. Confirm polling resumes, a recovery is recorded, and health returns to excellent.

### MQTT interruption

1. Stop Mosquitto for approximately 30 seconds.
2. Confirm the bridge records MQTT loss without crashing.
3. Restart Mosquitto.
4. Confirm automatic reconnect, discovery republish and resumed state publication.

### Home Assistant restart

1. Restart Home Assistant only.
2. Confirm MQTT entities remain or rediscover correctly.
3. Confirm commands and state updates continue.

### Container restart

1. Restart the York bridge container.
2. Confirm the startup sequence reaches `Bridge READY`.
3. Run the automated self-test again.

### Tablet restart

1. Restart the Android tablet.
2. Relaunch or confirm auto-start of the relay.
3. Confirm bridge recovery without restarting the Synology container.

## 4. Soak qualification

Run RC3.5 continuously for at least 24 hours, preferably 72 hours.

At the end, record:

- container restarts;
- MQTT reconnects;
- relay recoveries;
- poll errors and poll success rate;
- command failures and command success rate;
- stability score/rating;
- slowest poll and command time;
- any manual intervention required.

Run the automated self-test at the beginning and end of the soak period and keep both reports.

## Safety

The automated self-test is read-only. It does not send AC commands, stop services, restart containers, or alter Home Assistant discovery topics.
