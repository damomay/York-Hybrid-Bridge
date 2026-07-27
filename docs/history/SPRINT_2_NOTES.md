# Climate Bridge Sprint 2.1

## Included
- Credential-free startup banner.
- Native York endpoint configuration (`direct_device`).
- Direct endpoint validation.
- Native UDP socket lifecycle scaffold.
- Regression tests for the banner and native transport foundation.

## Current limitation
`york_direct` is not ready for production. State polling, authentication, packet encoding/decoding and commands remain unimplemented. Keep `transport.type: relay` for normal operation.
