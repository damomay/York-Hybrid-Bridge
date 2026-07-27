# Phase 6 — Static, Packaging and Container Qualification

## Scope

Phase 6 qualifies the reconciled Climate Bridge tree before live HVAC testing.
It does not change the normal container command, transport selection, relay
protocol behaviour, experimental transmission guards, or hardware access.

Base commit:
`a7c6a8d52d5ddbc98b92d43ab688f471c3725db1`

## Qualification support

- `phase6_quality_gate.py` parses tracked JSON and YAML and rejects tracked
  caches, compiled output, runtime reports, private network addresses, device
  MAC addresses, personal filesystem paths, private-key headers and common
  token signatures.
- `container_qualification.py` validates the packaged configuration, imports
  the production module set, records runtime and dependency versions, exposes
  a heartbeat health check, and handles `SIGTERM` without opening a socket.
- `.github/workflows/qualification.yml` performs a no-cache Docker build,
  labels the image with the canonical version and Git revision, starts the
  image with the network-free qualification command, checks container health
  and logs, stops it, and requires exit code 0.
- The Dockerfile's normal `CMD` remains unchanged. The qualification command
  is selected only by the Phase 6 workflow's explicit command override.

## Local evidence

Toolchain:

- Python 3.12.13
- paho-mqtt 2.1.0
- requests 2.32.4
- PyYAML 6.0.2
- pytest 9.1.1

Results:

- Complete pytest suite: 112 passed.
- Phase 6 qualification tests: 3 passed.
- Forced Python compilation: passed.
- Release/package verifier: passed for Climate Bridge 1.0.0-alpha.20.
- Example configuration validation: passed in relay mode.
- Tracked-tree and manifest scan: passed across the final 162-file staged tree.
- Cached, compiled and test output remained ignored.
- Staged diff check: passed.

## Remote container gate

GitHub Actions run
`https://github.com/damomay/York-Hybrid-Bridge/actions/runs/30255500545`
qualified commit `9eb05bf813ebec54e2308c3f4a3e7ae5a688efe3` on a Docker
runner and recorded:

- clean image build;
- canonical image version and commit revision;
- healthy network-free container startup;
- log confirmation that MQTT, relay and HVAC access are disabled;
- predictable `SIGTERM` shutdown;
- container exit code 0; and
- clean tracked tree after compilation and the complete test suite.

All remote checks passed, including 112/112 tests and a clean exit code 0.
Gate 6: PASS.
