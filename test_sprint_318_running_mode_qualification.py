from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

import pytest

from adapters.york import (
    BroadlinkYorkOneShotWriteClient,
    YORK_QUALIFICATION_POWER_ON_COOL,
    YORK_QUALIFICATION_POWER_ON_HEAT,
    YorkPacketDecoder,
)
from adapters.york.broadlink import AUTH_COMMAND, QUERY_COMMAND, york_xor
from test_sprint_313_power_on_heat_qualification import FakeSocket, _state_frame
import york_mode_one_shot_qualification as qualification


@pytest.mark.parametrize(
    ("case_name", "expected_hex", "expected_hash", "source"),
    [
        (
            "heat-to-cool",
            "BB0001031901004403063D00000000000000000000000000000000000000DD",
            "41fc632383cbbe62b9db91e018f9b9f73eaac3315e218439fa4e6f93c01e667c",
            "successful Relay v2 Heat to Cool transaction #4 "
            "(2026-07-30 12:18:56)",
        ),
        (
            "cool-to-heat",
            "BB0001031901004401063D00000000000000000000000000000000000000DF",
            "a499631892d2f17255351c7fd8ff2974532d508c01f1e589a49e49bd9a891515",
            "successful Relay v2 Cool to Heat transaction #5 "
            "(2026-07-30 12:19:46)",
        ),
    ],
)
def test_mode_frames_are_exact_captured_fixtures(
    case_name: str, expected_hex: str, expected_hash: str, source: str
):
    case = qualification.CASES[case_name]
    assert case.command.hex().upper() == expected_hex
    assert hashlib.sha256(case.command).hexdigest() == expected_hash
    assert york_xor(case.command) == 0
    assert case.source_reference == source
    qualification._validate_case(case)


def test_mode_frames_reuse_exact_previously_qualified_target_frames():
    assert (
        qualification.CASES["heat-to-cool"].command
        == YORK_QUALIFICATION_POWER_ON_COOL
    )
    assert (
        qualification.CASES["cool-to-heat"].command
        == YORK_QUALIFICATION_POWER_ON_HEAT
    )


def test_capture_manifest_matches_runtime_cases():
    manifest = json.loads(
        Path("protocols/york/qualification/alpha37_running_mode_changes.json")
        .read_text(encoding="utf-8")
    )
    assert manifest["version"] == "1.0.0-alpha.37"
    assert [item["name"] for item in manifest["cases"]] == list(
        qualification.CASES
    )
    for item in manifest["cases"]:
        case = qualification.CASES[item["name"]]
        assert bytes.fromhex(item["frame_hex"]) == case.command
        assert item["sha256"] == case.expected_sha256
        assert item["before"] == case.before
        assert item["after"] == case.after


@pytest.mark.parametrize("case_name", ["heat-to-cool", "cool-to-heat"])
def test_each_mode_case_has_one_write_and_four_sends(case_name: str):
    case = qualification.CASES[case_name]
    sock = FakeSocket(
        _state_frame(case.before),
        _state_frame(case.after),
        case.command,
    )
    decoder = YorkPacketDecoder()
    client = BroadlinkYorkOneShotWriteClient(
        "192.0.2.30",
        80,
        "02:00:00:00:00:30",
        3,
        case.command,
        socket_factory=lambda *_args: sock,
    )

    def approve(frame: bytes) -> None:
        observed = decoder.decode_state(frame).to_dict()
        assert qualification._compare(case.before, observed)["result"] == "MATCH"

    result = client.execute(approve, post_write_delay_seconds=0)
    assert result.send_count == 4
    assert qualification._compare(
        case.after, decoder.decode_state(result.after_frame).to_dict()
    )["result"] == "MATCH"
    assert [packet[0x26] for packet in sock.sent] == [
        AUTH_COMMAND,
        QUERY_COMMAND,
        QUERY_COMMAND,
        QUERY_COMMAND,
    ]


