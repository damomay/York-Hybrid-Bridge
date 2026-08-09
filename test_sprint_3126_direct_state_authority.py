from __future__ import annotations

from dataclasses import replace
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from bridge import ClimateBridge
from configuration import load_config
from direct_read_manager import DirectReadManager, DirectReadResult


DIRECT_STATE = {
    "power": True,
    "mode": "heat",
    "temperature": 21.5,
    "indoor_temperature": 22.0,
    "fan": "low",
    "swing": "off",
    "turbo": False,
    "eco": False,
    "health": False,
    "display": True,
}


def result(state: dict | None = None) -> DirectReadResult:
    observed = dict(DIRECT_STATE if state is None else state)
    return DirectReadResult(
        state=observed,
        comparison="authoritative (9 decoded fields)",
        matched_fields=9,
        compared_fields=9,
        response_length=21,
        udp_sends=2,
        raw_frame_hex="BB00",
        fan_status_byte=0x30,
        fan_status_nibble=3,
    )


class FakeDirectTransport:
    last_response_length = 21
    last_send_count = 2
    last_raw_frame_hex = "BB00"
    last_fan_status_byte = 0x30
    last_fan_status_nibble = 3

    def __init__(self, _config) -> None:
        self.calls = 0

    def get_state(self):
        self.calls += 1
        return dict(DIRECT_STATE)

    def close(self) -> None:
        return None


class FakeRelayTransport:
    name = "tablet_relay"
    display_name = "Relay (Legacy)"

    def __init__(self) -> None:
        self.get_state_calls = 0
        self.command_calls = 0
        self.command_response = {
            "power": False,
            "mode": "cool",
            "temperature": 30.0,
            "fan": "high",
            "swing": "both",
            "_transaction": {"success": True, "source": "tablet_relay"},
        }

    def get_state(self):
        self.get_state_calls += 1
        raise AssertionError("Relay /state was used during direct authority")

    def command(self, **_changes):
        self.command_calls += 1
        return dict(self.command_response)

    def close(self) -> None:
        return None


class FakeDirectManager:
    def __init__(self, states=None, error: Exception | None = None) -> None:
        self.states = list(states or [DIRECT_STATE])
        self.error = error
        self.calls = 0

    def read_authoritative(self):
        self.calls += 1
        if self.error is not None:
            raise self.error
        state = self.states[min(self.calls - 1, len(self.states) - 1)]
        return result(state)

    def close(self) -> None:
        return None


def make_bridge(direct: FakeDirectManager, relay: FakeRelayTransport):
    config = replace(
        load_config(Path("config.example.yml")),
        direct_read_enabled=True,
    )
    with (
        patch("bridge.create_transport", return_value=relay),
        patch("bridge.DirectReadManager", return_value=direct),
        patch("bridge.MqttManager"),
    ):
        bridge = ClimateBridge(config)
    bridge.mqtt.publish = Mock(return_value=True)
    return bridge


def test_authoritative_manager_reads_immediately_without_shadow_schedule():
    config = load_config(Path("config.example.yml"))
    transport = FakeDirectTransport(config)
    manager = DirectReadManager(config, transport_factory=lambda _cfg: transport)

    first = manager.read_authoritative()
    second = manager.read_authoritative()

    assert first.state == DIRECT_STATE
    assert first.comparison == "authoritative (9 decoded fields)"
    assert second.state == DIRECT_STATE
    assert transport.calls == 2


def test_poll_publishes_direct_state_without_relay_state_request():
    relay = FakeRelayTransport()
    bridge = make_bridge(FakeDirectManager(), relay)
    bridge.publish_state = Mock()

    bridge.poll_once()

    bridge.publish_state.assert_called_once_with(DIRECT_STATE)
    assert relay.get_state_calls == 0


def test_native_command_guard_receives_fresh_direct_state():
    relay = FakeRelayTransport()
    bridge = make_bridge(FakeDirectManager(), relay)
    fan = Mock()
    fan.command.return_value = {
        **DIRECT_STATE,
        "fan": "high",
        "_transaction": {"success": True},
    }
    bridge.direct_fan = fan

    response = bridge.execute_command({"fan": "high"})

    fan.command.assert_called_once_with("high", DIRECT_STATE)
    assert response["fan"] == "high"
    assert relay.command_calls == 0
    assert relay.get_state_calls == 0


def test_native_safe_stop_is_rejected_without_fallback():
    relay = FakeRelayTransport()
    after = {**DIRECT_STATE, "swing": "horizontal"}
    bridge = make_bridge(FakeDirectManager([DIRECT_STATE, after]), relay)
    swing = Mock()
    swing.command.side_effect = RuntimeError("unqualified")
    bridge.direct_swing = swing

    with pytest.raises(Exception, match="native command rejected"):
        bridge.execute_command({"swing": "horizontal"})

    assert relay.command_calls == 0
    assert relay.get_state_calls == 0


def test_direct_read_failure_blocks_relay_command_selection():
    relay = FakeRelayTransport()
    bridge = make_bridge(
        FakeDirectManager(error=TimeoutError("direct state unavailable")),
        relay,
    )

    with pytest.raises(TimeoutError, match="direct state unavailable"):
        bridge.execute_command({"display": False})

    assert relay.command_calls == 0
    assert relay.get_state_calls == 0
