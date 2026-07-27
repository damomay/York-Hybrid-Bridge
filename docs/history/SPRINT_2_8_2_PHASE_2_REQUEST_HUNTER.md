# Sprint 2.8.2 Phase 2 — York Request Hunter

Alpha 19 adds a conservative, offline request-candidate analysis tool.

## Command

```sh
python /app/york_request_hunter.py
```

## Safety

- Opens no network sockets.
- Transmits no packets.
- Does not modify observed evidence.
- Does not write to the verified packet library.
- Optional candidate files remain `observed` and `safe_to_transmit: false`.

## Expected result with the current evidence

The 23 imported records are expected to be excluded as known state responses. A result of `NO_REQUEST_CANDIDATES` is evidence that a new full-duplex controller capture is still required, not a tool failure.
