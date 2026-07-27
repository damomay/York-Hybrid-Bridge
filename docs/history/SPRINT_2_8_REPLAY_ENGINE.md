# Sprint 2.8 — York Replay Engine

The replay engine is a guarded one-shot execution layer.

It will only load a packet record when it is marked `verified`, has direction
`controller_to_device`, and purpose `state_request`. It opens the XML broadcast
listener before transmitting, sends the captured request once over UDP, waits
for a `statusUpdateMsg`, compares the observed XML state with `expected_state`,
and writes a JSON report under `/reports/replay`.

No commands are generated and no retry loop is enabled. Until a verified
request record exists, both validation and live replay stop before opening a
socket.

## Commands

```sh
python /app/york_replay_engine.py --validate-only
python /app/york_replay_engine.py
```
