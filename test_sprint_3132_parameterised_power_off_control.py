from __future__ import annotations

from pathlib import Path

import pytest

from adapters.york.broadlink import (
    YORK_QUALIFICATION_COMMANDS,
    YORK_QUALIFICATION_POWER_OFF,
    YORK_QUALIFICATION_POWER_OFF_HEAT,
    YorkOneShotWriteResult,
    york_xor,
)
from adapters.york.errors import YorkProtocolError
from adapters.york.power_off_command import (
    QUALIFIED_PARAMETERISED_POWER_OFF_COMMANDS,
    build_parameterised_power_off_command,
    validate_parameterised_power_off_command,
)
from adapters.york.power_on_command import build_parameterised_power_on_command
from configuration import load_config
from direct_power_manager import DirectPowerManager, DirectPowerSafeStop


BASELINE_ON = {
    "power": True,
    "mode": "heat",
    "temperature": 22.5,
    "fan": "low",
    "swing": "off",
    "turbo": False,
    "eco": False,
    "health": False,
    "display": True,
}
BASELINE_OFF = {**BASELINE_ON, "power": False}


def _state_frame(state: dict) -> bytes:
    mode = {"cool": 0x01, "heat": 0x04}[state["mode"]]
    fan = {"low": 0x10, "high": 0x30}[state["fan"]]
    swing = {"off": 0x00, "vertical": 0x40}[state["swing"]]
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


class FakeClient:
    def __init__(self, command: bytes, before: dict, after: dict) -> None:
        self.command = command
        self.before = before
        self.after = after
        self.last_send_count = 0

    def execute(self, approve_precondition, *, post_write_delay_seconds):
        assert post_write_delay_seconds == 2
        self.last_send_count = 2
        approve_precondition(_state_frame(self.before))
        self.last_send_count = 4
        return YorkOneShotWriteResult(
            before_frame=_state_frame(self.before),
            command_reply_frame=_state_frame(self.after),
            after_frame=_state_frame(self.after),
            send_count=4,
            session_id=0x12345678,
        )


def _manager(before=BASELINE_ON, after=BASELINE_OFF):
    config = load_config(Path("config.example.yml"))
    clients = []

    def factory(_host, _port, _mac, _timeout, command):
        client = FakeClient(command, before, after)
        clients.append(client)
        return client

    return DirectPowerManager(config, client_factory=factory), clients


def test_parameterised_off_reproduces_captured_heat_high_vertical_anchor():
    frame = build_parameterised_power_off_command(
        "heat", 25.0, "high", "vertical"
    )

    assert frame == YORK_QUALIFICATION_POWER_OFF_HEAT
    assert frame in YORK_QUALIFICATION_COMMANDS
    assert frame in QUALIFIED_PARAMETERISED_POWER_OFF_COMMANDS
    assert york_xor(frame) == 0


def test_captured_cool_anchor_proves_same_power_bit_without_expanding_shape():
    on_frame = build_parameterised_power_on_command(
        "cool", 25.0, "low", "off"
    )

    assert YORK_QUALIFICATION_POWER_OFF[7] == 0x40
    assert YORK_QUALIFICATION_POWER_OFF_HEAT[7] == 0x40
    assert on_frame[7] == 0x44
    with pytest.raises(YorkProtocolError, match="supports only"):
        build_parameterised_power_off_command(
            "cool", 25.0, "high", "vertical"
        )


@pytest.mark.parametrize(
    ("mode", "temperature", "fan", "swing"),
    [
        ("heat", 16.0, "low", "off"),
        ("heat", 22.5, "low", "off"),
        ("cool", 30.0, "low", "off"),
        ("heat", 31.0, "low", "vertical"),
        ("heat", 25.5, "high", "vertical"),
    ],
)
def test_off_frame_changes_only_proven_power_bit_and_checksum(
    mode, temperature, fan, swing
):
    on_frame = build_parameterised_power_on_command(
        mode, temperature, fan, swing
    )
    off_frame = build_parameterised_power_off_command(
        mode, temperature, fan, swing
    )

    validate_parameterised_power_off_command(
        off_frame, mode, temperature, fan, swing
    )
    assert len(off_frame) == 31
    assert off_frame[7] == 0x40
    assert off_frame[:7] == on_frame[:7]
    assert off_frame[8:-1] == on_frame[8:-1]
    assert york_xor(off_frame) == 0
    assert off_frame in QUALIFIED_PARAMETERISED_POWER_OFF_COMMANDS


def test_verified_half_degree_baseline_powers_off_and_preserves_fields():
    manager, clients = _manager()

    response = manager.command({"power": False}, dict(BASELINE_ON))

    assert len(clients) == 1
    assert clients[0].command == build_parameterised_power_off_command(
        "heat", 22.5, "low", "off"
    )
    assert clients[0].command not in YORK_QUALIFICATION_COMMANDS
    assert response == {**BASELINE_OFF, "_transaction": response["_transaction"]}
    transaction = response["_transaction"]
    assert transaction["case"] == "parameterised-off-heat-low-off"
    assert transaction["before"] == BASELINE_ON
    assert transaction["after"] == BASELINE_OFF
    assert transaction["verification"] == {
        "success": True,
        "matched_fields": 9,
        "compared_fields": 9,
    }
    assert transaction["udp_sends"] == 4
    assert transaction["automatic_retries"] == 0
    assert transaction["fallback_used"] is False


@pytest.mark.parametrize(
    "changed",
    [
        {"fan": "auto"},
        {"swing": "horizontal"},
        {"eco": True},
        {"display": False},
        {"mode": "dry"},
    ],
)
def test_unqualified_on_state_safe_stops_before_client_creation(changed):
    config = load_config(Path("config.example.yml"))

    def forbidden_client(*_args, **_kwargs):
        raise AssertionError("client created for an unqualified power-off state")

    manager = DirectPowerManager(config, client_factory=forbidden_client)
    state = {**BASELINE_ON, **changed}

    with pytest.raises(
        DirectPowerSafeStop,
        match="authoritative direct state|qualified power shape",
    ):
        manager.command({"power": False}, state)


def test_live_pre_read_must_match_authoritative_state_before_off_write():
    live_before = {**BASELINE_ON, "temperature": 23.0}
    manager, clients = _manager(before=live_before)

    with pytest.raises(
        DirectPowerSafeStop,
        match="direct pre-read differs from authoritative direct state",
    ):
        manager.command({"power": False}, dict(BASELINE_ON))

    assert clients[0].last_send_count == 2
    assert manager.last_udp_sends == 2


def test_noncanonical_off_frame_is_rejected():
    frame = bytearray(
        build_parameterised_power_off_command("heat", 22.5, "low", "off")
    )
    frame[8] ^= 0x01
    frame[-1] = york_xor(frame[:-1])

    with pytest.raises(YorkProtocolError, match="non-canonical"):
        validate_parameterised_power_off_command(
            bytes(frame), "heat", 22.5, "low", "off"
        )
