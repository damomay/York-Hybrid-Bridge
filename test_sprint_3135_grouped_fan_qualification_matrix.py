from __future__ import annotations

import hashlib
from pathlib import Path

import pytest

from adapters.york.broadlink import (
    BroadlinkYorkCoolFanOffQualificationClient,
    YORK_QUALIFICATION_COMMANDS,
    york_xor,
)
from adapters.york.cool_fan_off_qualification import (
    YORK_CANDIDATE_COOL_HIGH_OFF_22_5,
    YORK_QUALIFICATION_COOL_LOW_OFF_22_5,
    build_cool_22_5_fan_off_qualification_command,
    validate_cool_22_5_fan_off_qualification_command,
)
from adapters.york.errors import YorkProtocolError
from adapters.york.fan_off_qualification import (
    YORK_CANDIDATE_HEAT_HIGH_OFF_22_5,
    YORK_QUALIFICATION_HEAT_LOW_OFF_22_5,
)
from adapters.york.power_on_command import build_parameterised_power_on_command
from configuration import load_config
from direct_fan_manager import (
    DirectFanManager,
    DirectFanSafeStop,
    DirectFanVerificationError,
)
from test_sprint_3111_temperature_boundary_qualification import (
    FakeSocket,
    _state_frame,
)


def _state(fan: str = "low", **overrides):
    state = {
        "power": True,
        "mode": "cool",
        "temperature": 22.5,
        "indoor_temperature": 21,
        "fan": fan,
        "swing": "off",
        "turbo": False,
        "eco": False,
        "health": False,
        "display": True,
    }
    state.update(overrides)
    return state


def _manager(before_fan="low", target_fan="high", *, direct_before=None, after=None):
    config = load_config(Path("config.example.yml"))
    command = build_cool_22_5_fan_off_qualification_command(target_fan)
    sock = FakeSocket(
        _state_frame(direct_before or _state(before_fan)),
        _state_frame(after or _state(target_fan)),
        command,
    )

    def factory(host, port, mac, timeout, fan):
        assert fan == target_fan
        return BroadlinkYorkCoolFanOffQualificationClient(
            host,
            port,
            mac,
            timeout,
            fan,
            socket_factory=lambda *_args: sock,
        )

    return DirectFanManager(config, cool_off_client_factory=factory), sock


def test_alpha64_cool_frames_are_exact_and_checksum_locked():
    assert YORK_QUALIFICATION_COOL_LOW_OFF_22_5.hex().upper() == (
        "BB0001031901004403090202000000000000000000000000000000000000EF"
    )
    assert YORK_CANDIDATE_COOL_HIGH_OFF_22_5.hex().upper() == (
        "BB0001031901004403090502000000000000000000000000000000000000E8"
    )
    assert york_xor(YORK_QUALIFICATION_COOL_LOW_OFF_22_5) == 0
    assert york_xor(YORK_CANDIDATE_COOL_HIGH_OFF_22_5) == 0
    assert hashlib.sha256(YORK_CANDIDATE_COOL_HIGH_OFF_22_5).hexdigest() == (
        "480527a4abe7644e8aa41f3ff9de0ebb86f6c8d4cb5ce170b62334f3f82fbc7e"
    )


def test_cool_low_frame_is_existing_canonical_mode_target():
    assert YORK_QUALIFICATION_COOL_LOW_OFF_22_5 == (
        build_parameterised_power_on_command("cool", 22.5, "low", "off")
    )


@pytest.mark.parametrize(
    ("heat", "cool"),
    (
        (YORK_QUALIFICATION_HEAT_LOW_OFF_22_5, YORK_QUALIFICATION_COOL_LOW_OFF_22_5),
        (YORK_CANDIDATE_HEAT_HIGH_OFF_22_5, YORK_CANDIDATE_COOL_HIGH_OFF_22_5),
    ),
)
def test_cool_frames_apply_only_proven_mode_delta_and_checksum(heat, cool):
    changed = [index for index, pair in enumerate(zip(heat, cool)) if pair[0] != pair[1]]
    assert changed == [8, 30]
    assert heat[8] == 0x01
    assert cool[8] == 0x03


def test_candidate_is_isolated_from_immutable_capture_replay_allowlist():
    assert YORK_CANDIDATE_COOL_HIGH_OFF_22_5 not in YORK_QUALIFICATION_COMMANDS
    assert YORK_QUALIFICATION_COOL_LOW_OFF_22_5 not in YORK_QUALIFICATION_COMMANDS


@pytest.mark.parametrize("fan", ("low", "high"))
def test_case_specific_validator_accepts_only_exact_cool_frame(fan):
    frame = build_cool_22_5_fan_off_qualification_command(fan)
    validate_cool_22_5_fan_off_qualification_command(frame, fan)
    changed = bytearray(frame)
    changed[8] ^= 1
    changed[-1] ^= 1
    with pytest.raises(YorkProtocolError, match="non-canonical"):
        validate_cool_22_5_fan_off_qualification_command(bytes(changed), fan)


@pytest.mark.parametrize(
    ("before_fan", "target_fan"),
    (("low", "high"), ("high", "low")),
)
def test_cool_matrix_path_uses_four_sends_and_verifies_nine_fields(
    before_fan,
    target_fan,
):
    manager, sock = _manager(before_fan, target_fan)
    response = manager.command(target_fan, _state(before_fan))
    transaction = response["_transaction"]

    assert response["mode"] == "cool"
    assert response["fan"] == target_fan
    assert response["temperature"] == 22.5
    assert response["swing"] == "off"
    assert transaction["qualified_path"] == (
        "alpha64_cool_22_5_off_low_high_qualification"
    )
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
        _state(temperature=22.0),
        _state(mode="dry"),
        _state(swing="vertical"),
        _state(power=False),
        _state(turbo=True),
        _state(eco=True),
        _state(health=True),
        _state(display=False),
    ),
)
def test_nearby_unqualified_cool_shapes_stop_before_socket(state):
    config = load_config(Path("config.example.yml"))

    def forbidden(*_args, **_kwargs):
        raise AssertionError("client created for an unqualified Alpha.64 state")

    manager = DirectFanManager(
        config,
        client_factory=forbidden,
        off_client_factory=forbidden,
        cool_off_client_factory=forbidden,
    )
    with pytest.raises(DirectFanSafeStop):
        manager.command("high", state)
    assert manager.last_udp_sends == 0


def test_fresh_cool_pre_read_mismatch_stops_after_two_sends_without_write():
    manager, sock = _manager(direct_before=_state(temperature=23.0))
    with pytest.raises(DirectFanSafeStop, match="direct pre-read differs"):
        manager.command("high", _state("low"))
    assert manager.last_udp_sends == 2
    assert len(sock.sent) == 2


def test_cool_post_read_mismatch_is_reported_without_retry():
    manager, sock = _manager(after=_state("low"))
    with pytest.raises(DirectFanVerificationError, match="fan"):
        manager.command("high", _state("low"))
    assert manager.last_udp_sends == 4
    assert len(sock.sent) == 4
