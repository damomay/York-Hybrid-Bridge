from __future__ import annotations

import hashlib

import pytest

from adapters.york import (
    BroadlinkYorkOneShotWriteClient,
    YORK_QUALIFICATION_HEAT_LOW_HORIZONTAL_21_5,
    YORK_QUALIFICATION_HEAT_LOW_OFF_21_5,
    YORK_REJECTED_ALPHA49_HEAT_LOW_HORIZONTAL_21_5,
)
from adapters.york.broadlink import YORK_QUALIFICATION_COMMANDS, york_xor
from adapters.york.swing_command import QUALIFIED_SWING_MODES
from test_sprint_3111_temperature_boundary_qualification import FakeSocket
from york_heat_horizontal_axis_qualification import CASES, main


def _state(swing: str) -> dict[str, object]:
    return {
        "power": True,
        "mode": "heat",
        "temperature": 21.5,
        "indoor_temperature": 21,
        "fan": "low",
        "swing": swing,
        "turbo": False,
        "eco": False,
        "health": False,
        "display": True,
    }


def _state_frame(state: dict[str, object]) -> bytes:
    swing = {
        "off": 0x00,
        "horizontal": 0x20,
        "vertical": 0x40,
        "both": 0x60,
    }[str(state["swing"])]
    frame = bytearray.fromhex(
        "BB 01 00 03 0F 01 00 00 00 00 00 00 00 00 00 00 00 60 00 00 00"
    )
    frame[7] = 0x20 | 0x04 | 0x10
    frame[8] = 0x10 | (21 - 16)
    frame[9] = 0x02
    frame[10] = swing
    frame[-1] = york_xor(frame[:-1])
    return bytes(frame)


def test_exact_horizontal_only_and_off_frames_are_locked():
    assert YORK_QUALIFICATION_HEAT_LOW_HORIZONTAL_21_5.hex().upper() == (
        "BB00010319010044010A020A000000000000000000000000000000000000E6"
    )
    assert YORK_QUALIFICATION_HEAT_LOW_OFF_21_5.hex().upper() == (
        "BB00010319010044010A0202000000000000000000000000000000000000EE"
    )
    assert YORK_QUALIFICATION_HEAT_LOW_HORIZONTAL_21_5[10] == 0x02
    assert YORK_QUALIFICATION_HEAT_LOW_HORIZONTAL_21_5[11] == 0x0A
    assert YORK_QUALIFICATION_HEAT_LOW_OFF_21_5[10] == 0x02
    assert YORK_QUALIFICATION_HEAT_LOW_OFF_21_5[11] == 0x02


@pytest.mark.parametrize("case", CASES.values(), ids=lambda item: item.name)
def test_cases_have_valid_length_xor_fingerprint_and_allowlist(case):
    assert len(case.command) == 31
    assert york_xor(case.command) == 0
    assert hashlib.sha256(case.command).hexdigest() == case.expected_sha256
    assert case.command in YORK_QUALIFICATION_COMMANDS


@pytest.mark.parametrize(
    ("before_swing", "target_swing", "command"),
    [
        ("off", "horizontal", YORK_QUALIFICATION_HEAT_LOW_HORIZONTAL_21_5),
        ("horizontal", "off", YORK_QUALIFICATION_HEAT_LOW_OFF_21_5),
    ],
)
def test_one_shot_client_uses_four_sends_and_one_exact_write(
    before_swing,
    target_swing,
    command,
):
    sock = FakeSocket(
        _state_frame(_state(before_swing)),
        _state_frame(_state(target_swing)),
        command,
    )
    client = BroadlinkYorkOneShotWriteClient(
        "192.0.2.53",
        80,
        "02:00:00:00:00:53",
        1,
        command,
        socket_factory=lambda *_args: sock,
    )
    approved = []

    result = client.execute(
        lambda frame: approved.append(frame),
        post_write_delay_seconds=0,
    )

    assert approved == [result.before_frame]
    assert result.send_count == 4
    assert client.last_send_count == 4
    assert len(sock.sent) == 4


def test_offline_validation_opens_no_socket(monkeypatch, capsys):
    monkeypatch.setattr(
        "sys.argv",
        ["york_heat_horizontal_axis_qualification.py", "config.example.yml"],
    )

    assert main() == 0
    output = capsys.readouterr().out
    assert "VALIDATION PASSED" in output
    assert "no socket opened and no packet transmitted" in output
    assert "Normal Home Assistant Off/Horizontal routing: Relay v2" in output


def test_wrong_token_stops_before_client_creation(monkeypatch):
    monkeypatch.setattr(
        "sys.argv",
        [
            "york_heat_horizontal_axis_qualification.py",
            "config.example.yml",
            "--case",
            "off-to-horizontal",
            "--execute",
            "--confirm",
            "WRONG",
        ],
    )

    with pytest.raises(SystemExit, match="exact confirmation token"):
        main()


def test_normal_swing_manager_still_excludes_horizontal_and_both():
    assert QUALIFIED_SWING_MODES == ("off", "vertical")


def test_failed_alpha49_status_bit_candidate_is_not_allowlisted():
    assert YORK_REJECTED_ALPHA49_HEAT_LOW_HORIZONTAL_21_5.hex().upper() == (
        "BB00010319010044010A0222000000000000000000000000000000000000CE"
    )
    assert YORK_REJECTED_ALPHA49_HEAT_LOW_HORIZONTAL_21_5 not in (
        YORK_QUALIFICATION_COMMANDS
    )


def test_alpha53_horizontal_tool_is_removed_from_promoted_container():
    dockerfile = __import__("pathlib").Path(__file__).with_name("Dockerfile").read_text()
    assert "york_heat_horizontal_axis_qualification.py" not in dockerfile
    assert "york_dry_horizontal_axis_qualification.py" not in dockerfile
    assert "york_horizontal_axis_qualification.py" not in dockerfile
