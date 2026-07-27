# Sprint 2.6.1 — Integrated Qualification

Climate Bridge alpha.13 integrates the recovered York decoder fixtures into the existing live qualification suite.

The standard command now runs:

- seven live bridge checks; and
- one offline York decoder fixture check covering 14 recovered frames.

Expected summary on a healthy installation:

```text
RESULT: PASS (8/8 checks passed)
```

The Docker image also includes `york_decoder_qualification.py` as a standalone diagnostic entry point so both commands are valid.
