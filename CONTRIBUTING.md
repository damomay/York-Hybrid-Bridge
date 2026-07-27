# Contributing to Climate Bridge

First of all, thank you for considering contributing to Climate Bridge.

This project provides a reliable bridge between supported York systems and
Home Assistant while carefully developing a broader architecture. The Android
relay is the only verified working transport in `1.0.0-alpha.20`; native
direct control and multi-vendor operation are not completed features.

Whether you're fixing a bug, improving documentation, adding diagnostics, or implementing support for additional HVAC systems, your contribution is appreciated.

---

# Project Philosophy

Climate Bridge is built around five core principles.

## Reliability

The bridge is intended to operate continuously for months without intervention.

Reliability always takes priority over adding new features.

---

## Local Control

The project avoids unnecessary cloud dependencies wherever possible.

Users should retain complete control over their own HVAC systems.

---

## Maintainability

Code should be easy to understand, modify, and extend.

Readable code is preferred over clever code.

---

## Extensibility

The long-term vision is to evolve Climate Bridge into a vendor-independent framework supporting multiple HVAC manufacturers.

New features should be designed with future expansion in mind.

---

## Transparency

Good diagnostics are considered a feature.

The bridge should clearly report its health, status, performance, and any errors encountered.

---

# Development Workflow

Development follows a simple Git workflow.

```
main
    │
Develop
    │
feature branch
```

- `main` contains stable production releases.
- `Develop` contains the next release under development.
- Feature branches should be created from `Develop`.
- Pull Requests should target `Develop` unless the maintainer specifies a
  controlled reconciliation or urgent production path.

---

# Before You Begin

Please check for existing Issues before starting work.

If you are planning native transmission, tablet removal, multiple-device
support or an architectural change, open a discussion first. These areas have
ordered safety gates in `ROADMAP.md`.

---

# Coding Standards

The project follows standard Python best practices.

Please:

- Follow PEP 8 where practical.
- Prefer readability over clever implementations.
- Keep functions focused on a single responsibility.
- Avoid duplicated logic.
- Use descriptive variable and function names.
- Avoid unnecessary complexity.
- Add comments only where they improve understanding.
- Use type hints where appropriate.

---

# Error Handling

Climate Bridge is designed to run unattended.

Please ensure:

- Errors are handled gracefully.
- Exceptions include meaningful messages.
- Recovery is preferred over termination whenever possible.
- Logging provides sufficient information for troubleshooting.

---

# Logging

Logging should be:

- Clear
- Concise
- Consistent
- Actionable

Avoid excessive logging inside high-frequency polling loops unless required for debugging.

---

# Testing

Every change should maintain a fully passing test suite.

Before submitting a Pull Request, run:

```bash
python -m compileall -q -f .
python phase6_quality_gate.py
python release_verifier.py
python -c "from pathlib import Path; from validate_config import validate; print('Example transport:', validate(Path('config.example.yml')))"
python -m pytest
python york_decoder_qualification.py --no-write
git diff --check
```

All tests should pass.

If new functionality is introduced, corresponding tests should be added whenever practical.

Never knowingly introduce failing tests.

Do not hide a failure with a skip, xfail, timing inflation, broad mock or
weakened assertion. If the collected test count falls below the current
baseline, explain and repair the loss before requesting review.

See `docs/TESTING.md` for Docker qualification and live-test boundaries.

---

# Documentation

Documentation is considered part of the project.

Please update documentation when:

- Adding new features
- Changing configuration
- Adding diagnostics
- Modifying behaviour
- Introducing new entities
- Changing installation procedures

Documentation includes:

- README.md
- CHANGELOG.md
- Configuration examples
- Inline code documentation
- `ROADMAP.md`
- `RELEASE_NOTES.md`
- relevant files in `docs/`

---

# Commit Messages

Please keep commits small and focused.

Good examples:

```
Improve relay timeout handling

Refactor diagnostics manager

Add health summary sensor

Improve MQTT reconnect handling

Update installation documentation
```

Avoid combining unrelated changes into a single commit.

---

# Pull Requests

A good Pull Request should:

- Address a single logical change.
- Include a clear description.
- Pass all tests.
- Include documentation updates if required.
- Maintain backwards compatibility where practical.

Large Pull Requests are harder to review than several smaller ones.

---

# Feature Requests

Feature requests are welcome.

When proposing a new feature, please explain:

- The problem it solves.
- Why it benefits users.
- Any potential impact on existing functionality.

Where possible, include examples or screenshots.

---

# Bug Reports

Useful bug reports include:

- Bridge version
- Home Assistant version
- Docker version (if applicable)
- Operating system
- Configuration (with sensitive information removed)
- Relevant log output
- Steps to reproduce the issue

The more information provided, the easier the issue is to diagnose.

---

# Roadmap

The long-term direction of the project includes:

- Multi-vendor Hybrid Bridge architecture
- Additional HVAC manufacturer support
- Enhanced diagnostics
- Improved performance monitoring
- Expanded Home Assistant integration
- Improved deployment options

Contributions aligned with these goals are especially welcome.

---

# Code Review Checklist

Before submitting a Pull Request, please verify:

- [ ] Code follows the existing project style.
- [ ] Tests pass successfully.
- [ ] Documentation has been updated where required.
- [ ] Logging is appropriate.
- [ ] Error handling has been considered.
- [ ] No unnecessary dependencies have been introduced.
- [ ] Changes remain backwards compatible where practical.
- [ ] Relay JSON, native York requests and response evidence are not conflated.
- [ ] No unverified packet can become executable or transmit-safe.
- [ ] Logs, captures and configuration are sanitized.

---

# Thank You

Climate Bridge has grown from the York Hybrid Bridge protocol research project through careful engineering, testing, and continuous improvement.

Thank you for helping make the project even better.

Every contribution—whether code, documentation, testing, bug reports, or ideas—is genuinely appreciated.
