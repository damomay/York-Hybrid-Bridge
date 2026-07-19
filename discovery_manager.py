from __future__ import annotations

import json
import logging
import threading
import time
from typing import Any, Callable

from configuration import Config


LOG = logging.getLogger("york_bridge.discovery")
PublishFn = Callable[[str, Any, bool], bool]
MIN_DISCOVERY_PUBLISH_GAP_SECONDS = 1.0


class DiscoveryManager:
    """Publish and maintain Home Assistant MQTT Discovery entities."""

    def __init__(self, config: Config, app_version: str, publish_fn: PublishFn) -> None:
        self.config = config
        self.app_version = app_version
        self.publish_fn = publish_fn
        self.last_publish_monotonic = 0.0
        self._publish_lock = threading.Lock()
        self._minimum_publish_gap_seconds = MIN_DISCOVERY_PUBLISH_GAP_SECONDS

    def bridge_device_payload(self) -> dict[str, Any]:
        return {
            "identifiers": [self.config.bridge_unique_id],
            "name": self.config.bridge_name,
            "manufacturer": "York Hybrid Bridge",
            "model": "Tablet Relay Edition",
            "sw_version": self.app_version,
        }

    def ac_device_payload(self) -> dict[str, Any]:
        return {
            "identifiers": [self.config.unique_id],
            "name": self.config.device_name,
            "manufacturer": "York / TCL",
            "model": "YHKE12XEAATA-RX / TFIAC type 20014",
            "sw_version": self.app_version,
            "via_device": self.config.bridge_unique_id,
        }

    def due(self) -> bool:
        return (
            time.monotonic() - self.last_publish_monotonic
            >= self.config.discovery_refresh_seconds
        )

    def _publish_config(self, topic: str, payload: dict[str, Any]) -> bool:
        """Publish a deterministic retained Home Assistant discovery payload."""
        return self.publish_fn(
            topic,
            json.dumps(payload, sort_keys=True),
            True,
        )

    def publish_all(self, *, force: bool = False) -> bool:
        with self._publish_lock:
            now = time.monotonic()
            if (
                not force
                and now - self.last_publish_monotonic
                < self._minimum_publish_gap_seconds
            ):
                LOG.debug("Skipping duplicate MQTT discovery publish")
                return False
            LOG.info("Publishing Home Assistant MQTT discovery")
            self.last_publish_monotonic = now

        cfg = self.config
        ac_device = self.ac_device_payload()
        bridge_device = self.bridge_device_payload()
        published_count = 0

        climate = {
            "name": cfg.device_name,
            "unique_id": f"{cfg.unique_id}_climate",
            "availability_topic": f"{cfg.base_topic}/availability",
            "mode_command_topic": f"{cfg.base_topic}/mode/set",
            "mode_state_topic": f"{cfg.base_topic}/mode/state",
            "modes": ["off", "cool", "heat", "dry", "fan_only", "auto"],
            "temperature_command_topic": f"{cfg.base_topic}/temperature/set",
            "temperature_state_topic": f"{cfg.base_topic}/temperature/state",
            "current_temperature_topic": f"{cfg.base_topic}/current_temperature/state",
            "min_temp": 16,
            "max_temp": 31,
            "temp_step": 0.5,
            "fan_mode_command_topic": f"{cfg.base_topic}/fan/set",
            "fan_mode_state_topic": f"{cfg.base_topic}/fan/state",
            "fan_modes": ["auto", "low", "medium", "high"],
            "swing_mode_command_topic": f"{cfg.base_topic}/swing/set",
            "swing_mode_state_topic": f"{cfg.base_topic}/swing/state",
            "swing_modes": ["off", "vertical", "horizontal", "both"],
            "payload_available": "online",
            "payload_not_available": "offline",
            "device": ac_device,
        }
        self._publish_config(
            f"{cfg.discovery_prefix}/climate/{cfg.unique_id}/config",
            climate,
        )
        published_count += 1

        for key, label in {
            "turbo": "Turbo",
            "eco": "Eco",
            "health": "Health",
            "display": "Display",
            "sleep": "Sleep",
        }.items():
            payload = {
                "name": label,
                "unique_id": f"{cfg.unique_id}_{key}",
                "availability_topic": f"{cfg.base_topic}/availability",
                "command_topic": f"{cfg.base_topic}/{key}/set",
                "state_topic": f"{cfg.base_topic}/{key}/state",
                "payload_on": "ON",
                "payload_off": "OFF",
                "state_on": "ON",
                "state_off": "OFF",
                "device": ac_device,
            }
            self._publish_config(
                f"{cfg.discovery_prefix}/switch/{cfg.unique_id}_{key}/config",
                payload,
            )
            published_count += 1

        # AC activity sensors provide meaningful timeline entries for climate
        # attributes that Home Assistant otherwise stores only as attributes.
        ac_activity: dict[str, dict[str, Any]] = {
            "power_state": {"name": "Power state", "icon": "mdi:power"},
            "target_temperature": {
                "name": "Target temperature",
                "device_class": "temperature",
                "unit_of_measurement": "°C",
                "state_class": "measurement",
                "icon": "mdi:thermometer",
            },
            "operating_mode": {
                "name": "Operating mode",
                "icon": "mdi:air-conditioner",
            },
            "fan_mode": {"name": "Fan mode", "icon": "mdi:fan"},
            "swing_mode": {
                "name": "Swing mode",
                "icon": "mdi:swap-vertical",
            },
            "last_event": {
                "name": "Last AC event",
                "icon": "mdi:timeline-clock-outline",
            },
        }
        for key, extra in ac_activity.items():
            payload = {
                "name": extra["name"],
                "unique_id": f"{cfg.unique_id}_activity_{key}",
                "state_topic": f"{cfg.base_topic}/activity/{key}",
                "availability_topic": f"{cfg.base_topic}/availability",
                "device": ac_device,
            }
            payload.update({k: v for k, v in extra.items() if k != "name"})
            self._publish_config(
                f"{cfg.discovery_prefix}/sensor/{cfg.unique_id}_activity_{key}/config",
                payload,
            )
            published_count += 1

        # Keep a precise state-change timestamp available for advanced
        # diagnostics, but disable it by default so routine timestamp changes do
        # not clutter the York AC2 Activity timeline. The meaningful activity
        # sensors above remain enabled.
        self.publish_fn(
            f"{cfg.discovery_prefix}/sensor/{cfg.unique_id}_last_state_update/config",
            "",
            True,
        )
        ac_diagnostics: dict[str, dict[str, Any]] = {
            "last_state_change_timestamp": {
                "name": "Last state change timestamp",
                "device_class": "timestamp",
                "icon": "mdi:clock-check-outline",
                "enabled_by_default": False,
            },
        }

        bridge_diagnostics: dict[str, dict[str, Any]] = {
            "last_command": {"name": "Last command"},
            "last_command_result": {"name": "Last command result"},
            "last_command_duration": {
                "name": "Last command duration",
                "unit_of_measurement": "ms",
            },
            "last_transaction_id": {"name": "Last transaction ID"},
            "bridge_version": {
                "name": "Software version",
                "icon": "mdi:information-outline",
            },
            "bridge_status": {"name": "Bridge status", "icon": "mdi:bridge"},
            "health_status": {
                "name": "Overall health",
                "icon": "mdi:shield-heart",
            },
            "health_score": {
                "name": "Health score",
                "unit_of_measurement": "%",
                "state_class": "measurement",
                "icon": "mdi:gauge",
            },
            "health_reason": {
                "name": "Health reason",
                "icon": "mdi:text-box-check-outline",
            },
            "bridge_summary": {
                "name": "Bridge summary",
                "icon": "mdi:text-box-check",
            },
            "health_advisor": {
                "name": "Health advisor",
                "icon": "mdi:lightbulb-on",
            },
            "stability_score": {
                "name": "Bridge stability score",
                "unit_of_measurement": "%",
                "state_class": "measurement",
                "icon": "mdi:chart-line-variant",
            },
            "stability_status": {
                "name": "Stability rating",
                "icon": "mdi:shield-check-outline",
            },
            "stability_trend": {
                "name": "Stability trend",
                "icon": "mdi:trending-up",
            },
            "mqtt_status": {"name": "MQTT status", "icon": "mdi:lan-connect"},
            "transport_type": {
                "name": "Transport type",
                "icon": "mdi:transit-connection-variant",
            },
            "relay_status": {
                "name": "Tablet relay status",
                "icon": "mdi:tablet-dashboard",
            },
            "bridge_uptime": {
                "name": "Uptime seconds",
                "unit_of_measurement": "s",
                "device_class": "duration",
                "state_class": "total_increasing",
                "icon": "mdi:timer-outline",
            },
            "bridge_uptime_text": {
                "name": "Bridge uptime",
                "icon": "mdi:clock-outline",
            },
            "poll_count": {
                "name": "State polls",
                "state_class": "total_increasing",
                "icon": "mdi:counter",
            },
            "poll_errors": {
                "name": "Poll errors",
                "state_class": "total_increasing",
                "icon": "mdi:alert-circle-outline",
            },
            "poll_success_rate": {
                "name": "Poll success rate",
                "unit_of_measurement": "%",
                "state_class": "measurement",
                "icon": "mdi:check-decagram-outline",
            },
            "last_poll_time": {
                "name": "Current poll time",
                "unit_of_measurement": "ms",
                "state_class": "measurement",
                "icon": "mdi:timer-sand",
            },
            "average_poll_time": {
                "name": "Average poll time",
                "unit_of_measurement": "ms",
                "state_class": "measurement",
                "icon": "mdi:timer-outline",
            },
            "fastest_poll_time": {
                "name": "Fastest poll time",
                "unit_of_measurement": "ms",
                "state_class": "measurement",
                "icon": "mdi:speedometer",
            },
            "slowest_poll_time": {
                "name": "Slowest poll time",
                "unit_of_measurement": "ms",
                "state_class": "measurement",
                "icon": "mdi:timer-alert-outline",
            },
            "command_count": {
                "name": "Commands sent",
                "state_class": "total_increasing",
                "icon": "mdi:counter",
            },
            "command_failures": {
                "name": "Command failures",
                "state_class": "total_increasing",
                "icon": "mdi:alert-circle-outline",
            },
            "command_deferred": {
                "name": "Commands deferred",
                "state_class": "total_increasing",
                "icon": "mdi:clock-arrow-right-outline",
            },
            "command_not_applicable": {
                "name": "Commands not applicable",
                "state_class": "total_increasing",
                "icon": "mdi:minus-circle-outline",
            },
            "command_success_rate": {
                "name": "Command success rate",
                "unit_of_measurement": "%",
                "state_class": "measurement",
                "icon": "mdi:check-decagram",
            },
            "average_command_time": {
                "name": "Average command time",
                "unit_of_measurement": "ms",
                "state_class": "measurement",
                "icon": "mdi:timer-check-outline",
            },
            "fastest_command_time": {
                "name": "Fastest command time",
                "unit_of_measurement": "ms",
                "state_class": "measurement",
                "icon": "mdi:speedometer",
            },
            "slowest_command_time": {
                "name": "Slowest command time",
                "unit_of_measurement": "ms",
                "state_class": "measurement",
                "icon": "mdi:timer-alert-outline",
            },
            "mqtt_reconnects": {
                "name": "MQTT reconnects",
                "state_class": "total_increasing",
                "icon": "mdi:lan-connect",
            },
            "recovery_count": {
                "name": "Recoveries",
                "state_class": "total_increasing",
                "icon": "mdi:auto-fix",
            },
            "recovery_failures": {
                "name": "Recovery failures",
                "state_class": "total_increasing",
                "icon": "mdi:alert-circle-outline",
            },
            "recovery_success_rate": {
                "name": "Recovery success rate",
                "unit_of_measurement": "%",
                "state_class": "measurement",
                "icon": "mdi:check-decagram",
            },
            "last_recovery": {"name": "Last recovery", "icon": "mdi:history"},
            "last_recovery_age": {
                "name": "Last recovery age",
                "icon": "mdi:clock-check-outline",
            },
            "recovery_reason": {
                "name": "Recovery reason",
                "icon": "mdi:information-outline",
            },
            "last_recovery_duration": {
                "name": "Last recovery duration",
                "unit_of_measurement": "ms",
                "state_class": "measurement",
                "icon": "mdi:timer-refresh-outline",
            },
            "average_recovery_time": {
                "name": "Average recovery time",
                "unit_of_measurement": "ms",
                "state_class": "measurement",
                "icon": "mdi:timer-sync-outline",
            },
            "longest_recovery_time": {
                "name": "Longest recovery time",
                "unit_of_measurement": "ms",
                "state_class": "measurement",
                "icon": "mdi:timer-alert-outline",
            },
            "last_event": {
                "name": "Latest bridge event",
                "icon": "mdi:timeline-clock-outline",
            },
            "event_level": {
                "name": "Latest event level",
                "icon": "mdi:label-outline",
            },
            "event_message": {
                "name": "Latest event message",
                "icon": "mdi:message-text-clock-outline",
            },
            "protocol_name": {"name": "Protocol", "icon": "mdi:connection"},
            "discovery_status": {
                "name": "Home Assistant discovery",
                "icon": "mdi:home-assistant",
            },
            "last_error": {"name": "Last error", "icon": "mdi:alert-outline"},
        }

        # RC3.2 replaces session-wide reliability entities with rolling stability.
        for legacy_key in ("reliability_score", "reliability_status"):
            self.publish_fn(
                f"{cfg.discovery_prefix}/sensor/{cfg.bridge_unique_id}_{legacy_key}/config",
                "",
                True,
            )

        published_count += self._publish_diagnostic_entities(
            ac_diagnostics,
            ac_device,
            owner_unique_id=cfg.unique_id,
            bridge_owned=False,
        )
        published_count += self._publish_diagnostic_entities(
            bridge_diagnostics,
            bridge_device,
            owner_unique_id=cfg.bridge_unique_id,
            bridge_owned=True,
        )
        LOG.info(
            "Published %s Home Assistant discovery entities",
            published_count,
        )
        return True

    def _publish_diagnostic_entities(
        self,
        entities: dict[str, dict[str, Any]],
        device: dict[str, Any],
        *,
        owner_unique_id: str,
        bridge_owned: bool,
    ) -> int:
        cfg = self.config
        published_count = 0

        for key, extra in entities.items():
            # Identity.1 originally published bridge sensors with AC-owned unique IDs.
            # Clear those retained discovery records before creating the corrected
            # bridge-owned entities so Home Assistant migrates them cleanly.
            if bridge_owned:
                legacy_topic = (
                    f"{cfg.discovery_prefix}/sensor/{cfg.unique_id}_{key}/config"
                )
                self.publish_fn(legacy_topic, "", True)

            payload = {
                "name": extra["name"],
                "unique_id": f"{owner_unique_id}_{key}",
                "state_topic": f"{cfg.base_topic}/diagnostic/{key}",
                "availability_topic": (
                    f"{cfg.base_topic}/bridge/availability"
                    if bridge_owned
                    else f"{cfg.base_topic}/availability"
                ),
                "entity_category": "diagnostic",
                "device": device,
            }
            payload.update({k: v for k, v in extra.items() if k != "name"})
            self._publish_config(
                f"{cfg.discovery_prefix}/sensor/{owner_unique_id}_{key}/config",
                payload,
            )
            published_count += 1

        return published_count
