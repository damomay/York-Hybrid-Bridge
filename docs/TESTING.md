# Testing and qualification

Run safe checks from the repository root. Python 3.12 matches the container and
GitHub workflow baseline.

## Offline local gate

```bash
python -m compileall -q -f .
python phase6_quality_gate.py
python release_verifier.py
python -c "from pathlib import Path; from validate_config import validate; print('Example transport:', validate(Path('config.example.yml')))"
python -m pytest
python york_decoder_qualification.py --no-write
git diff --check
git status --short
```

The accepted V1 reconciliation recorded 773 passing tests, a passing Phase 6
gate and release verifier, a valid `native` example, and 14/14 decoder fixtures.
Counts can legitimately rise; investigate reductions and never conceal failures
with weakened assertions, broad mocks, unexplained skips, or xfails.

Documentation-only work should run all safe applicable offline checks. If a
check generates files, changes runtime state, needs unavailable dependencies,
or requires hardware/network access, report it as not run with the reason.

## Docker and live boundaries

The GitHub qualification workflow is the authoritative network-free container
gate. Local `docker compose up` is not an offline test: normal startup connects
to configured MQTT and HVAC endpoints. Do not build, deploy, start, or stop a
live installation unless that operation is explicitly in scope.

Live HVAC qualification requires Damien's approval, a named device and case,
physical observation, an expected result, rollback readiness, and a stop on any
unexpected command, retry, state change, or reported/physical disagreement.

## Protocol tools

Decoder and classifier help or no-write modes may be used offline. Replay,
native probes, capture collection, imports containing private evidence, and any
command path require their own reviewed authorization. Consult
`protocols/york/README.md` and `AGENTS.md`; packaging is not proof of safety.
