from __future__ import annotations

import threading
from pathlib import Path

import pytest

from adapters.york.broadlink import BroadlinkYorkFanWriteClient
from adapters.york.errors import YorkProtocolError
from adapters.york.fan_command import (
    build_qualified_heat_vertical_fan_command,
    validate_qualified_heat_vertical_fan_command,
)
from bridge import ClimateBridge
from configuration import load_config
from direct_fan_manager import (
    DirectFanManager,
    DirectFanSafeStop,
    DirectFanVerificationError,
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
    temperature: float = 25.0,
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
    before_fan: str,
    target_fan: str,
    temperature: float,
    *,
    after_fan: str | None = None,
    direct_before: dict[str, object] | None = None,
):
    config = load_config(Path("config.example.yml"))
    command = build_qualified_heat_vertical_fan_command(
        target_fan,
        temperature,
    )
    sock = FakeSocket(
        _state_frame(direct_before or _state(temperature, fan=before_fan)),
        _state_frame(
            _state(
                temperature,
                fan=after_fan if after_fan is not None else target_fan,
            )
        ),
        command,
    )

    def factory(host, port, mac, timeout, requested_fan, requested_temperature):
        assert requested_fan == target_fan
        assert requested_temperature == temperature
        return BroadlinkYorkFanWriteClient(
            "192.0.2.47",
            port,
            "02:00:00:00:00:47",
            timeout,
            requested_fan,
            requested_temperature,
            socket_factory=lambda *_args: sock,
        )

    return DirectFanManager(config, client_factory=factory), sock


@pytest.mark.parametrize(
    ("fan", "state_byte", "expected_25_hex", "expected_25_5_hex"),
    [
        (
            "low",
            0x3A,
            "BB0001031901004401063A00000000000000000000000000000000000000D8",
            "BB0001031901004401063A02000000000000000000000000000000000000DA",
        ),
        (
            "high",
            0x3D,
            "BB0001031901004401063D00000000000000000000000000000000000000DF",
            "BB0001031901004401063D02000000000000000000000000000000000000DD",
        ),
    ],
)
def test_fan_target_frames_reuse_exact_qualified_shapes(
    fan,
    state_byte,
    expected_25_hex,
    expected_25_5_hex,
):
    whole = build_qualified_heat_vertical_fan_command(fan, 25.0)
    half = build_qualified_heat_vertical_fan_command(fan, 25.5)

    assert whole.hex().upper() == expected_25_hex
    assert half.hex().upper() == expected_25_5_hex
    assert whole[10] == half[10] == state_byte
    assert whole[11] == 0x00
    assert half[11] == 0x02
    assert validate_qualified_heat_vertical_fan_command(whole, fan) == 25.0
    assert validate_qualified_heat_vertical_fan_command(half, fan) == 25.5


@pytest.mark.parametrize(
    "temperature",
    [value / 2 for value in range(32, 63)],
)
@pytest.mark.parametrize("fan", ("low", "high"))
def test_fan_generator_covers_complete_qualified_temperature_range(
    fan,
    temperature,
):
    frame = build_qualified_heat_vertical_fan_command(fan, temperature)

    assert (
        validate_qualified_heat_vertical_fan_command(frame, fan)
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
    ("before_fan", "target_fan"),
    [("low", "high"), ("high", "low")],
)
@pytest.mark.parametrize("temperature", (16.0, 25.0, 25.5, 30.5, 31.0))
def test_normal_fan_control_uses_one_guarded_native_write(
    before_fan,
    target_fan,
    temperature,
):
    manager, sock = _manager(before_fan, target_fan, temperature)

    response = manager.command(
        target_fan,
        _state(temperature, fan=before_fan),
    )

    assert response["fan"] == target_fan
    assert response["temperature"] == temperature
    assert response["swing"] == "vertical"
    transaction = response["_transaction"]
    assert transaction["source"] == "york_direct_fan"
    assert transaction["qualified_path"] == (
        "parameterised_heat_vertical_low_high"
    )
    assert transaction["requested"] == {"fan": target_fan}
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


