from __future__ import annotations

from dataclasses import replace
import logging
from pathlib import Path
from unittest.mock import Mock, patch

from bridge import ClimateBridge, log_startup_banner
from configuration import load_config
from direct_read_manager import DirectReadResult
from health_manager import HealthManager
from recovery_manager import friendly_reason


DIRECT_STATE = {
    "power": True,
    "mode": "heat",
    "temperature": 21.5,
    "indoor_temperature": 23.0,
    "fan": "low",
    "swing": "off",
    "turbo": False,
    "eco": False,
    "health": False,
    "display": True,
}


class StoppedRelay:
    name = "tablet_relay"
    display_name = "Relay (Legacy)"

    def __init__(self) -> None:
        self.state_calls = 0
        self.command_calls = 0

    def get_state(self):
        self.state_calls += 1
        raise AssertionError("tablet state must not be read")

    def command(self, **_changes):
        self.command_calls += 1
        raise ConnectionRefusedError("Relay v2 is stopped")

    def close(self) -> None:
        return None


class DirectReader:
    def __init__(self) -> None:
        self.calls = 0

    def read_authoritative(self) -> DirectReadResult:
        self.calls += 1
        return DirectReadResult(
            state=dict(DIRECT_STATE),
            comparison="authoritative (9 decoded fields)",
            matched_fields=9,
            compared_fields=9,
            response_length=21,
            udp_sends=2,
            raw_frame_hex="BB00",
            fan_status_byte=0x30,
            fan_status_nibble=3,
        )

    def close(self) -> None:
        return None


def make_bridge():
    config = replace(
        load_config(Path("config.example.yml")),
        direct_read_enabled=True,
        transport_offline_after_failures=3,
    )
    relay = StoppedRelay()
    reader = DirectReader()
    with (
        patch("bridge.create_transport", return_value=relay),
        patch("bridge.DirectReadManager", return_value=reader),
        patch("bridge.MqttManager"),
    ):
        climate = ClimateBridge(config)
    climate.mqtt.connected = True
    climate.mqtt.publish = Mock(return_value=True)
    return climate, reader, relay


def test_mqtt_startup_keeps_ac_offline_until_fresh_direct_read(tmp_path):
    climate, reader, relay = make_bridge()
    with patch("bridge.READY_FILE", tmp_path / "ready"):
        climate.on_mqtt_connected(reconnect=False)

    climate.mqtt.publish.assert_any_call(
        f"{climate.config.base_topic}/bridge/availability", "online", retain=True
    )
    climate.mqtt.publish.assert_any_call(
        f"{climate.config.base_topic}/availability", "offline", retain=True
    )
    assert climate.authoritative_state_confirmed is False
    assert reader.calls == 0
    assert relay.state_calls == 0
    assert relay.command_calls == 0


def test_first_direct_poll_restores_ac_availability_without_relay():
    climate, reader, relay = make_bridge()

    climate.poll_once()

    climate.mqtt.publish.assert_any_call(
        f"{climate.config.base_topic}/availability", "online", retain=True
    )
    assert climate.authoritative_state_confirmed is True
    assert climate.last_state == DIRECT_STATE
    assert reader.calls == 1
    assert relay.state_calls == 0


def test_repeated_direct_failures_mark_only_ac_entity_unavailable():
    climate, _reader, relay = make_bridge()

    for _ in range(3):
        climate._handle_poll_failure(TimeoutError("York module unavailable"))

    climate.mqtt.publish.assert_any_call(
        f"{climate.config.base_topic}/availability", "offline", retain=True
    )
    assert climate.authoritative_state_confirmed is False
    assert climate.diagnostics.bridge_status == "error"
    assert climate.recovery.failure_count == 1
    assert relay.state_calls == 0


def test_direct_poll_recovers_after_failure_without_relay():
    climate, reader, relay = make_bridge()
    climate._handle_poll_failure(TimeoutError("York module unavailable"))

    climate.poll_once()

    assert climate.consecutive_poll_failures == 0
    assert climate.authoritative_state_confirmed is True
    assert climate.recovery.active is False
    assert climate.recovery.recovery_count == 1
    assert reader.calls == 1
    assert relay.state_calls == 0


def test_mqtt_reconnect_requires_new_direct_validation(tmp_path):
    climate, reader, relay = make_bridge()
    climate.ready = True
    climate.authoritative_state_confirmed = True
    climate.on_mqtt_disconnected("network interrupted")
    climate.mqtt.connected = True

    with patch("bridge.READY_FILE", tmp_path / "ready"):
        climate.on_mqtt_connected(reconnect=True)

    assert climate.authoritative_state_confirmed is False
    climate.mqtt.publish.assert_any_call(
        f"{climate.config.base_topic}/availability", "offline", retain=True
    )
    climate.poll_once()
    assert climate.authoritative_state_confirmed is True
    assert climate.recovery.active is False
    assert climate.recovery.recovery_count == 1
    assert reader.calls == 1
    assert relay.state_calls == 0


def test_direct_health_diagnostics_do_not_call_failure_a_relay_problem():
    result = HealthManager().evaluate(
        mqtt_connected=True,
        consecutive_poll_failures=3,
        relay_offline_after_failures=3,
        average_command_time_ms=0,
        bridge_status="error",
        state_source_label="Direct LAN state source",
    )

    assert result.status == "critical"
    assert result.reason == "Direct LAN state source is unavailable"
    assert "Relay" not in result.reason


def test_direct_recovery_reason_is_not_described_as_tablet_polling():
    reason = friendly_reason(
        "Direct LAN state read: TimeoutError: York module unavailable"
    )

    assert reason.startswith("Direct LAN state read was interrupted")
    assert "tablet" not in reason.lower()


def test_startup_banner_describes_native_state_path(caplog):
    config = replace(
        load_config(Path("config.example.yml")), direct_read_enabled=True
    )

    with caplog.at_level(logging.INFO, logger="climate_bridge"):
        log_startup_banner(config, "Relay (Legacy)")

    text = caplog.text
    assert "Transport    : Native LAN (no Relay runtime)" in text
    assert "State Source : authenticated direct LAN read" in text
