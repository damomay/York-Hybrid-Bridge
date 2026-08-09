from __future__ import annotations

import threading
from pathlib import Path

import pytest

from adapters.york.broadlink import BroadlinkYorkSwingWriteClient
from adapters.york.errors import YorkProtocolError
from adapters.york.swing_command import (
    build_qualified_heat_low_swing_command,
    validate_qualified_heat_low_swing_command,
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
from test_sprint_3111_temperature_boundary_qualification import (
    FakeSocket,
    _state_frame,
)


def _state(
    temperature: float = 21.0,
    *,
    fan: str = "low",
    swing: str = "vertical",
) -> dict[str, object]:
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


def _manager(
    before_swing: str,
    target_swing: str,
    temperature: float,
    *,
    after_swing: str | None = None,
    direct_before: dict[str, object] | None = None,
):
    config = load_config(Path("config.example.yml"))
    command = build_qualified_heat_low_swing_command(
        target_swing,
        temperature,
    )
    sock = FakeSocket(
        _state_frame(
            direct_before
            or _state(temperature, swing=before_swing)
        ),
        _state_frame(
            _state(
                temperature,
                swing=(
                    after_swing
                    if after_swing is not None
                    else target_swing
                ),
            )
        ),
        command,
    )

    def factory(
        host,
        port,
        mac,
        timeout,
        requested_swing,
        requested_temperature,
    ):
        assert requested_swing == target_swing
        assert requested_temperature == temperature
        return BroadlinkYorkSwingWriteClient(
            "192.0.2.48",
            port,
            "02:00:00:00:00:48",
            timeout,
            requested_swing,
            requested_temperature,
            socket_factory=lambda *_args: sock,
        )

    return DirectSwingManager(config, client_factory=factory), sock


@pytest.mark.parametrize(
    ("swing", "state_byte", "expected_21_hex", "expected_21_5_hex"),
    [
        (
            "off",
            0x02,
            "BB00010319010044010A0200000000000000000000000000000000000000EC",
            "BB00010319010044010A0202000000000000000000000000000000000000EE",
        ),
        (
            "vertical",
            0x3A,
            "BB00010319010044010A3A00000000000000000000000000000000000000D4",
            "BB00010319010044010A3A02000000000000000000000000000000000000D6",
        ),
    ],
)
def test_swing_target_frames_reuse_exact_qualified_shapes(
    swing,
    state_byte,
    expected_21_hex,
    expected_21_5_hex,
):
    whole = build_qualified_heat_low_swing_command(swing, 21.0)
    half = build_qualified_heat_low_swing_command(swing, 21.5)

    assert whole.hex().upper() == expected_21_hex
    assert half.hex().upper() == expected_21_5_hex
    assert whole[10] == half[10] == state_byte
    assert whole[11] == 0x00
    assert half[11] == 0x02
    assert validate_qualified_heat_low_swing_command(
        whole,
        swing,
    ) == 21.0
    assert validate_qualified_heat_low_swing_command(
        half,
        swing,
    ) == 21.5


@pytest.mark.parametrize(
    "temperature",
    [value / 2 for value in range(32, 61)],
)
@pytest.mark.parametrize("swing", ("off", "vertical"))
def test_swing_generator_covers_shared_qualified_temperature_range(
    swing,
    temperature,
):
    frame = build_qualified_heat_low_swing_command(swing, temperature)

    assert (
        validate_qualified_heat_low_swing_command(frame, swing)
        == temperature
    )
    assert frame[11] == (0x02 if temperature % 1 else 0x00)
    assert not _xor(frame)


def _xor(frame: bytes) -> int:
    value = 0
    for byte in frame:
        value ^= byte
    return value


@pytest.mark.parametrize(
    ("before_swing", "target_swing"),
    [("vertical", "off"), ("off", "vertical")],
)
@pytest.mark.parametrize("temperature", (16.0, 21.0, 21.5, 29.5, 30.0))
def test_normal_swing_control_uses_one_guarded_native_write(
    before_swing,
    target_swing,
    temperature,
):
    manager, sock = _manager(before_swing, target_swing, temperature)

    response = manager.command(
        target_swing,
        _state(temperature, swing=before_swing),
    )

    assert response["swing"] == target_swing
    assert response["temperature"] == temperature
    assert response["fan"] == "low"
    transaction = response["_transaction"]
    assert transaction["source"] == "york_direct_swing"
    assert transaction["qualified_path"] == (
        "parameterised_heat_low_off_vertical"
    )
    assert transaction["requested"] == {"swing": target_swing}
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


@pytest.mark.parametrize("target_swing", ("horizontal", "both", "auto", ""))
def test_unqualified_target_stops_before_client_or_socket(target_swing):
    config = load_config(Path("config.example.yml"))

    def forbidden_client(*_args, **_kwargs):
        raise AssertionError("client created for unqualified swing target")

    manager = DirectSwingManager(config, client_factory=forbidden_client)

    with pytest.raises(DirectSwingSafeStop):
        manager.command(target_swing, _state())

    assert manager.last_udp_sends == 0


@pytest.mark.parametrize(
    "state",
    [
        _state(swing="horizontal"),
        _state(swing="both"),
        _state(fan="high"),
        {**_state(), "mode": "cool"},
        {**_state(), "power": False},
        {**_state(), "display": False},
    ],
)
def test_unqualified_starting_shape_stops_before_client_or_socket(state):
    config = load_config(Path("config.example.yml"))

    def forbidden_client(*_args, **_kwargs):
        raise AssertionError("client created for unqualified state")

    manager = DirectSwingManager(config, client_factory=forbidden_client)

    with pytest.raises(DirectSwingSafeStop):
        manager.command("off", state)

    assert manager.last_udp_sends == 0


@pytest.mark.parametrize("temperature", (15.5, 30.5, 31.0, 21.25))
def test_unshared_temperature_stops_before_client_or_socket(temperature):
    config = load_config(Path("config.example.yml"))

    def forbidden_client(*_args, **_kwargs):
        raise AssertionError("client created for unqualified temperature")

    manager = DirectSwingManager(config, client_factory=forbidden_client)

    with pytest.raises(YorkProtocolError):
        manager.command("off", _state(temperature))

    assert manager.last_udp_sends == 0


def test_live_state_mismatch_stops_after_auth_and_read_without_write():
    direct_before = _state(21.0, fan="high", swing="vertical")
    manager, sock = _manager(
        "vertical",
        "off",
        21.0,
        direct_before=direct_before,
    )

    with pytest.raises(
        DirectSwingSafeStop,
        match="direct pre-read differs from relay state",
    ):
        manager.command("off", _state(21.0, swing="vertical"))

    assert manager.last_udp_sends == 2
    assert len(sock.sent) == 2


def test_post_read_mismatch_is_not_reported_as_success():
    manager, sock = _manager(
        "vertical",
        "off",
        21.0,
        after_swing="vertical",
    )

    with pytest.raises(
        DirectSwingVerificationError,
        match="direct post-read verification failed: swing",
    ):
        manager.command("off", _state(21.0, swing="vertical"))

    assert manager.last_udp_sends == 4
    assert len(sock.sent) == 4


@pytest.mark.parametrize(
    ("before_swing", "target_swing"),
    [("vertical", "off"), ("off", "vertical")],
)
def test_bridge_uses_native_swing_path_without_relay_fallback(
    before_swing,
    target_swing,
):
    state = _state(21.0, swing=before_swing)
    response_state = {
        **_state(21.0, swing=target_swing),
        "_transaction": {
            "source": "york_direct_swing",
            "qualified_path": "parameterised_heat_low_off_vertical",
            "success": True,
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
        {
            "command": lambda self, target, relay: response_state,
            "last_udp_sends": 4,
        },
    )()
    bridge.last_state = state
    bridge.pending_temperature = None
    bridge._update_health = lambda: None

    response = bridge.execute_command({"swing": target_swing})

    assert response["swing"] == target_swing
    assert response["temperature"] == 21.0
    assert response["fan"] == "low"
    assert response["_transaction"]["source"] == "york_direct_swing"
    assert bridge.transport.calls == []


@pytest.mark.parametrize("target_swing", ("horizontal", "both"))
def test_bridge_rejects_unqualified_swing_modes_without_fallback(
    target_swing,
):
    state = _state(21.0, swing="vertical")
    relay_response = {**state, "swing": target_swing}
    bridge = ClimateBridge.__new__(ClimateBridge)
    bridge.config = load_config(Path("config.example.yml"))
    bridge.stop_event = threading.Event()
    bridge.diagnostics = DummyDiagnostics()
    bridge.mqtt = DummyMqtt()
    bridge.transport = DummyRelay(relay_response)
    bridge.direct_temperature = None
    bridge.direct_fan = None
    bridge.direct_swing = DirectSwingManager(bridge.config)
    bridge.last_state = state
    bridge.pending_temperature = None
    bridge._update_health = lambda: None

    with pytest.raises(Exception, match="native command rejected"):
        bridge.execute_command({"swing": target_swing})

    assert bridge.transport.calls == []


def test_normal_control_imports_manager_not_qualification_tool():
    source = Path("bridge.py").read_text(encoding="utf-8")
    assert "DirectSwingManager" in source
    assert "york_swing_one_shot_qualification" not in source
