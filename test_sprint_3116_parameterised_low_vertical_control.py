from __future__ import annotations

import threading
from pathlib import Path

import pytest

from adapters.york.broadlink import BroadlinkYorkLowVerticalTemperatureWriteClient
from adapters.york.errors import YorkProtocolError
from adapters.york.low_vertical_temperature_command import (
    build_captured_heat_low_vertical_temperature_command,
)
from bridge import ClimateBridge
from configuration import load_config
from direct_temperature_manager import DirectTemperatureManager
from test_sprint_310_guarded_direct_temperature import (
    DummyDiagnostics,
    DummyMqtt,
    DummyRelay,
)
from test_sprint_3111_temperature_boundary_qualification import (
    FakeSocket,
    _state_frame,
)


def _state(temperature: float) -> dict[str, object]:
    return {
        "power": True,
        "mode": "heat",
        "temperature": float(temperature),
        "indoor_temperature": 21,
        "fan": "low",
        "swing": "vertical",
        "turbo": False,
        "eco": False,
        "health": False,
        "display": True,
    }


def _manager(before: float, target: float):
    config = load_config(Path("config.example.yml"))
    command = build_captured_heat_low_vertical_temperature_command(target)
    sock = FakeSocket(
        _state_frame(_state(before)),
        _state_frame(_state(target)),
        command,
    )

    def factory(host, port, mac, timeout, requested_target):
        assert requested_target == target
        return BroadlinkYorkLowVerticalTemperatureWriteClient(
            "192.0.2.45",
            port,
            "02:00:00:00:00:45",
            timeout,
            requested_target,
            socket_factory=lambda *_args: sock,
        )

    return (
        DirectTemperatureManager(
            config,
            low_vertical_client_factory=factory,
        ),
        sock,
    )


@pytest.mark.parametrize(
    ("before", "target"),
    [
        (25.0, 26.0),
        (26.0, 25.0),
        (25.0, 16.0),
        (25.0, 31.0),
        (16.0, 31.0),
        (31.0, 16.0),
        (24.0, 25.0),
    ],
)
def test_parameterised_low_vertical_normal_control(
    before: float,
    target: float,
):
    manager, sock = _manager(before, target)

    response = manager.command(target, _state(before))

    assert response["temperature"] == target
    assert response["fan"] == "low"
    assert response["swing"] == "vertical"
    transaction = response["_transaction"]
    assert transaction["source"] == "york_direct_temperature_low_vertical"
    assert transaction["qualified_path"] == "parameterised_heat_low_vertical"
    assert transaction["verification"] == {
        "success": True,
        "matched_fields": 9,
        "compared_fields": 9,
    }
    assert transaction["udp_sends"] == 4
    assert transaction["automatic_retries"] == 0
    assert transaction["fallback_used"] is False
    assert manager.last_udp_sends == 4
    assert len(sock.sent) == 4


@pytest.mark.parametrize("target", (15.0, 15.5, 25.25, 31.5, 32.0))
def test_invalid_target_stops_before_client_or_socket(target: float):
    config = load_config(Path("config.example.yml"))

    def forbidden_client(*_args, **_kwargs):
        raise AssertionError("client created for invalid target")

    manager = DirectTemperatureManager(
        config,
        client_factory=forbidden_client,
        captured_client_factory=forbidden_client,
        low_vertical_client_factory=forbidden_client,
    )

    with pytest.raises(YorkProtocolError):
        manager.command(target, _state(25.0))

    assert manager.last_udp_sends == 0


def test_live_state_mismatch_stops_before_write():
    config = load_config(Path("config.example.yml"))
    target = 26.0
    command = build_captured_heat_low_vertical_temperature_command(target)
    direct_before = _state(25.0)
    direct_before["swing"] = "off"
    sock = FakeSocket(
        _state_frame(direct_before),
        _state_frame(_state(target)),
        command,
    )

    def factory(host, port, mac, timeout, requested_target):
        return BroadlinkYorkLowVerticalTemperatureWriteClient(
            "192.0.2.45",
            port,
            "02:00:00:00:00:45",
            timeout,
            requested_target,
            socket_factory=lambda *_args: sock,
        )

    manager = DirectTemperatureManager(
        config,
        low_vertical_client_factory=factory,
    )

    with pytest.raises(Exception, match="direct pre-read differs from relay state"):
        manager.command(target, _state(25.0))

    assert manager.last_udp_sends == 2
    assert len(sock.sent) == 2


def test_bridge_uses_parameterised_path_without_relay_fallback():
    state = _state(25.0)
    direct_response = {
        **_state(26.0),
        "_transaction": {
            "source": "york_direct_temperature_low_vertical",
            "qualified_path": "parameterised_heat_low_vertical",
            "success": True,
            "fallback_used": False,
        },
    }
    bridge = ClimateBridge.__new__(ClimateBridge)
    bridge.config = load_config(Path("config.example.yml"))
    bridge.stop_event = threading.Event()
    bridge.diagnostics = DummyDiagnostics()
    bridge.mqtt = DummyMqtt()
    bridge.transport = DummyRelay({**state, "temperature": 26.0})
    bridge.direct_temperature = type(
        "DirectStub",
        (),
        {
            "command": lambda self, target, relay: direct_response,
            "last_udp_sends": 4,
        },
    )()
    bridge.last_state = state
    bridge.pending_temperature = None
    bridge._update_health = lambda: None

    response = bridge.execute_command({"temperature": 26.0})

    assert response["temperature"] == 26.0
    assert response["_transaction"]["qualified_path"] == (
        "parameterised_heat_low_vertical"
    )
    assert bridge.transport.calls == []


def test_normal_control_imports_generator_not_qualification_tool():
    source = Path("direct_temperature_manager.py").read_text(encoding="utf-8")
    assert "build_captured_heat_low_vertical_temperature_command" in source
    assert "york_low_vertical_temperature_range_qualification" not in source
