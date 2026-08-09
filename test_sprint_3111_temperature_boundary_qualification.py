from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

import pytest

from adapters.york import (
    BroadlinkYorkOneShotWriteClient,
    MAX_QUALIFIED_TEMPERATURE,
    MIN_QUALIFIED_TEMPERATURE,
    build_captured_heat_high_vertical_temperature_command,
    validate_captured_heat_high_vertical_temperature_command,
)
from adapters.york.broadlink import AUTH_COMMAND, QUERY_COMMAND, york_xor
from adapters.york.decoder import YorkPacketDecoder
from test_sprint_313_power_on_heat_qualification import FakeSocket, _state_frame
import york_temperature_one_shot_qualification as qualification


BOUNDARY_CAPTURE_FIXTURES = {
    16: (
        "BB00010319010044010F3D00000000000000000000000000000000000000D6",
        "7304bb1ebf387eff98ebd61eba08b3f71f64b41651b7a6cc817dcc9c3dda2012",
    ),
    17: (
        "BB00010319010044010E3D00000000000000000000000000000000000000D7",
        "fa8dc0f70af8ceef190ca211ca4ffc7fd06658486618c2285cbf1e69a3c47f3d",
    ),
    30: (
        "BB0001031901004401013D00000000000000000000000000000000000000D8",
        "5dd67ed0617c79ddd553e1f1306c3d7daafd8955e8fb66dc9ad23af534d725e2",
    ),
    31: (
        "BB0001031901004401003D00000000000000000000000000000000000000D9",
        "b1a20475a10b9dd5181a4fac9eb66126fe2416545921944cef8df58324d33981",
    ),
}


@pytest.mark.parametrize("target_temperature", tuple(BOUNDARY_CAPTURE_FIXTURES))
def test_boundary_frames_match_exact_relay_captures(target_temperature: int):
    expected_hex, expected_hash = BOUNDARY_CAPTURE_FIXTURES[target_temperature]
    generated = build_captured_heat_high_vertical_temperature_command(
        target_temperature
    )
    assert generated.hex().upper() == expected_hex
    assert hashlib.sha256(generated).hexdigest() == expected_hash
    assert york_xor(generated) == 0
    assert (
        validate_captured_heat_high_vertical_temperature_command(generated)
        == float(target_temperature)
    )


def test_complete_supported_range_is_canonical_and_checksum_valid():
    assert MIN_QUALIFIED_TEMPERATURE == 16
    assert MAX_QUALIFIED_TEMPERATURE == 31
    for temperature in range(16, 32):
        frame = build_captured_heat_high_vertical_temperature_command(temperature)
        assert len(frame) == 31
        assert frame[9] == 31 - temperature
        assert frame[10] == 0x3D
        assert york_xor(frame) == 0
        assert (
            validate_captured_heat_high_vertical_temperature_command(frame)
            == float(temperature)
        )


def test_alpha40_manifest_matches_capture_and_runtime_cases():
    manifest = json.loads(
        Path(
            "protocols/york/qualification/"
            "alpha40_heat_temperature_boundaries.json"
        ).read_text(encoding="utf-8")
    )
    assert manifest["version"] == "1.0.0-alpha.40"
    assert manifest["supported_range_celsius"] == {
        "minimum": 16,
        "maximum": 31,
        "increment": 1,
    }
    assert manifest["encoding"]["formula"] == (
        "31 - whole-degree Celsius setpoint"
    )
    assert [item["target_temperature"] for item in manifest["captures"]] == [
        16,
        17,
        31,
        30,
    ]
    for item in manifest["captures"]:
        expected_hex, expected_hash = BOUNDARY_CAPTURE_FIXTURES[
            item["target_temperature"]
        ]
        assert item["frame_hex"] == expected_hex
        assert item["sha256"] == expected_hash
    assert [item["name"] for item in manifest["live_cases"]] == list(
        qualification.CASES
    )
    for item in manifest["live_cases"]:
        case = qualification.CASES[item["name"]]
        assert item["before_temperature"] == case.before_temperature
        assert item["target_temperature"] == case.target_temperature
        assert bytes.fromhex(item["frame_hex"]) == case.command
        assert item["sha256"] == case.expected_sha256


@pytest.mark.parametrize("case_name", tuple(qualification.CASES))
def test_each_boundary_case_has_one_write_and_four_sends(case_name: str):
    case = qualification.CASES[case_name]
    sock = FakeSocket(
        _state_frame(case.before),
        _state_frame(case.after),
        case.command,
    )
    decoder = YorkPacketDecoder()
    client = BroadlinkYorkOneShotWriteClient(
        "192.0.2.40",
        80,
        "02:00:00:00:00:40",
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
def test_boundary_precondition_failure_sends_zero_writes(case_name: str):
    case = qualification.CASES[case_name]
    sock = FakeSocket(
        _state_frame(case.before),
        _state_frame(case.after),
        case.command,
    )
    client = BroadlinkYorkOneShotWriteClient(
        "192.0.2.40",
        80,
        "02:00:00:00:00:40",
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


def test_alpha40_validation_mode_opens_no_socket(
    tmp_path: Path,
    monkeypatch,
    capsys,
):
    config = _enabled_config(tmp_path)

    def forbidden_socket(*_args, **_kwargs):
        raise AssertionError("validation mode opened a socket")

    monkeypatch.setattr("adapters.york.broadlink.socket.socket", forbidden_socket)
    monkeypatch.setattr(sys, "argv", ["temperature-tool", str(config)])
    assert qualification.main() == 0
    output = capsys.readouterr().out
    assert output.count("Generator/capture match: exact (31/31 bytes)") == 2
    assert "Qualified whole-degree range: 16 to 31 °C inclusive" in output
    assert "no socket opened and no packet transmitted" in output


def test_alpha40_qualification_remains_separate_from_normal_control():
    root = Path(__file__).parent
    for name in (
        "bridge.py",
        "mqtt_manager.py",
        "direct_power_manager.py",
        "direct_temperature_manager.py",
    ):
        source = (root / name).read_text(encoding="utf-8")
        assert "york_temperature_one_shot_qualification" not in source