@pytest.mark.parametrize("target_fan", ("auto", "medium", "turbo", ""))
def test_unqualified_target_stops_before_client_or_socket(target_fan):
    config = load_config(Path("config.example.yml"))

    def forbidden_client(*_args, **_kwargs):
        raise AssertionError("client created for an unqualified fan target")

    manager = DirectFanManager(config, client_factory=forbidden_client)

    with pytest.raises(DirectFanSafeStop):
        manager.command(target_fan, _state())

    assert manager.last_udp_sends == 0


@pytest.mark.parametrize(
    "state",
    [
        _state(fan="auto"),
        _state(fan="medium"),
        _state(fan="low", swing="off"),
        {**_state(fan="low"), "mode": "cool"},
        {**_state(fan="low"), "power": False},
        {**_state(fan="low"), "display": False},
    ],
)
def test_unqualified_starting_shape_stops_before_client_or_socket(state):
    config = load_config(Path("config.example.yml"))

    def forbidden_client(*_args, **_kwargs):
        raise AssertionError("client created for an unqualified state")

    manager = DirectFanManager(config, client_factory=forbidden_client)

    with pytest.raises(DirectFanSafeStop):
        manager.command("high", state)

    assert manager.last_udp_sends == 0


def test_live_state_mismatch_stops_after_auth_and_read_without_write():
    direct_before = _state(25.0, fan="low", swing="off")
    manager, sock = _manager(
        "low",
        "high",
        25.0,
        direct_before=direct_before,
    )

    with pytest.raises(
        DirectFanSafeStop,
        match="direct pre-read differs from relay state",
    ):
        manager.command("high", _state(25.0, fan="low"))

    assert manager.last_udp_sends == 2
    assert len(sock.sent) == 2


def test_post_read_mismatch_is_not_reported_as_success():
    manager, sock = _manager(
        "low",
        "high",
        25.0,
        after_fan="low",
    )

    with pytest.raises(
        DirectFanVerificationError,
        match="direct post-read verification failed: fan",
    ):
        manager.command("high", _state(25.0, fan="low"))

    assert manager.last_udp_sends == 4
    assert len(sock.sent) == 4


@pytest.mark.parametrize(
    ("before_fan", "target_fan"),
    [("low", "high"), ("high", "low")],
)
def test_bridge_uses_native_fan_path_without_relay_fallback(
    before_fan,
    target_fan,
):
    state = _state(25.0, fan=before_fan)
    response_state = {
        **_state(25.0, fan=target_fan),
        "_transaction": {
            "source": "york_direct_fan",
            "qualified_path": "parameterised_heat_vertical_low_high",
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
    bridge.direct_fan = type(
        "DirectFanStub",
        (),
        {
            "command": lambda self, target, relay: response_state,
            "last_udp_sends": 4,
        },
    )()
    bridge.last_state = state
    bridge.pending_temperature = None
    bridge._update_health = lambda: None

    response = bridge.execute_command({"fan": target_fan})

    assert response["fan"] == target_fan
    assert response["temperature"] == 25.0
    assert response["swing"] == "vertical"
    assert response["_transaction"]["source"] == "york_direct_fan"
    assert bridge.transport.calls == []


@pytest.mark.parametrize("target_fan", ("auto", "medium"))
def test_bridge_rejects_unqualified_fan_modes_without_fallback(target_fan):
    state = _state(25.0, fan="low")
    relay_response = {**state, "fan": target_fan}
    bridge = ClimateBridge.__new__(ClimateBridge)
    bridge.config = load_config(Path("config.example.yml"))
    bridge.stop_event = threading.Event()
    bridge.diagnostics = DummyDiagnostics()
    bridge.mqtt = DummyMqtt()
    bridge.transport = DummyRelay(relay_response)
    bridge.direct_temperature = None
    bridge.direct_fan = DirectFanManager(bridge.config)
    bridge.last_state = state
    bridge.pending_temperature = None
    bridge._update_health = lambda: None

    with pytest.raises(Exception, match="native command rejected"):
        bridge.execute_command({"fan": target_fan})

    assert bridge.transport.calls == []


def test_normal_control_imports_manager_not_qualification_tool():
    source = Path("bridge.py").read_text(encoding="utf-8")
    assert "DirectFanManager" in source
    assert "york_fan_one_shot_qualification" not in source
