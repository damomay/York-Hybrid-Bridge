from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import yaml


class ConfigError(ValueError):
    """Compatibility error type retained for repository callers and tests."""


@dataclass(frozen=True)
class Config:
    transport_type: str
    poll_seconds: float
    transport_offline_after_failures: int
    direct_host: str
    direct_mac: str
    direct_port: int
    direct_connect_timeout: float
    direct_state_request_hex: str
    direct_read_enabled: bool
    direct_read_poll_seconds: float
    direct_control_enabled: bool
    direct_power_control_enabled: bool
    direct_control_post_write_delay_seconds: float
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
    debug_probe_on_startup: bool
    debug_probe_interval_seconds: float
    debug_capture_directory: str

    @property
    def relay_offline_after_failures(self) -> int:
        """Compatibility alias retained for historical health tests."""
        return self.transport_offline_after_failures

    @property
    def direct_enabled(self) -> bool:
        """Compatibility alias for the historical direct-device switch."""
        return self.direct_read_enabled


def load_config(path: Path) -> Config:
    raw = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    if not isinstance(raw, dict):
        raise ConfigError("configuration root must be a YAML mapping")
    transport = raw.get("transport") or raw.get("relay") or {}
    mqtt_cfg = raw["mqtt"]
    device = raw["device"]
    logging_cfg = raw.get("logging", {})
    if isinstance(logging_cfg, dict) and "direct_read" in logging_cfg:
        raise ConfigError(
            "direct_read is nested under logging; align direct_read with logging "
            "at the top level"
        )
    debug_cfg = raw.get("debug", {})

    direct_cfg = raw.get("direct_read") or raw.get("direct_device") or {}
    if not isinstance(direct_cfg, dict):
        raise ConfigError("direct_read must be a YAML mapping")
    direct_control_cfg = raw.get("direct_control") or {}
    if not isinstance(direct_control_cfg, dict):
        raise ConfigError("direct_control must be a YAML mapping")

    return Config(
        transport_type=str(transport.get("type", "native")),
        poll_seconds=float(transport.get("poll_seconds", 5)),
        transport_offline_after_failures=max(1, int(transport.get("offline_after_failures", 3))),
        direct_host=str(direct_cfg.get("host", "")).strip(),
        direct_mac=str(direct_cfg.get("mac", "")).strip().lower(),
        direct_port=int(direct_cfg.get("port", 80)),
        direct_connect_timeout=max(
            0.5, min(5.0, float(direct_cfg.get("timeout_seconds", direct_cfg.get("connect_timeout_seconds", 3))))
        ),
        direct_state_request_hex=str(direct_cfg.get("state_request_hex", "")).strip(),
        direct_read_enabled=bool(direct_cfg.get("enabled", False)),
        direct_read_poll_seconds=max(10.0, float(direct_cfg.get("poll_seconds", 30))),
        direct_control_enabled=bool(direct_control_cfg.get("enabled", False)),
        direct_power_control_enabled=bool(
            direct_control_cfg.get("power_enabled", False)
        ),
        direct_control_post_write_delay_seconds=max(
            0.0,
            min(
                10.0,
                float(direct_control_cfg.get("post_write_delay_seconds", 2)),
            ),
        ),
        mqtt_host=str(mqtt_cfg["host"]),
        mqtt_port=int(mqtt_cfg.get("port", 1883)),
        mqtt_username=str(mqtt_cfg.get("username", "")),
        mqtt_password=str(mqtt_cfg.get("password", "")),
        base_topic=str(mqtt_cfg.get("base_topic", "york/ac2")).rstrip("/"),
        discovery_prefix=str(mqtt_cfg.get("discovery_prefix", "homeassistant")).rstrip("/"),
        client_id=str(mqtt_cfg.get("client_id", "climate-bridge-york-ac2")),
        discovery_refresh_seconds=float(mqtt_cfg.get("discovery_refresh_seconds", 300)),
        reconnect_min_seconds=max(1, int(mqtt_cfg.get("reconnect_min_seconds", 1))),
        reconnect_max_seconds=max(2, int(mqtt_cfg.get("reconnect_max_seconds", 60))),
        startup_connect_timeout_seconds=max(5.0, float(mqtt_cfg.get("startup_connect_timeout_seconds", 30))),
        device_name=str(device.get("name", "York AC2")),
        unique_id=str(device.get("unique_id", "york_ac2")),
        bridge_name=str(device.get("bridge_name", "Climate Bridge")),
        bridge_unique_id=str(device.get("bridge_unique_id", f"{device.get('unique_id', 'york_ac2')}_bridge")),
        log_level=str(logging_cfg.get("level", "INFO")).upper(),
        debug_enabled=bool(debug_cfg.get("enabled", False)),
        debug_native_compare=bool(debug_cfg.get("native_compare", False)),
        debug_publish_raw_frames=bool(debug_cfg.get("publish_raw_frames", False)),
        debug_probe_on_startup=bool(debug_cfg.get("probe_on_startup", False)),
        debug_probe_interval_seconds=max(5.0, float(debug_cfg.get("probe_interval_seconds", 60))),
        debug_capture_directory=str(debug_cfg.get("capture_directory", "/reports/native-probes")),
    )
