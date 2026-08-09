from __future__ import annotations

import hashlib

import pytest

from adapters.york import (
    BroadlinkYorkOneShotWriteClient,
    YORK_QUALIFICATION_DRY_LOW_BOTH_21,
    YORK_QUALIFICATION_DRY_LOW_VERTICAL_21,
    YORK_REJECTED_ALPHA49_HEAT_LOW_HORIZONTAL_21_5,
)
from adapters.york.broadlink import YORK_QUALIFICATION_COMMANDS, york_xor
from adapters.york.swing_command import QUALIFIED_SWING_MODES
from test_sprint_3111_temperature_boundary_qualification import (
    FakeSocket,
)
from york_dry_horizontal_axis_qualification import CASES, main


def _state(swing: str) -> dict[str, object]:
    return {
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


def _state_frame(state: dict[str, object]) -> bytes:
    mode = {"cool": 0x01, "dry": 0x03, "heat": 0x04}[str(state["mode"])]
    fan = {"low": 0x10, "high": 0x30}[str(state["fan"])]
    swing = {
        "off": 0x00,
        "horizontal": 0x20,
        "vertical": 0x40,
        "both": 0x60,
    }[str(state["swing"])]
    temperature = float(state["temperature"])
    whole = int(temperature)
    frame = bytearray.fromhex(
        "BB 01 00 03 0F 01 00 00 00 00 00 00 00 00 00 00 00 60 00 00 00"
    )
    frame[7] = 0x20 | mode | (0x10 if state["power"] else 0)
    frame[8] = fan | (whole - 16)
    frame[9] = 0x02 if temperature != whole else 0
    frame[10] = swing
    frame[-1] = york_xor(frame[:-1])
    return bytes(frame)


def test_exact_independent_axis_and_return_frames_are_locked():
    assert YORK_QUALIFICATION_DRY_LOW_BOTH_21.hex().upper() == (
        "BB00010319010044020A3A08000000000000000000000000000000000000DF"
    )
    assert YORK_QUALIFICATION_DRY_LOW_VERTICAL_21.hex().upper() == (
        "BB00010319010044020A3A00000000000000000000000000000000000000D7"
    )
    assert YORK_QUALIFICATION_DRY_LOW_BOTH_21[8] == 0x02
    assert YORK_QUALIFICATION_DRY_LOW_BOTH_21[10] == 0x3A
    assert YORK_QUALIFICATION_DRY_LOW_BOTH_21[11] == 0x08
    assert YORK_QUALIFICATION_DRY_LOW_VERTICAL_21[8] == 0x02
    assert YORK_QUALIFICATION_DRY_LOW_VERTICAL_21[10] == 0x3A
    assert YORK_QUALIFICATION_DRY_LOW_VERTICAL_21[11] == 0x00


@pytest.mark.parametrize("case", CASES.values(), ids=lambda item: item.name)
def test_cases_have_valid_length_xor_fingerprint_and_allowlist(case):
    assert len(case.command) == 31
    assert york_xor(case.command) == 0
    assert hashlib.sha256(case.command).hexdigest() == case.expected_sha256
    assert case.command in YORK_QUALIFICATION_COMMANDS


@pytest.mark.parametrize(
    ("before_swing", "target_swing", "command"),
    [
        (
            "vertical",
            "both",
            YORK_QUALIFICATION_DRY_LOW_BOTH_21,
        ),
        (
            "both",
            "vertical",
            YORK_QUALIFICATION_DRY_LOW_VERTICAL_21,
        ),
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
        "192.0.2.49",
        80,
        "02:00:00:00:00:49",
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
        [
            "york_dry_horizontal_axis_qualification.py",
            "config.example.yml",
        ],
    )

    assert main() == 0
    output = capsys.readouterr().out
    assert "VALIDATION PASSED" in output
    assert "no socket opened and no packet transmitted" in output
    assert "Normal Home Assistant Horizontal/Both routing: Relay v2" in output


def test_wrong_token_stops_before_client_creation(monkeypatch):
    monkeypatch.setattr(
        "sys.argv",
        [
            "york_dry_horizontal_axis_qualification.py",
            "config.example.yml",
            "--case",
            "vertical-to-both",
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


def test_qualification_tools_are_not_copied_into_alpha52_container():
    dockerfile = __import__("pathlib").Path(__file__).with_name("Dockerfile").read_text()
    assert "york_dry_horizontal_axis_qualification.py" not in dockerfile
    assert "york_horizontal_axis_qualification.py" not in dockerfile
