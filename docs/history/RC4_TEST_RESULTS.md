# York Hybrid Bridge RC4 Qualification Results

- Tester:
- Start date/time:
- Bridge version: 3.0.0-rc.3.5
- Qualification suite version: 1.0.0
- Synology/DSM: DS1522+ / DSM 7.3.2
- Home Assistant version:
- Tablet/Android version:

## Automated self-test

| Test | Before fault tests | After fault tests | End of soak |
|---|---|---|---|
| Safe qualification suite |  |  |  |

Attach or retain the generated JSON and Markdown reports from `qualification-reports/`.

## Functional tests

| Test | Expected result | Result | Notes |
|---|---|---|---|
| Set temperature | Physical AC and HA state update |  |  |
| Change HVAC mode | Physical AC and HA state update |  |  |
| Change fan mode | Physical AC and HA state update |  |  |
| Display toggle | Physical AC and HA state update |  |  |
| Eco toggle | Physical AC and HA state update |  |  |
| Health toggle | Physical AC and HA state update |  |  |
| Sleep toggle | Physical AC and HA state update |  |  |
| Turbo toggle | Physical AC and HA state update |  |  |
| Command diagnostics | Result, timing and transaction update |  |  |

## Failure and recovery tests

| Test | Expected recovery | Result | Recovery time / Notes |
|---|---|---|---|
| Tablet relay stopped 30 s | Warning, then automatic recovery |  |  |
| Mosquitto stopped 30 s | Reconnect and rediscover |  |  |
| Home Assistant restart | Entities and operation return |  |  |
| Bridge container restart | Clean startup to READY |  |  |
| Android tablet restart | Relay and polling recover |  |  |

## Soak test

- Soak duration:
- Manual interventions:
- Container restarts:
- MQTT reconnects:
- Recoveries:
- Poll errors:
- Poll success rate:
- Command failures:
- Command success rate:
- Stability score/rating:
- Slowest poll:
- Slowest command:

## Final qualification decision

- [ ] PASS — suitable for v3.0 Final preparation
- [ ] CONDITIONAL PASS — minor issue documented
- [ ] FAIL — requires RC4 code changes

Notes:
