from __future__ import annotations

from pathlib import Path
from unittest.mock import Mock

import pytest

from adapters.york.decoder import YorkPacketDecoder
from bridge import ClimateBridge
from configuration import load_config
from direct_temperature_manager import DirectTemperatureManager, DirectTemperatureSafeStop
from transport.york_direct_transport import YorkDirectTransport


DRY_CAPTURE_1 = bytes.fromhex(
    "BB0100030F0100330100000000000000005C0800D1"
)
FAN_ONLY_CAPTURE_2 = bytes.fromhex(
    "BB0100030F0100320700000000000000005A0000D8"
)


class _CapturedReadClient:
    last_send_count = 2

    def __init__(self, frame: bytes) -> None:
        self.frame = frame

    def read_state_frame(self) -> bytes:
        return self.frame


@pytest.mark.parametrize(
    ("frame", "expected"),
    ((DRY_CAPTURE_1, 17.0), (FAN_ONLY_CAPTURE_2, 16.0)),
)
def test_indoor_temperature_matches_official_sdk_captures(frame, expected):
    assert YorkPacketDecoder().decode_indoor_temperature(frame) == expected


def test_direct_fan_only_state_omits_placeholder_and_keeps_room_temperature():
    transport = YorkDirectTransport(load_config(Path("config.example.yml")))
    transport.client = _CapturedReadClient(FAN_ONLY_CAPTURE_2)

    state = transport.get_state()

    assert state["mode"] == "fan_only"
    assert "temperature" not in state
    assert state["indoor_temperature"] == 16.0


def test_fan_only_temperature_command_stops_before_client_creation():
    def forbidden(*_args, **_kwargs):
        raise AssertionError("temperature client created in Fan-only")

    manager = DirectTemperatureManager(
        load_config(Path("config.example.yml")),
        client_factory=forbidden,
        captured_client_factory=forbidden,
        low_vertical_client_factory=forbidden,
    )
    with pytest.raises(DirectTemperatureSafeStop, match="Heat or Cool"):
        manager.command(
            22.0,
            {
                "power": True,
                "mode": "fan_only",
                "fan": "auto",
                "swing": "off",
            },
        )
    assert manager.last_udp_sends == 0


def test_publish_state_does_not_publish_fan_only_placeholder_setpoint():
    bridge = object.__new__(ClimateBridge)
    bridge.config = Mock(base_topic="climate_bridge/york")
    bridge.mqtt = Mock()
    bridge.diagnostics = Mock()
    bridge.pending_temperature = None
    bridge.last_state = {}
    bridge.last_published_state = {}

    bridge.publish_state(
        {
            "power": True,
            "mode": "fan_only",
            "temperature": 23.0,
            "indoor_temperature": 16.0,
            "fan": "auto",
            "swing": "off",
        }
    )

    topics = [call.args[0] for call in bridge.mqtt.publish.call_args_list]
    assert "climate_bridge/york/temperature/state" in topics
    bridge.mqtt.publish.assert_any_call(
        "climate_bridge/york/temperature/state", None, retain=True
    )
    bridge.mqtt.publish.assert_any_call(
        "climate_bridge/york/current_temperature/state", 16.0, retain=True
    )
