from __future__ import annotations

from pathlib import Path

import pytest

from adapters.york.broadlink import (
    YORK_QUALIFICATION_COMMANDS,
    YORK_QUALIFICATION_HEAT_LOW_OFF_21_5,
    YorkOneShotWriteResult,
    york_xor,
)
from adapters.york.power_on_command import (
    QUALIFIED_PARAMETERISED_POWER_ON_COMMANDS,
    build_parameterised_power_on_command,
    validate_parameterised_power_on_command,
)
from configuration import load_config
from direct_power_manager import DirectPowerManager, DirectPowerSafeStop


BASELINE_OFF = {
    "power": False,
    "mode": "heat",
    "temperature": 21.5,
    "fan": "low",
    "swing": "off",
    "turbo": False,
    "eco": False,
    "health": False,
    "display": True,
}
BASELINE_ON = {**BASELINE_OFF, "power": True}


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


def _manager(before=BASELINE_OFF, after=BASELINE_ON):
    config = load_config(Path("config.example.yml"))
    clients = []

    def factory(_host, _port, _mac, _timeout, command):
        client = FakeClient(command, before, after)
        clients.append(client)
        return client

    return DirectPowerManager(config, client_factory=factory), clients


def test_observed_off_heat_21_5_low_off_frame_is_existing_capture():
    frame = build_parameterised_power_on_command("heat", 21.5, "low", "off")

    assert frame == YORK_QUALIFICATION_HEAT_LOW_OFF_21_5
    assert frame in YORK_QUALIFICATION_COMMANDS
    assert frame in QUALIFIED_PARAMETERISED_POWER_ON_COMMANDS
    assert york_xor(frame) == 0
    validate_parameterised_power_on_command(
        frame, "heat", 21.5, "low", "off"
    )


@pytest.mark.parametrize(
    ("mode", "temperature", "fan", "swing"),
    [
        ("heat", 16.0, "low", "off"),
        ("heat", 21.5, "low", "off"),
        ("cool", 30.0, "low", "off"),
        ("heat", 31.0, "low", "vertical"),
        ("heat", 25.5, "high", "vertical"),
    ],
)
def test_every_enabled_shape_builds_a_canonical_allowlisted_frame(
    mode, temperature, fan, swing
):
    frame = build_parameterised_power_on_command(mode, temperature, fan, swing)

    validate_parameterised_power_on_command(
        frame, mode, temperature, fan, swing
    )
    assert len(frame) == 31
    assert frame[7] == 0x44
    assert york_xor(frame) == 0
    assert frame in QUALIFIED_PARAMETERISED_POWER_ON_COMMANDS


def test_observed_off_baseline_powers_on_and_preserves_every_stored_field():
    manager, clients = _manager()

    response = manager.command(
        {"power": True, "mode": "heat"},
        dict(BASELINE_OFF),
    )

    assert len(clients) == 1
    assert clients[0].command == YORK_QUALIFICATION_HEAT_LOW_OFF_21_5
    assert response == {
        **BASELINE_ON,
        "_transaction": response["_transaction"],
    }
    assert response["_transaction"]["case"] == (
        "parameterised-on-heat-low-off"
    )
    assert response["_transaction"]["before"] == BASELINE_OFF
    assert response["_transaction"]["after"] == BASELINE_ON
    assert response["_transaction"]["verification"] == {
        "success": True,
        "matched_fields": 9,
        "compared_fields": 9,
    }
    assert response["_transaction"]["udp_sends"] == 4
    assert response["_transaction"]["automatic_retries"] == 0
    assert response["_transaction"]["fallback_used"] is False


@pytest.mark.parametrize(
    "changed",
    [
        {"fan": "auto"},
        {"swing": "horizontal"},
        {"eco": True},
        {"display": False},
        {"temperature": 31.0},
    ],
)
def test_unqualified_off_state_safe_stops_before_client_creation(changed):
    config = load_config(Path("config.example.yml"))

    def forbidden_client(*_args, **_kwargs):
        raise AssertionError("client created for an unqualified power-on state")

    manager = DirectPowerManager(config, client_factory=forbidden_client)
    state = {**BASELINE_OFF, **changed}

    with pytest.raises(
        DirectPowerSafeStop,
        match="authoritative direct state|qualified power shape",
    ):
        manager.command({"power": True, "mode": "heat"}, state)


def test_live_pre_read_must_still_match_authoritative_state_before_write():
    live_before = {**BASELINE_OFF, "temperature": 22.0}
    manager, clients = _manager(before=live_before)

    with pytest.raises(
        DirectPowerSafeStop,
        match="direct pre-read differs from authoritative direct state",
    ):
        manager.command(
            {"power": True, "mode": "heat"},
            dict(BASELINE_OFF),
        )

    assert clients[0].last_send_count == 2
    assert manager.last_udp_sends == 2
