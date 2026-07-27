# York packet library

Each JSON file represents one captured protocol frame and its evidence.

Only a record with all of the following properties may be transmitted by the native probe:

- `status`: `verified`
- `direction`: `request`
- `purpose`: `state_request`
- a complete `frame_hex` beginning with `BB`
- a traceable `source`

`template.json` is never executable. Partial, remembered, reconstructed, or merely observed frames must remain `unverified` or `observed`.

The Sprint 2.5 native probe searches this directory by record ID. If no verified state request exists, it exits before opening a network socket.
