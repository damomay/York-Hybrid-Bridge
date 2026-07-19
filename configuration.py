from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml


class ConfigError(ValueError):
    """Raised when the bridge configuration is missing or invalid."""


@dataclass(frozen=True)
class Config:
    relay_url: str
    relay_timeout: float
    poll_seconds: float
    command_retries: int
    retry_delay_seconds: float
    relay_offline_after_failures: int

    mqtt_host: str
    mqtt_port: int
    mqtt_username: str
    mqtt_password: str
    base_topic: str
    discovery_prefix: str
    client_id: str
    discovery_refresh_seconds: float
    reconnect_min_seconds: int
    reconnect_max_seconds: int
    startup_connect_timeout_seconds: float

    device_name: str
    unique_id: str
    bridge_name: str
    bridge_unique_id: str

    log_level: str


def _required_section(raw: dict[str, Any], name: str) -> dict[str, Any]:
    """Return a required configuration section with a clear error message."""
    section = raw.get(name)

    if not isinstance(section, dict):
        raise ConfigError(
            f"Missing or invalid '{name}' section in the configuration file."
        )

    return section


def load_config(path: Path) -> Config:
    """Load and validate York Hybrid Bridge configuration from a YAML file."""
    if not path.is_file():
        raise ConfigError(f"Configuration file not found: {path}")

    try:
        loaded = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    except yaml.YAMLError as exc:
        raise ConfigError(f"Invalid YAML in configuration file {path}: {exc}") from exc
    except OSError as exc:
        raise ConfigError(f"Unable to read configuration file {path}: {exc}") from exc

    if not isinstance(loaded, dict):
        raise ConfigError("The configuration root must be a YAML mapping.")

    raw: dict[str, Any] = loaded
    relay = _required_section(raw, "relay")
    mqtt_cfg = _required_section(raw, "mqtt")
    device = _required_section(raw, "device")

    logging_cfg = raw.get("logging", {})
    if not isinstance(logging_cfg, dict):
        raise ConfigError("The 'logging' section must be a YAML mapping.")

    try:
        relay_url = str(relay["base_url"]).strip().rstrip("/")
        mqtt_host = str(mqtt_cfg["host"]).strip()
    except KeyError as exc:
        raise ConfigError(
            f"Missing required configuration value: {exc.args[0]}"
        ) from exc

    if not relay_url:
        raise ConfigError("'relay.base_url' must not be empty.")

    if not mqtt_host:
        raise ConfigError("'mqtt.host' must not be empty.")

    try:
        reconnect_min_seconds = max(
            1,
            int(mqtt_cfg.get("reconnect_min_seconds", 1)),
        )
        reconnect_max_seconds = max(
            reconnect_min_seconds,
            int(mqtt_cfg.get("reconnect_max_seconds", 60)),
        )

        return Config(
            relay_url=relay_url,
            relay_timeout=max(0.1, float(relay.get("timeout_seconds", 10))),
            poll_seconds=max(0.1, float(relay.get("poll_seconds", 5))),
            command_retries=max(0, int(relay.get("command_retries", 2))),
            retry_delay_seconds=max(
                0.0,
                float(relay.get("retry_delay_seconds", 1)),
            ),
            relay_offline_after_failures=max(
                1,
                int(relay.get("offline_after_failures", 3)),
            ),
            mqtt_host=mqtt_host,
            mqtt_port=int(mqtt_cfg.get("port", 1883)),
            mqtt_username=str(mqtt_cfg.get("username", "")),
            mqtt_password=str(mqtt_cfg.get("password", "")),
            base_topic=str(
                mqtt_cfg.get("base_topic", "york/ac2")
            ).strip().rstrip("/"),
            discovery_prefix=str(
                mqtt_cfg.get("discovery_prefix", "homeassistant")
            ).strip().rstrip("/"),
            client_id=str(
                mqtt_cfg.get("client_id", "york-ac2-hybrid-bridge")
            ).strip(),
            discovery_refresh_seconds=max(
                0.0,
                float(mqtt_cfg.get("discovery_refresh_seconds", 300)),
            ),
            reconnect_min_seconds=reconnect_min_seconds,
            reconnect_max_seconds=reconnect_max_seconds,
            startup_connect_timeout_seconds=max(
                5.0,
                float(mqtt_cfg.get("startup_connect_timeout_seconds", 30)),
            ),
            device_name=str(device.get("name", "York AC2")).strip(),
            unique_id=str(device.get("unique_id", "york_ac2")).strip(),
            bridge_name=str(
                device.get("bridge_name", "York Hybrid Bridge")
            ).strip(),
            bridge_unique_id=str(
                device.get(
                    "bridge_unique_id",
                    f"{device.get('unique_id', 'york_ac2')}_bridge",
                )
            ).strip(),
            log_level=str(logging_cfg.get("level", "INFO")).strip().upper(),
        )
    except (TypeError, ValueError) as exc:
        raise ConfigError(f"Invalid configuration value: {exc}") from exc