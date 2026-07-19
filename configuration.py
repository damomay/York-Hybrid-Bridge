from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import yaml


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


def load_config(path: Path) -> Config:
    raw = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    relay = raw["relay"]
    mqtt_cfg = raw["mqtt"]
    device = raw["device"]
    logging_cfg = raw.get("logging", {})

    return Config(
        relay_url=str(relay["base_url"]).rstrip("/"),
        relay_timeout=float(relay.get("timeout_seconds", 10)),
        poll_seconds=float(relay.get("poll_seconds", 5)),
        command_retries=int(relay.get("command_retries", 2)),
        retry_delay_seconds=float(relay.get("retry_delay_seconds", 1)),
        relay_offline_after_failures=max(1, int(relay.get("offline_after_failures", 3))),
        mqtt_host=str(mqtt_cfg["host"]),
        mqtt_port=int(mqtt_cfg.get("port", 1883)),
        mqtt_username=str(mqtt_cfg.get("username", "")),
        mqtt_password=str(mqtt_cfg.get("password", "")),
        base_topic=str(mqtt_cfg.get("base_topic", "york/ac2")).rstrip("/"),
        discovery_prefix=str(mqtt_cfg.get("discovery_prefix", "homeassistant")).rstrip("/"),
        client_id=str(mqtt_cfg.get("client_id", "york-ac2-hybrid-bridge")),
        discovery_refresh_seconds=float(mqtt_cfg.get("discovery_refresh_seconds", 300)),
        reconnect_min_seconds=max(1, int(mqtt_cfg.get("reconnect_min_seconds", 1))),
        reconnect_max_seconds=max(2, int(mqtt_cfg.get("reconnect_max_seconds", 60))),
        startup_connect_timeout_seconds=max(5.0, float(mqtt_cfg.get("startup_connect_timeout_seconds", 30))),
        device_name=str(device.get("name", "York AC2")),
        unique_id=str(device.get("unique_id", "york_ac2")),
        bridge_name=str(device.get("bridge_name", "York Hybrid Bridge")),
        bridge_unique_id=str(device.get("bridge_unique_id", f"{device.get('unique_id', 'york_ac2')}_bridge")),
        log_level=str(logging_cfg.get("level", "INFO")).upper(),
    )
