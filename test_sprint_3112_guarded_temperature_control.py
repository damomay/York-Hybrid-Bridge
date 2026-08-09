from __future__ import annotations

import threading
from pathlib import Path

import pytest

from adapters.york.broadlink import BroadlinkYorkCapturedTemperatureWriteClient
from adapters.york.captured_temperature_command import (
    build_captured_heat_high_vertical_temperature_command,
)
from bridge import ClimateBridge
from configuration import load_config
from direct_temperature_manager import (
    DirectTemperatureManager,
    DirectTemperatureSafeStop,
)
from test_sprint_310_guarded_direct_temperature import (
    DummyDiagnostics,
    DummyMqtt,
    DummyRelay,
)
from test_sprint_3111_temperature_boundary_qualification import (
    FakeSocket,
    _state_frame,
)


def _state(temperature: float, *, fan: str = "high", swing: str = "vertical"):
    return {
        "power": True,
        "mode": "heat",
        "temperature": float(temperature),
        "indoor_temperature": 21,
        "fan": fan,
        "swing": swing,
        "turbo": False,
        "eco": False,
        "health": False,
        "display": True,
    }


def _manager(before: float, target: float):
    config = load_config(Path("config.example.yml"))
    command = build_captured_heat_high_vertical_temperature_command(target)
    before_state = _state(before)
    after_state = _state(target)
    sock = FakeSocket(
        _state_frame(before_state),
        _state_frame(after_state),
        command,
    )

    def factory(host, port, mac, timeout, requested_target):
        assert requested_target == target
        return BroadlinkYorkCapturedTemperatureWriteClient(
            "192.0.2.41",
            port,
            "02:00:00:00:00:41",
            timeout,
            requested_target,
            socket_factory=lambda *_args: sock,
        )

    return (
        DirectTemperatureManager(
            config,
            captured_client_factory=factory,
        ),
        sock,
    )


@pytest.mark.parametrize(
    ("before", "target"),
    [
        (16.0, 17.0),
        (23.0, 24.0),
        (24.0, 23.0),
        (30.0, 31.0),
        (31.0, 16.0),
    ],
)
def test_normal_guarded_whole_degree_temperature_control(before, target):
    manager, sock = _manager(before, target)

    response = manager.command(target, _state(before))

    assert response["temperature"] == target
    assert response["_transaction"]["source"] == (
        "york_direct_temperature_captured"
    )
    assert response["_transaction"]["qualified_path"] == (
        "captured_heat_high_vertical"
    )
    assert response["_transaction"]["verification"] == {
        "success": True,
        "matched_fields": 9,
        "compared_fields": 9,
    }
    assert response["_transaction"]["automatic_retries"] == 0
    assert response["_transaction"]["fallback_used"] is False
    assert manager.last_udp_sends == 4
    assert len(sock.sent) == 4


@pytest.mark.parametrize("target", [15.0, 23.25, 32.0])
def test_invalid_captured_target_stops_before_client(target):
    config = load_config(Path("config.example.yml"))

    def forbidden_client(*_args, **_kwargs):
        raise AssertionError("client created for an invalid captured target")

    manager = DirectTemperatureManager(
        config,
        captured_client_factory=forbidden_client,
    )

    with pytest.raises(Exception):
        manager.command(target, _state(23.0))


def test_non_half_step_low_vertical_target_stops_before_client():
    config = load_config(Path("config.example.yml"))

    def forbidden_client(*_args, **_kwargs):
        raise AssertionError("client created for Low/Vertical fallback state")

    manager = DirectTemperatureManager(
        config,
        client_factory=forbidden_client,
        captured_client_factory=forbidden_client,
        low_vertical_client_factory=forbidden_client,
    )

    with pytest.raises(Exception):
        manager.command(24.25, _state(23.0, fan="low", swing="vertical"))


def test_bridge_rejects_non_half_step_low_vertical_target_without_fallback():
    state = _state(23.0, fan="low", swing="vertical")
    relay_response = {**state, "temperature": 24.25}
    bridge = ClimateBridge.__new__(ClimateBridge)
    bridge.config = load_config(Path("config.example.yml"))
    bridge.stop_event = threading.Event()
    bridge.diagnostics = DummyDiagnostics()
    bridge.mqtt = DummyMqtt()
    bridge.transport = DummyRelay(relay_response)
    bridge.direct_temperature = DirectTemperatureManager(bridge.config)
    bridge.last_state = state
    bridge.pending_temperature = None
    bridge._update_health = lambda: None

    with pytest.raises(Exception, match="native command rejected"):
        bridge.execute_command({"temperature": 24.25})

    assert bridge.transport.calls == []


def test_alpha41_release_exposes_normal_control_without_one_shot_tool_import():
    source = Path("direct_temperature_manager.py").read_text(encoding="utf-8")
    assert "build_captured_heat_high_vertical_temperature_command" in source
    assert "york_temperature_one_shot_qualification" not in source
