# Phase 5 — Complete Test Suite

## Scope

Phase 5 restored every alpha.20 test module that was approved by the Phase 1
manifest, kept the six organized repository tests as the canonical copies, and
retained the four reconciliation gate modules added in Phases 3 and 4.

The Android relay remains the default transport. No native York command was
enabled and no guarded transmission requirement was weakened.

## Reproduced starting failures

The untouched alpha.20 tree reproduced the Phase 0 result:

- 78 passed;
- 9 failed;
- 3 stale version assertions;
- 5 tests constructing York-direct transport from the relay-only example;
- 1 invalid empty-string password assertion.

## Repairs

1. Updated the three historical version assertions to the canonical
   `1.0.0-alpha.20` baseline.
2. Gave direct-transport tests explicit, enabled test configuration using
   reserved documentation addresses and a fabricated locally administered MAC.
3. Replaced the impossible empty-password containment assertion with a
   non-empty sentinel-secret regression check.
4. Updated the captured-frame test to use an approved 21-byte qualified fixture
   because the reconciled decoder correctly rejects incomplete four-byte
   placeholders.
5. Preserved the polished healthcheck contract: local PID/heartbeat liveness
   plus conditional relay-path validation.
6. Restored the selectable transport metadata used by release verification.
7. Reconciled the report-directory package contract so Compose mounts the
   tracked `qualification-reports` directory at `/reports`.
8. Added a release verifier aligned with the organized `tests/` tree, generated
   dashboard exclusions, and the canonical `VERSION` file.
9. Added `pytest-of-*/` to generated-test-output exclusions.

## Gate 5 evidence

- Complete collected suite: 109 tests.
- Complete result: 109 passed.
- Original polished repository baseline: 18 passed.
- Alpha.20 test modules represented: 29 of 29.
- Reconciliation gate test modules retained: 4.
- Skips: 0.
- Xfails: 0.
- Release verification: passed.
- YAML parse: passed.
- Python compilation: passed.
- Private York fixture scan: passed.
- Git whitespace check: passed.

No test was removed, skipped, marked xfail, hidden behind timing inflation, or
weakened with a broad mock to obtain the green result. The only network mock is
the socket constructor in the explicit connection-lifecycle unit test; it
verifies the exact reserved endpoint and close behavior without transmitting.
