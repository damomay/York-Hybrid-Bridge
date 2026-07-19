# Security Policy

Thank you for helping keep York Hybrid Bridge secure.

The security of users running this project in their home networks is important. If you discover a security vulnerability, please report it responsibly so it can be investigated and resolved before public disclosure.

---

# Supported Versions

The following versions currently receive security updates.

| Version | Supported |
|---------|:---------:|
| 3.x | ✅ |
| Earlier versions | ❌ |

Only the latest stable release is actively maintained.

---

# Reporting a Vulnerability

If you believe you have discovered a security vulnerability, please **do not create a public GitHub Issue**.

Instead, please contact the project maintainer privately with as much information as possible, including:

- Description of the vulnerability
- Steps to reproduce the issue
- Potential impact
- Suggested mitigation (if known)
- Relevant log files (with sensitive information removed)

Reports will be investigated as quickly as possible.

Where appropriate:

- The issue will be reproduced.
- A fix will be developed.
- A new release will be published.
- Credit may be given to the reporter (if desired).

---

# Responsible Disclosure

Please allow reasonable time for a fix to be developed before publicly disclosing security-related issues.

Responsible disclosure helps protect all users of the project.

---

# Protect Your Privacy

When reporting bugs or requesting support, **never publish sensitive information** such as:

- MQTT usernames
- MQTT passwords
- API keys
- Access tokens
- Wi-Fi passwords
- Home Assistant secrets
- Public IP addresses
- VPN configuration
- Private certificates
- Authentication credentials

If sharing configuration files or logs, remove or replace sensitive values before posting.

Example:

```yaml
mqtt:
  host: mqtt.example.local
  username: your_username
  password: ********
```

---

# Security Best Practices

For the best security when running York Hybrid Bridge:

- Keep Home Assistant up to date.
- Keep Docker and your operating system updated.
- Use strong, unique MQTT passwords.
- Restrict MQTT broker access to trusted devices.
- Avoid exposing MQTT directly to the Internet.
- Protect Home Assistant with authentication.
- Keep your local network secure.
- Regularly back up your Home Assistant configuration.

---

# Scope

York Hybrid Bridge is designed for operation within trusted local networks.

The bridge does not intentionally expose services directly to the public Internet.

Users are responsible for securing:

- Home Assistant
- MQTT broker
- Docker host
- NAS or server
- Local network
- Reverse proxies (if used)

---

# Third-Party Software

York Hybrid Bridge depends on a number of third-party components, including but not limited to:

- Python
- Docker
- Home Assistant
- Mosquitto MQTT
- Operating system packages

Security vulnerabilities affecting these projects should also be kept up to date by users.

---

# Security Updates

Security-related fixes will be documented in the project's CHANGELOG and included in the next stable release whenever practical.

Critical vulnerabilities may result in an immediate patch release outside the normal release cycle.

---

# A Shared Responsibility

Security is a shared responsibility between the project maintainer and its users.

Thoughtful reporting, responsible disclosure, and good operational practices help ensure York Hybrid Bridge remains a reliable and secure solution for the Home Assistant community.

Thank you for helping make the project better.