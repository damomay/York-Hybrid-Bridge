from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml


class ConfigError(ValueError):
    """Raised when the bridge configuration is missing or invalid."""


@dataclass(frozen=True)
class Config:
    transport_type: str
    transport_url: str
    transport_timeout: float
    poll_seconds: float
    command_retries: int
    retry_delay_seconds: float
    transport_offline_after_failures: int

    direct_enabled: bool
    direct_host: str
    direct_mac: str
    direct_port: int
    direct_connect_timeout: float
    direct_state_request_hex: str

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
    debug_enabled: bool
    debug_native_compare: bool
    debug_publish_raw_frames: bool
    debug_relay_extraction: bool
    debug_probe_on_startup: bool
    debug_probe_interval_seconds: float
    debug_capture_directory: str

    @property
    def relay_url(self) -> str:
        """Legacy alias retained for the proven tablet-relay path."""
        return self.transport_url

    @property
    def relay_timeout(self) -> float:
        """Legacy alias retained for existing runtime and tools."""
        return self.transport_timeout

    @property
    def relay_offline_after_failures(self) -> int:
        """Legacy alias retained for existing health calculations."""
        return self.transport_offline_after_failures


def _required_section(raw: dict[str, Any], name: str) -> dict[str, Any]:
    """Return a required configuration section with a clear error message."""
    section = raw.get(name)
    if not isinstance(section, dict):
        raise ConfigError(
            f"Missing or invalid '{name}' section in the configuration file."
        )
    return section


def _optional_section(raw: dict[str, Any], name: str) -> dict[str, Any]:
    """Return an optional mapping without accepting malformed values."""
    section = raw.get(name, {})
    if not isinstance(section, dict):
        raise ConfigError(f"The '{name}' section must be a YAML mapping.")
    return section


def load_config(path: Path) -> Config:
    """Load bridge configuration while preserving the validated legacy path."""
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
    transport = raw.get("transport")
    if transport is None:
        transport = raw.get("relay")
    if not isinstance(transport, dict):
        raise ConfigError(
            "Missing or invalid 'transport' section "
            "(legacy 'relay' is also accepted)."
        )

    mqtt_cfg = _required_section(raw, "mqtt")
    device = _required_section(raw, "device")
    logging_cfg = _optional_section(raw, "logging")
    direct_cfg = _optional_section(raw, "direct_device")
    debug_cfg = _optional_section(raw, "debug")

    try:
        transport_type = str(transport.get("type", "relay")).strip().lower()
        transport_url = str(transport.get("base_url", "")).strip().rstrip("/")
        mqtt_host = str(mqtt_cfg["host"]).strip()
    except KeyError as exc:
        raise ConfigError(
            f"Missing required configuration value: {exc.args[0]}"
        ) from exc

    if transport_type not in {"relay", "tablet_relay", "york", "york_direct"}:
        raise ConfigError(f"Unsupported transport type: {transport_type}")
    if transport_type in {"relay", "tablet_relay"} and not transport_url:
        raise ConfigError("'transport.base_url' must not be empty for relay mode.")
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
            transport_type=transport_type,
            transport_url=transport_url,
            transport_timeout=max(
                0.1,
                float(transport.get("timeout_seconds", 10)),
            ),
            poll_seconds=max(0.1, float(transport.get("poll_seconds", 5))),
            command_retries=max(
                0,
                int(transport.get("command_retries", 2)),
            ),
            retry_delay_seconds=max(
                0.0,
                float(transport.get("retry_delay_seconds", 1)),
            ),
            transport_offline_after_failures=max(
                1,
                int(transport.get("offline_after_failures", 3)),
            ),
            direct_enabled=bool(direct_cfg.get("enabled", False)),
            direct_host=str(direct_cfg.get("host", "")).strip(),
            direct_mac=str(direct_cfg.get("mac", "")).strip().lower(),
            direct_port=int(direct_cfg.get("port", 16384)),
            direct_connect_timeout=max(
                0.5,
                float(direct_cfg.get("connect_timeout_seconds", 3)),
            ),
            direct_state_request_hex=str(
                direct_cfg.get("state_request_hex", "")
            ).strip(),
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
            debug_enabled=bool(debug_cfg.get("enabled", False)),
            debug_native_compare=bool(debug_cfg.get("native_compare", False)),
            debug_publish_raw_frames=bool(
                debug_cfg.get("publish_raw_frames", False)
            ),
            debug_relay_extraction=bool(
                debug_cfg.get("relay_extraction", False)
            ),
            debug_probe_on_startup=bool(
                debug_cfg.get("probe_on_startup", False)
            ),
            debug_probe_interval_seconds=max(
                5.0,
                float(debug_cfg.get("probe_interval_seconds", 60)),
            ),
            debug_capture_directory=str(
                debug_cfg.get("capture_directory", "/reports/native-probes")
            ).strip(),
        )
    except (TypeError, ValueError) as exc:
        raise ConfigError(f"Invalid configuration value: {exc}") from exc
