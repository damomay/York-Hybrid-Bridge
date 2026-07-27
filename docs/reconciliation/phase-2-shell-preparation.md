# Phase 2 — Clean repository shell

Status: PASS candidate
Branch: `feature/climate-bridge-reconciliation`
Baseline: `741145f1a2de81f1f338eccf7f2d4af6595510fd`

## Bounded change

- Preserved the repository licence, security policy, contribution guide,
  screenshots, GitHub templates, test workflow, and release workflow.
- Extended `.gitignore` for caches, compiled files, pip debris, logs, packet
  captures, local configuration, secrets, runtime reports, and generated York
  protocol-lab output.
- Added `.dockerignore` with equivalent packaging exclusions.
- Created only manifest-approved directory scaffolding for adapters, transport,
  protocol tooling, historical notes, qualification output, and reconciliation
  evidence.
- Added no alpha.20 runtime, test, fixture, capture, or generated report.

## Checks

| Check | Result |
|---|---|
| Reconciliation branch compared with `Develop` before the change | Identical at the recorded baseline |
| `main` compared with the recorded Phase 0 SHA | Identical; `main` unchanged |
| Professional shell presence | PASS |
| Ignored-file probes | PASS: 21 debris paths ignored |
| Approved-file probes | PASS: 8 paths remain eligible for tracking |
| GitHub workflow YAML parsing | PASS: test workflow 1 job; release workflow 2 jobs |
| `.dockerignore` structural check | PASS: unique, non-empty patterns |
| Existing repository test baseline | PASS: 18 passed |
| Whitespace/error check | PASS: `git diff --check` |

The first test attempt did not execute because the disposable Phase 0 virtual
environment had a broken Python symlink. A fresh isolated Python 3.12
environment was created from `requirements.txt` plus `pytest`; the unchanged
18-test baseline then passed. This was an environment repair only.

## Gate decision

Gate 2 may pass after this shell-only change is committed and the remote branch
is verified at that exact commit. If verification fails, revert only this
commit and do not begin Phase 3.
