from __future__ import annotations

from dataclasses import replace
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from bridge import ClimateBridge, RelayFreeCommandRejected, log_startup_banner
from configuration import load_config
from direct_read_manager import DirectReadResult
from transport.factory import create_transport
from transport.native_command_boundary import NativeCommandBoundaryTransport


STATE = {
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


class DirectReader:
    def __init__(self) -> None:
        self.calls = 0

    def read_authoritative(self) -> DirectReadResult:
        self.calls += 1
        return DirectReadResult(
            state=dict(STATE),
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


def relay_free_config():
    return replace(
        load_config(Path("config.example.yml")),
        direct_read_enabled=True,
        direct_control_enabled=True,
        direct_power_control_enabled=True,
    )


def make_bridge():
    config = relay_free_config()
    reader = DirectReader()
    with (
        patch("bridge.DirectReadManager", return_value=reader),
        patch("bridge.MqttManager"),
    ):
        climate = ClimateBridge(config)
    climate.mqtt.publish = Mock(return_value=True)
    return climate, reader


def test_alpha57_config_selects_boundary_without_constructing_relay():
    config = relay_free_config()
    transport = create_transport(config)

    assert isinstance(transport, NativeCommandBoundaryTransport)
    assert transport.command_fallback_enabled is False


def test_boundary_contains_no_live_relay_endpoint_or_http_client():
    config = relay_free_config()
    transport = NativeCommandBoundaryTransport(config)

    assert not hasattr(transport, "session")
    assert not hasattr(transport, "extraction_logger")
    assert not hasattr(config, "transport_url")
    with pytest.raises(RuntimeError, match="qualified native allowlist"):
        transport.command(display=False)


def test_qualified_native_command_bypasses_boundary():
    climate, reader = make_bridge()
    native = Mock()
    native.command.return_value = {
        **STATE,
        "fan": "high",
        "_transaction": {"success": True, "source": "york_direct_fan"},
    }
    climate.direct_fan = native
    climate.transport.command = Mock(side_effect=AssertionError("boundary called"))

    response = climate.execute_command({"fan": "high"})

    assert response["fan"] == "high"
    assert reader.calls == 1
    native.command.assert_called_once_with("high", STATE)
    climate.transport.command.assert_not_called()


def test_native_safe_stop_is_rejected_without_relay_or_retry():
    climate, reader = make_bridge()
    native = Mock()
    native.command.side_effect = RuntimeError("state outside qualified swing shape")
    climate.direct_swing = native
    climate.transport.command = Mock(side_effect=AssertionError("boundary called"))

    with pytest.raises(RelayFreeCommandRejected, match="native command rejected"):
        climate.execute_command({"swing": "horizontal"})

    assert reader.calls == 1
    climate.transport.command.assert_not_called()
    assert climate.diagnostics.command_failure_count == 1
    assert "command rejected" in climate.diagnostics.last_error


def test_unqualified_feature_is_rejected_after_fresh_direct_read():
    climate, reader = make_bridge()
    climate.transport.command = Mock(side_effect=AssertionError("boundary called"))

    with pytest.raises(RelayFreeCommandRejected, match="no qualified native command path"):
        climate.execute_command({"display": False})

    assert reader.calls == 1
    assert climate.last_state == STATE
    climate.transport.command.assert_not_called()


def test_mqtt_rejection_republishes_confirmed_direct_state():
    climate, _reader = make_bridge()
    climate.last_state = dict(STATE)
    climate.execute_command = Mock(
        side_effect=RelayFreeCommandRejected("unqualified test command")
    )
    climate.publish_state = Mock()
    message = Mock()
    message.topic = f"{climate.config.base_topic}/display/set"
    message.payload = b"OFF"

    climate.on_mqtt_message(message)

    climate.publish_state.assert_called_once_with(STATE)


def test_startup_banner_declares_no_relay_runtime(caplog):
    with caplog.at_level("INFO", logger="climate_bridge"):
        log_startup_banner(relay_free_config(), "Relay (Legacy)")

    assert "Transport    : Native LAN (no Relay runtime)" in caplog.text
    assert "State Source : authenticated direct LAN read" in caplog.text
