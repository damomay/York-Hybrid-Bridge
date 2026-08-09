from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

import pytest

from adapters.york import (
    BroadlinkYorkLowVerticalTemperatureWriteClient,
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
import york_low_vertical_temperature_range_qualification as qualification


CAPTURE_ANCHORS = {
    24: (
        "BB0001031901004401073A00000000000000000000000000000000000000D9",
        "021edcaff53f8f41dfef46fccd8cc38a3c58d86143ec6b0a1bfa3bf13e4a367d",
    ),
    25: (
        "BB0001031901004401063A00000000000000000000000000000000000000D8",
        "1853cd22c2955c69fd892ef4e8d0e15ecb1bdb1f07c9f00ba96290067630539b",
    ),
}


@pytest.mark.parametrize("target_temperature", range(16, 32))
def test_parameterised_range_is_canonical(target_temperature: int):
    command = build_captured_heat_low_vertical_temperature_command(
        target_temperature
    )
    assert len(command) == 31
    assert command[:9] == bytes.fromhex("BB0001031901004401")
    assert command[9] == 31 - target_temperature
    assert command[10] == 0x3A
    assert command[11:-1] == bytes(19)
    assert york_xor(command) == 0
    assert (
        validate_captured_heat_low_vertical_temperature_command(command)
        == float(target_temperature)
    )


@pytest.mark.parametrize("target_temperature", (24, 25))
def test_parameterised_generator_preserves_exact_alpha42_anchors(
    target_temperature: int,
):
    expected_hex, expected_hash = CAPTURE_ANCHORS[target_temperature]
    command = build_captured_heat_low_vertical_temperature_command(
        target_temperature
    )
    assert command.hex().upper() == expected_hex
    assert hashlib.sha256(command).hexdigest() == expected_hash


@pytest.mark.parametrize("target_temperature", (None, "warm", 15, 16.25, 32))
def test_parameterised_generator_rejects_invalid_targets(target_temperature):
    with pytest.raises(Exception):
        build_captured_heat_low_vertical_temperature_command(target_temperature)


def test_alpha44_manifest_matches_runtime_boundary_and_cases():
    manifest = json.loads(
        Path(
            "protocols/york/qualification/"
            "alpha44_heat_low_vertical_temperature_range.json"
        ).read_text(encoding="utf-8")
    )
    assert manifest["version"] == "1.0.0-alpha.44"
    assert manifest["encoding"]["generated_range_celsius"] == [16, 31]
    assert manifest["encoding"]["generated_frame_count"] == 16
    assert manifest["encoding"]["constant_byte_10"] == "3A"
    assert manifest["existing_physical_evidence_celsius"] == [24, 25, 26]
    for anchor in manifest["exact_capture_anchors"]:
        expected_hex, expected_hash = CAPTURE_ANCHORS[
            anchor["target_temperature"]
        ]
        assert anchor["frame_hex"] == expected_hex
        assert anchor["sha256"] == expected_hash
    assert [item["name"] for item in manifest["live_cases"]] == list(
        qualification.CASES
    )


@pytest.mark.parametrize("case_name", tuple(qualification.CASES))
def test_each_alpha44_case_has_one_write_and_four_sends(case_name: str):
    case = qualification.CASES[case_name]
    sock = FakeSocket(
        _state_frame(case.before),
        _state_frame(case.after),
        case.command,
    )
    decoder = YorkPacketDecoder()
    client = BroadlinkYorkLowVerticalTemperatureWriteClient(
        "192.0.2.44",
        80,
        "02:00:00:00:00:44",
        3,
        case.target_temperature,
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
def test_alpha44_precondition_failure_sends_zero_writes(case_name: str):
    case = qualification.CASES[case_name]
    sock = FakeSocket(
        _state_frame(case.before),
        _state_frame(case.after),
        case.command,
    )
    client = BroadlinkYorkLowVerticalTemperatureWriteClient(
        "192.0.2.44",
        80,
        "02:00:00:00:00:44",
        3,
        case.target_temperature,
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


def test_alpha44_validation_mode_opens_no_socket(tmp_path, monkeypatch, capsys):
    config = _enabled_config(tmp_path)

    def forbidden_socket(*_args, **_kwargs):
        raise AssertionError("validation mode opened a socket")

    monkeypatch.setattr("adapters.york.broadlink.socket.socket", forbidden_socket)
    monkeypatch.setattr(
        sys,
        "argv",
        ["low-vertical-range-tool", str(config)],
    )
    assert qualification.main() == 0
    output = capsys.readouterr().out
    assert "16 to 31 °C inclusive (16/16 frames)" in output
    assert "Exact Alpha.42 capture matches: 24 and 25 °C" in output
    assert "no socket opened and no packet transmitted" in output


def _low_vertical_state(temperature: float) -> dict[str, object]:
    return {
        "power": True,
        "mode": "heat",
        "temperature": float(temperature),
        "fan": "low",
        "swing": "vertical",
        "turbo": False,
        "eco": False,
        "health": False,
        "display": True,
    }


class PathConfig:
    direct_host = "192.0.2.44"
    direct_port = 80
    direct_mac = "02:00:00:00:00:44"
    direct_connect_timeout = 3
    direct_control_post_write_delay_seconds = 0


def test_alpha44_tool_remains_separate_from_normal_control():
    source = Path("direct_temperature_manager.py").read_text(encoding="utf-8")
    assert "york_low_vertical_temperature_range_qualification" not in source
