from __future__ import annotations

import threading
from pathlib import Path

import pytest

from adapters.york import (
    BroadlinkYorkOneShotWriteClient,
    YORK_QUALIFICATION_DRY_LOW_BOTH_21,
    YORK_QUALIFICATION_DRY_LOW_VERTICAL_21,
)
from bridge import ClimateBridge
from configuration import load_config
from direct_swing_manager import (
    DirectSwingManager,
    DirectSwingSafeStop,
    DirectSwingVerificationError,
)
from test_sprint_310_guarded_direct_temperature import (
    DummyDiagnostics,
    DummyMqtt,
    DummyRelay,
)
from test_sprint_3111_temperature_boundary_qualification import FakeSocket
from test_sprint_3122_dry_horizontal_axis_qualification import _state_frame


def _state(swing: str, **changes):
    state = {
        "power": True,
        "mode": "dry",
        "temperature": 21.0,
        "indoor_temperature": 21,
        "fan": "low",
        "swing": swing,
        "turbo": False,
        "eco": False,
        "health": False,
        "display": True,
    }
    state.update(changes)
    return state


def _manager(before_swing, target_swing, *, live_before=None, live_after=None):
    command = (
        YORK_QUALIFICATION_DRY_LOW_BOTH_21
        if target_swing == "both"
        else YORK_QUALIFICATION_DRY_LOW_VERTICAL_21
    )
    sock = FakeSocket(
        _state_frame(live_before or _state(before_swing)),
        _state_frame(live_after or _state(target_swing)),
        command,
    )

    def dry_factory(host, port, mac, timeout, requested_command):
        assert requested_command == command
        return BroadlinkYorkOneShotWriteClient(
            "192.0.2.52",
            port,
            "02:00:00:00:00:52",
            timeout,
            requested_command,
            socket_factory=lambda *_args: sock,
        )

    config = load_config(Path("config.example.yml"))
    return DirectSwingManager(config, axis_client_factory=dry_factory), sock


@pytest.mark.parametrize(
    ("before_swing", "target_swing", "command"),
    [
        ("vertical", "both", YORK_QUALIFICATION_DRY_LOW_BOTH_21),
        ("both", "vertical", YORK_QUALIFICATION_DRY_LOW_VERTICAL_21),
    ],
)
def test_normal_control_uses_exact_qualified_frame_once(
    before_swing, target_swing, command
):
    manager, sock = _manager(before_swing, target_swing)

    response = manager.command(target_swing, _state(before_swing))

    assert response["swing"] == target_swing
    assert response["mode"] == "dry"
    assert response["temperature"] == 21.0
    assert response["fan"] == "low"
    assert response["_transaction"]["qualified_path"] == (
        "dry_21_low_independent_horizontal_axis"
    )
    assert response["_transaction"]["verification"]["matched_fields"] == 9
    assert response["_transaction"]["udp_sends"] == 4
    assert response["_transaction"]["automatic_retries"] == 0
    assert len(sock.sent) == 4
    assert command in (YORK_QUALIFICATION_DRY_LOW_BOTH_21,
                       YORK_QUALIFICATION_DRY_LOW_VERTICAL_21)


@pytest.mark.parametrize(
    ("before_swing", "target_swing", "changes"),
    [
        ("vertical", "horizontal", {}),
        ("off", "both", {}),
        ("both", "off", {}),
        ("vertical", "both", {"mode": "heat"}),
        ("vertical", "both", {"temperature": 21.5}),
        ("vertical", "both", {"fan": "high"}),
        ("vertical", "both", {"display": False}),
    ],
)
def test_unqualified_shape_stops_before_dry_client_or_socket(
    before_swing, target_swing, changes
):
    config = load_config(Path("config.example.yml"))

    def forbidden_client(*_args, **_kwargs):
        raise AssertionError("dry client created for unqualified state")

    manager = DirectSwingManager(config, axis_client_factory=forbidden_client)
    with pytest.raises(DirectSwingSafeStop):
        manager.command(target_swing, _state(before_swing, **changes))
    assert manager.last_udp_sends == 0


def test_live_pre_read_mismatch_stops_before_write():
    manager, sock = _manager(
        "vertical", "both", live_before=_state("vertical", fan="high")
    )
    with pytest.raises(DirectSwingSafeStop, match="direct pre-read differs"):
        manager.command("both", _state("vertical"))
    assert manager.last_udp_sends == 2
    assert len(sock.sent) == 2


def test_post_read_mismatch_is_not_success():
    manager, sock = _manager(
        "vertical", "both", live_after=_state("vertical")
    )
    with pytest.raises(DirectSwingVerificationError, match="post-read"):
        manager.command("both", _state("vertical"))
    assert manager.last_udp_sends == 4
    assert len(sock.sent) == 4


@pytest.mark.parametrize(
    ("before_swing", "target_swing"),
    [("vertical", "both"), ("both", "vertical")],
)
def test_bridge_uses_native_path_without_relay(before_swing, target_swing):
    state = _state(before_swing)
    response_state = {
        **_state(target_swing),
        "_transaction": {
            "success": True,
            "source": "york_direct_swing",
            "qualified_path": "dry_21_low_independent_horizontal_axis",
            "fallback_used": False,
        },
    }
    bridge = ClimateBridge.__new__(ClimateBridge)
    bridge.config = load_config(Path("config.example.yml"))
    bridge.stop_event = threading.Event()
    bridge.diagnostics = DummyDiagnostics()
    bridge.mqtt = DummyMqtt()
    bridge.transport = DummyRelay(response_state)
    bridge.direct_temperature = None
    bridge.direct_fan = None
    bridge.direct_swing = type(
        "DirectSwingStub",
        (),
        {"command": lambda self, target, relay: response_state,
         "last_udp_sends": 4},
    )()
    bridge.last_state = state
    bridge.pending_temperature = None
    bridge._update_health = lambda: None

    response = bridge.execute_command({"swing": target_swing})

    assert response["swing"] == target_swing
    assert response["_transaction"]["source"] == "york_direct_swing"
    assert bridge.transport.calls == []


def test_qualification_tool_is_not_executable_in_container():
    dockerfile = Path("Dockerfile").read_text(encoding="utf-8")
    assert "york_dry_horizontal_axis_qualification.py" not in dockerfile
