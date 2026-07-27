# Phase 4 — Product identity, versioning and configuration

Status: PASS.

## Scope

Phase 4 established one current Climate Bridge identity and one canonical
`1.0.0-alpha.20` version source. It reconciled committed configuration examples
and validation without changing the relay protocol, enabling York-direct
transmission, removing the tablet, adding devices, or altering `main`.

York Hybrid Bridge remains in current documents only where it identifies the
project's historical lineage. Historical changelog entries retain their
original product name and version.

## Identity and version

- `VERSION` is the canonical application version source.
- `version.py` exposes `APP_NAME`, `APP_VERSION` and the compatibility
  `__version__` alias from that source.
- The startup banner, diagnostics, Home Assistant discovery, qualification
  tools and research-tool banners consume the shared version constants.
- Runtime, Docker Compose, OCI product labels, issue templates, release
  workflow and current project documentation use Climate Bridge.
- The Docker image includes both `VERSION` and `version.py`.

## Configuration

- The proven Android relay remains the default transport.
- York-direct mode remains disabled in the committed example and is rejected
  by startup validation unless its explicit safety requirements are present.
- The example contains no device-specific IP address, MAC address, password or
  token.
- Empty MQTT username and password values accurately represent anonymous
  broker access.
- A configured username with an intentionally empty password is preserved and
  passed to the MQTT client.
- Relay URLs require an explicit HTTP or HTTPS scheme.
- Startup validation now consumes the same `Config` model as the running
  bridge, preventing duplicate defaults from drifting.

## Gate 4 checks

- Targeted identity, configuration, transport and transmission-safety tests:
  19/19 PASS.
- Complete reconciled suite: 72/72 PASS.
- Python compile check: PASS.
- Example configuration parse and startup validation: PASS.
- Workflow, Compose and example YAML parse: PASS.
- Current-version and product-identity search: PASS.
- Historical York Hybrid Bridge references limited to lineage/history: PASS.
- `git diff --check`: PASS.
- Relay protocol logic changed: no.
- Experimental transmission enabled: no.
- `main` changed: no.

The bounded commit
`3a058233b373d72222308b8d6d59fde2d218cc50` was published to
`feature/climate-bridge-reconciliation` and remotely verified. `main` remained
unchanged.
