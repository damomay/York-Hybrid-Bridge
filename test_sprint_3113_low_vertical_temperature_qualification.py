from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

import pytest

from adapters.york import (
    BroadlinkYorkOneShotWriteClient,
    build_captured_heat_low_vertical_temperature_command,
    validate_captured_heat_low_vertical_temperature_command,
)
from adapters.york.broadlink import AUTH_COMMAND, QUERY_COMMAND, york_xor
from adapters.york.decoder import YorkPacketDecoder
from direct_temperature_manager import (
    DirectTemperatureManager,
    DirectTemperatureSafeStop,
)
from test_sprint_3111_temperature_boundary_qualification import (
    FakeSocket,
    _state_frame,
)
import york_low_vertical_temperature_qualification as qualification


CAPTURE_FIXTURES = {
    24: (
        "BB0001031901004401073A00000000000000000000000000000000000000D9",
        "021edcaff53f8f41dfef46fccd8cc38a3c58d86143ec6b0a1bfa3bf13e4a367d",
    ),
    25: (
        "BB0001031901004401063A00000000000000000000000000000000000000D8",
        "1853cd22c2955c69fd892ef4e8d0e15ecb1bdb1f07c9f00ba96290067630539b",
    ),
}


@pytest.mark.parametrize("target_temperature", (24, 25))
def test_low_vertical_frames_match_exact_relay_captures(target_temperature: int):
    expected_hex, expected_hash = CAPTURE_FIXTURES[target_temperature]
    generated = build_captured_heat_low_vertical_temperature_command(
        target_temperature
    )
    assert generated.hex().upper() == expected_hex
    assert hashlib.sha256(generated).hexdigest() == expected_hash
    assert york_xor(generated) == 0
    assert (
        validate_captured_heat_low_vertical_temperature_command(generated)
        == float(target_temperature)
    )


@pytest.mark.parametrize("target_temperature", (15, 24.25, 32))
def test_low_vertical_generator_rejects_non_whole_or_out_of_range_target(
    target_temperature: float,
):
    with pytest.raises(Exception):
        build_captured_heat_low_vertical_temperature_command(target_temperature)


def test_alpha42_manifest_matches_runtime_cases_and_capture_evidence():
    manifest = json.loads(
        Path(
            "protocols/york/qualification/"
            "alpha42_heat_low_vertical_temperature.json"
        ).read_text(encoding="utf-8")
    )
    assert manifest["version"] == "1.0.0-alpha.42"
    assert manifest["encoding"]["constant_byte_10"] == "3A"
    assert [item["target_temperature"] for item in manifest["captures"]] == [
        24,
        25,
    ]
    for item in manifest["captures"]:
        expected_hex, expected_hash = CAPTURE_FIXTURES[
            item["target_temperature"]
        ]
        assert item["frame_hex"] == expected_hex
        assert item["sha256"] == expected_hash
        assert item["physical_result"] == "success"
        assert item["fan_preserved"] == "low"
        assert item["swing_preserved"] == "vertical"
    assert [item["name"] for item in manifest["live_cases"]] == list(
        qualification.CASES
    )
    for item in manifest["live_cases"]:
        case = qualification.CASES[item["name"]]
        assert item["before_temperature"] == case.before_temperature
        assert item["target_temperature"] == case.target_temperature
        assert item["confirmation_token"] == case.confirmation_token


@pytest.mark.parametrize("case_name", tuple(qualification.CASES))
def test_each_low_vertical_case_has_one_write_and_four_sends(case_name: str):
    case = qualification.CASES[case_name]
    sock = FakeSocket(
        _state_frame(case.before),
        _state_frame(case.after),
        case.command,
    )
    decoder = YorkPacketDecoder()
    client = BroadlinkYorkOneShotWriteClient(
        "192.0.2.42",
        80,
        "02:00:00:00:00:42",
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
        case.after,
        decoder.decode_state(result.after_frame).to_dict(),
    )["result"] == "MATCH"
    assert [packet[0x26] for packet in sock.sent] == [
        AUTH_COMMAND,
        QUERY_COMMAND,
        QUERY_COMMAND,
        QUERY_COMMAND,
    ]


@pytest.mark.parametrize("case_name", tuple(qualification.CASES))
def test_low_vertical_precondition_failure_sends_zero_writes(case_name: str):
    case = qualification.CASES[case_name]
    sock = FakeSocket(
        _state_frame(case.before),
        _state_frame(case.after),
        case.command,
    )
    client = BroadlinkYorkOneShotWriteClient(
        "192.0.2.42",
        80,
        "02:00:00:00:00:42",
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


def _enabled_config(tmp_path: Path) -> Path:
    config = tmp_path / "config.yml"
    config.write_text(
        Path("config.example.yml")
        .read_text(encoding="utf-8")
        .replace("direct_read:\n  enabled: false", "direct_read:\n  enabled: true"),
        encoding="utf-8",
    )
    return config


def test_alpha42_validation_mode_opens_no_socket(
    tmp_path: Path,
    monkeypatch,
    capsys,
):
    config = _enabled_config(tmp_path)

    def forbidden_socket(*_args, **_kwargs):
        raise AssertionError("validation mode opened a socket")

    monkeypatch.setattr("adapters.york.broadlink.socket.socket", forbidden_socket)
    monkeypatch.setattr(sys, "argv", ["low-vertical-tool", str(config)])
    assert qualification.main() == 0
    output = capsys.readouterr().out
    assert output.count("Generator/capture match: exact (31/31 bytes)") == 2
    assert "Capture-qualified targets: 24 and 25 °C only" in output
    assert "no socket opened and no packet transmitted" in output


def test_one_shot_qualification_tool_is_not_imported_by_normal_control():
    source = Path("direct_temperature_manager.py").read_text(encoding="utf-8")
    assert "york_low_vertical_temperature_qualification" not in source