@pytest.mark.parametrize("case_name", ["heat-to-cool", "cool-to-heat"])
def test_precondition_failure_sends_zero_writes(case_name: str):
    case = qualification.CASES[case_name]
    sock = FakeSocket(
        _state_frame(case.before),
        _state_frame(case.after),
        case.command,
    )
    client = BroadlinkYorkOneShotWriteClient(
        "192.0.2.30",
        80,
        "02:00:00:00:00:30",
        3,
        case.command,
        socket_factory=lambda *_args: sock,
    )

    with pytest.raises(RuntimeError, match="mismatch"):
        client.execute(
            lambda _frame: (_ for _ in ()).throw(RuntimeError("mismatch")),
            post_write_delay_seconds=0,
        )
    assert client.last_send_count == 2
    assert len(sock.sent) == 2


def test_package_exposes_only_two_running_mode_cases():
    assert tuple(qualification.CASES) == ("heat-to-cool", "cool-to-heat")
    assert qualification.CASES["heat-to-cool"].before["power"] is True
    assert qualification.CASES["heat-to-cool"].before["mode"] == "heat"
    assert qualification.CASES["heat-to-cool"].after["mode"] == "cool"
    assert qualification.CASES["cool-to-heat"].before["power"] is True
    assert qualification.CASES["cool-to-heat"].before["mode"] == "cool"
    assert qualification.CASES["cool-to-heat"].after["mode"] == "heat"


def test_mode_tool_is_not_wired_into_normal_control():
    root = Path(__file__).parent
    for name in (
        "bridge.py",
        "mqtt_manager.py",
        "direct_power_manager.py",
        "direct_temperature_manager.py",
    ):
        source = (root / name).read_text(encoding="utf-8")
        assert "york_mode_one_shot_qualification" not in source


def _enabled_config(tmp_path: Path) -> Path:
    config = tmp_path / "config.yml"
    config.write_text(
        Path("config.example.yml")
        .read_text(encoding="utf-8")
        .replace("direct_read:\n  enabled: false", "direct_read:\n  enabled: true"),
        encoding="utf-8",
    )
    return config


def test_validation_mode_opens_no_socket(tmp_path: Path, monkeypatch, capsys):
    config = _enabled_config(tmp_path)

    def forbidden_socket(*_args, **_kwargs):
        raise AssertionError("validation mode opened a socket")

    monkeypatch.setattr("adapters.york.broadlink.socket.socket", forbidden_socket)
    monkeypatch.setattr(sys, "argv", ["mode-tool", str(config)])
    assert qualification.main() == 0
    output = capsys.readouterr().out
    assert "Mode Heat To Cool case:" in output
    assert "Mode Cool To Heat case:" in output
    assert output.count("Captured frame: exact (31/31 bytes)") == 2
    assert "transaction #4 (2026-07-30 12:18:56)" in output
    assert "transaction #5 (2026-07-30 12:19:46)" in output
    assert "no socket opened and no packet transmitted" in output


def test_execute_without_case_stops_before_socket(tmp_path: Path, monkeypatch):
    config = _enabled_config(tmp_path)

    def forbidden_socket(*_args, **_kwargs):
        raise AssertionError("missing case opened a socket")

    monkeypatch.setattr("adapters.york.broadlink.socket.socket", forbidden_socket)
    monkeypatch.setattr(sys, "argv", ["mode-tool", str(config), "--execute"])
    with pytest.raises(
        SystemExit,
        match="--case heat-to-cool or --case cool-to-heat",
    ):
        qualification.main()


def test_wrong_confirmation_stops_before_socket(tmp_path: Path, monkeypatch):
    config = _enabled_config(tmp_path)

    def forbidden_socket(*_args, **_kwargs):
        raise AssertionError("wrong confirmation opened a socket")

    monkeypatch.setattr("adapters.york.broadlink.socket.socket", forbidden_socket)
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "mode-tool",
            str(config),
            "--case",
            "heat-to-cool",
            "--execute",
            "--confirm",
            "WRONG",
        ],
    )
    with pytest.raises(SystemExit, match="exact confirmation token"):
        qualification.main()
