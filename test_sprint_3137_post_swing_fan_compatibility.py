from __future__ import annotations

from pathlib import Path

import pytest

from adapters.york.broadlink import (
    BroadlinkYorkFanOffQualificationClient,
    york_xor,
)
from adapters.york.fan_off_qualification import (
    YORK_CANDIDATE_HEAT_HIGH_OFF_22_5,
)
from configuration import load_config
from direct_fan_manager import (
    DirectFanManager,
    DirectFanSafeStop,
    DirectFanVerificationError,
)
from test_sprint_3111_temperature_boundary_qualification import (
    FakeSocket,
)


def _state(fan: str = "low", swing: str = "horizontal", **overrides):
    state = {
        "power": True,
        "mode": "heat",
        "temperature": 22.5,
        "indoor_temperature": 23,
        "fan": fan,
        "swing": swing,
        "turbo": False,
        "eco": False,
        "health": False,
        "display": True,
    }
    state.update(overrides)
    return state


def _state_frame(state: dict) -> bytes:
    mode = {"cool": 0x01, "heat": 0x04}[state["mode"]]
    fan = {"low": 0x10, "high": 0x30}[state["fan"]]
    swing = {
        "off": 0x00,
        "horizontal": 0x20,
        "vertical": 0x40,
        "both": 0x60,
    }[state["swing"]]
    whole = int(state["temperature"])
    frame = bytearray.fromhex(
        "BB 01 00 03 0F 01 00 00 00 00 00 00 00 00 00 00 00 60 00 00 00"
    )
    frame[7] = 0x20 | mode | (0x10 if state["power"] else 0)
    frame[8] = fan | (whole - 16)
    frame[9] = 0x02 if state["temperature"] != whole else 0
    frame[10] = swing
    frame[-1] = york_xor(frame[:-1])
    return bytes(frame)


def _manager(*, direct_before=None, after=None):
    config = load_config(Path("config.example.yml"))
    sock = FakeSocket(
        _state_frame(direct_before or _state()),
        _state_frame(after or _state("high", "off")),
        YORK_CANDIDATE_HEAT_HIGH_OFF_22_5,
    )

    def factory(host, port, mac, timeout, fan):
        assert fan == "high"
        return BroadlinkYorkFanOffQualificationClient(
            host,
            port,
            mac,
            timeout,
            fan,
            socket_factory=lambda *_args: sock,
        )

    return DirectFanManager(config, off_client_factory=factory), sock


def test_alpha66_exact_failed_source_normalises_to_high_off_with_four_sends():
    manager, sock = _manager()
    response = manager.command("high", _state())
    transaction = response["_transaction"]

    assert response["fan"] == "high"
    assert response["swing"] == "off"
    assert transaction["qualified_path"] == (
        "alpha66_heat_22_5_low_horizontal_to_high_off_qualification"
    )
    assert transaction["before"]["swing"] == "horizontal"
    assert transaction["after"]["swing"] == "off"
    assert transaction["verification"] == {
        "success": True,
        "matched_fields": 9,
        "compared_fields": 9,
    }
    assert transaction["udp_sends"] == 4
    assert transaction["automatic_retries"] == 0
    assert transaction["fallback_used"] is False
    assert len(sock.sent) == 4


@pytest.mark.parametrize(
    "state",
    (
        _state(mode="cool"),
        _state(temperature=22.0),
        _state(fan="high"),
        _state(swing="both"),
        _state(power=False),
        _state(turbo=True),
        _state(eco=True),
        _state(health=True),
        _state(display=False),
    ),
)
def test_alpha66_nearby_shapes_remain_zero_write_stops(state):
    config = load_config(Path("config.example.yml"))

    def forbidden(*_args, **_kwargs):
        raise AssertionError("client created for an unqualified Alpha.66 state")

    manager = DirectFanManager(
        config,
        client_factory=forbidden,
        off_client_factory=forbidden,
        cool_off_client_factory=forbidden,
    )
    with pytest.raises(DirectFanSafeStop):
        manager.command("high" if state["fan"] == "low" else "low", state)
    assert manager.last_udp_sends == 0


def test_alpha66_fresh_pre_read_must_repeat_exact_horizontal_source():
    manager, sock = _manager(direct_before=_state(swing="off"))
    with pytest.raises(DirectFanSafeStop, match="direct pre-read differs.*swing"):
        manager.command("high", _state())
    assert manager.last_udp_sends == 2
    assert len(sock.sent) == 2


def test_alpha66_post_read_requires_both_high_and_off():
    manager, sock = _manager(after=_state("high", "horizontal"))
    with pytest.raises(DirectFanVerificationError, match="swing"):
        manager.command("high", _state())
    assert manager.last_udp_sends == 4
    assert len(sock.sent) == 4


def test_alpha66_does_not_authorise_horizontal_high_to_low():
    config = load_config(Path("config.example.yml"))
    manager = DirectFanManager(config)
    with pytest.raises(DirectFanSafeStop, match="swing"):
        manager.command("low", _state("high", "horizontal"))
    assert manager.last_udp_sends == 0
