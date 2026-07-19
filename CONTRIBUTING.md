# Contributing to York Hybrid Bridge

First of all, thank you for considering contributing to York Hybrid Bridge.

This project exists to provide a reliable, maintainable, and production-ready bridge between proprietary HVAC systems and Home Assistant. Every contribution helps improve the project for the entire Home Assistant community.

Whether you're fixing a bug, improving documentation, adding diagnostics, or implementing support for additional HVAC systems, your contribution is appreciated.

---

# Project Philosophy

York Hybrid Bridge is built around five core principles.

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

The long-term vision is to evolve York Hybrid Bridge into a vendor-independent Hybrid Bridge framework supporting multiple HVAC manufacturers.

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
develop
    │
Feature Branch
```

- `main` contains stable production releases.
- `develop` contains the next release under development.
- Feature branches should be created from `develop`.
- Pull Requests should target `develop` unless fixing an urgent production issue.

---

# Before You Begin

Please check for existing Issues before starting work.

If you're planning a significant feature or architectural change, consider opening a discussion first so ideas can be reviewed before implementation begins.

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

York Hybrid Bridge is designed to run unattended.

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
pytest
```

All tests should pass.

If new functionality is introduced, corresponding tests should be added whenever practical.

Never knowingly introduce failing tests.

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

---

# Thank You

York Hybrid Bridge has grown from a protocol research project into a production-ready Home Assistant integration through careful engineering, testing, and continuous improvement.

Thank you for helping make the project even better.

Every contribution—whether code, documentation, testing, bug reports, or ideas—is genuinely appreciated.