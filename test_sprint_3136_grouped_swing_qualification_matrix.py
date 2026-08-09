from __future__ import annotations

import hashlib
from pathlib import Path

import pytest

from adapters.york.broadlink import (
    BroadlinkYorkSwingMatrixQualificationClient,
    YORK_QUALIFICATION_COMMANDS,
    york_xor,
)
from adapters.york.swing_matrix_qualification import (
    YORK_CANDIDATE_HEAT_LOW_BOTH_22_5,
    YORK_CANDIDATE_HEAT_LOW_HORIZONTAL_22_5,
    YORK_QUALIFICATION_HEAT_LOW_OFF_22_5,
    YORK_QUALIFICATION_HEAT_LOW_VERTICAL_22_5,
    build_heat_22_5_low_swing_matrix_command,
)
from configuration import load_config
from direct_swing_manager import (
    DirectSwingManager,
    DirectSwingSafeStop,
    DirectSwingVerificationError,
)
from test_sprint_3111_temperature_boundary_qualification import FakeSocket


FRAMES = {
    "off": YORK_QUALIFICATION_HEAT_LOW_OFF_22_5,
    "vertical": YORK_QUALIFICATION_HEAT_LOW_VERTICAL_22_5,
    "both": YORK_CANDIDATE_HEAT_LOW_BOTH_22_5,
    "horizontal": YORK_CANDIDATE_HEAT_LOW_HORIZONTAL_22_5,
}
HASHES = {
    "off": "048b2814020e6119baa087f93eac0f6d980020b78bda74dbfa2b426a57a83601",
    "vertical": "b79c8ed1f0719823f5726d92823bffdf388e44dcfaa125dcdb1c57ad7cb3382f",
    "both": "9a8f9e2c9c720605ac3a33226eafb5903530218b79334f4ba14b606f40463700",
    "horizontal": "01b00ff14eda955457e35aedef38c71c63a473bc345a1a333088e56f8821c8da",
}
TRANSITIONS = (
    ("off", "vertical"),
    ("vertical", "both"),
    ("both", "horizontal"),
    ("horizontal", "off"),
)


def _state(swing: str, **changes):
    state = {
        "power": True,
        "mode": "heat",
        "temperature": 22.5,
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


def _state_frame(state):
    swing = {"off": 0x00, "horizontal": 0x20, "vertical": 0x40, "both": 0x60}[
        state["swing"]
    ]
    mode = {"cool": 0x01, "dry": 0x03, "heat": 0x04}[state["mode"]]
    fan = {"low": 0x10, "high": 0x30}[state["fan"]]
    whole = int(state["temperature"])
    frame = bytearray.fromhex(
        "BB0100030F01000000000000000000000060000000"
    )
    frame[7] = mode | (0x10 if state["power"] else 0) | (
        0x20 if state["display"] else 0
    )
    frame[8] = fan | (whole - 16)
    frame[9] = 0x02 if state["temperature"] != whole else 0
    frame[10] = swing
    frame[-1] = york_xor(frame[:-1])
    return bytes(frame)


def _manager(before, target, *, live_before=None, live_after=None):
    command = FRAMES[target]
    sock = FakeSocket(
        _state_frame(live_before or _state(before)),
        _state_frame(live_after or _state(target)),
        command,
    )

    def factory(host, port, mac, timeout, requested_swing):
        assert requested_swing == target
        return BroadlinkYorkSwingMatrixQualificationClient(
            host,
            port,
            mac,
            timeout,
            requested_swing,
            socket_factory=lambda *_args: sock,
        )

    config = load_config(Path("config.example.yml"))
    return DirectSwingManager(config, matrix_client_factory=factory), sock


@pytest.mark.parametrize("swing", tuple(FRAMES))
def test_alpha65_frames_are_exact_checksum_and_fingerprint_locked(swing):
    frame = build_heat_22_5_low_swing_matrix_command(swing)
    assert frame == FRAMES[swing]
    assert len(frame) == 31
    assert york_xor(frame) == 0
    assert hashlib.sha256(frame).hexdigest() == HASHES[swing]
    assert frame not in YORK_QUALIFICATION_COMMANDS


def test_matrix_changes_only_the_independently_qualified_axis_fields():
    assert FRAMES["off"][10:12] == bytes((0x02, 0x02))
    assert FRAMES["vertical"][10:12] == bytes((0x3A, 0x02))
    assert FRAMES["both"][10:12] == bytes((0x3A, 0x0A))
    assert FRAMES["horizontal"][10:12] == bytes((0x02, 0x0A))
    for frame in FRAMES.values():
        assert frame[8:10] == bytes((0x01, 0x09))


@pytest.mark.parametrize(("before", "target"), TRANSITIONS)
def test_each_matrix_step_has_fresh_guards_four_sends_and_nine_field_verification(
    before, target
):
    manager, sock = _manager(before, target)
    response = manager.command(target, _state(before))
    transaction = response["_transaction"]
    assert response["swing"] == target
    assert response["temperature"] == 22.5
    assert response["fan"] == "low"
    assert transaction["qualified_path"] == (
        "alpha65_heat_22_5_low_grouped_swing_matrix"
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
        _state("vertical", temperature=22.0),
        _state("vertical", mode="cool"),
        _state("vertical", fan="high"),
        _state("vertical", power=False),
        _state("vertical", display=False),
    ),
)
def test_nearby_unqualified_shapes_stop_before_socket(state):
    config = load_config(Path("config.example.yml"))

    def forbidden(*_args, **_kwargs):
        raise AssertionError("client created for an unqualified Alpha.65 state")

    manager = DirectSwingManager(
        config,
        client_factory=forbidden,
        axis_client_factory=forbidden,
        matrix_client_factory=forbidden,
    )
    with pytest.raises(DirectSwingSafeStop):
        manager.command("both", state)
    assert manager.last_udp_sends == 0


def test_fresh_pre_read_mismatch_stops_after_two_sends_without_write():
    manager, sock = _manager(
        "vertical", "both", live_before=_state("vertical", fan="high")
    )
    with pytest.raises(DirectSwingSafeStop, match="direct pre-read differs"):
        manager.command("both", _state("vertical"))
    assert manager.last_udp_sends == 2
    assert len(sock.sent) == 2


def test_post_read_mismatch_is_reported_without_retry():
    manager, sock = _manager(
        "both", "horizontal", live_after=_state("both")
    )
    with pytest.raises(DirectSwingVerificationError, match="swing"):
        manager.command("horizontal", _state("both"))
    assert manager.last_udp_sends == 4
    assert len(sock.sent) == 4


@pytest.mark.parametrize(
    ("before", "target"),
    (("off", "both"), ("vertical", "horizontal"), ("both", "off")),
)
def test_skipped_matrix_edges_remain_fail_closed(before, target):
    config = load_config(Path("config.example.yml"))

    def forbidden(*_args, **_kwargs):
        raise AssertionError("client created for a skipped Alpha.65 edge")

    manager = DirectSwingManager(
        config,
        client_factory=forbidden,
        axis_client_factory=forbidden,
        matrix_client_factory=forbidden,
    )
    with pytest.raises(DirectSwingSafeStop):
        manager.command(target, _state(before))
    assert manager.last_udp_sends == 0
