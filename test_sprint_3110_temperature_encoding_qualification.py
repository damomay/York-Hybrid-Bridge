from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

import pytest

from adapters.york import (
    BroadlinkYorkOneShotWriteClient,
    build_captured_heat_high_vertical_temperature_command,
    validate_captured_heat_high_vertical_temperature_command,
)
from adapters.york.broadlink import AUTH_COMMAND, QUERY_COMMAND, york_xor
from adapters.york.errors import YorkProtocolError
from adapters.york.decoder import YorkPacketDecoder
from test_sprint_313_power_on_heat_qualification import FakeSocket, _state_frame
import york_temperature_one_shot_qualification as qualification


@pytest.mark.parametrize(
    ("target_temperature", "expected_hex", "expected_hash"),
    [
        (
            24.0,
            "BB0001031901004401073D00000000000000000000000000000000000000DE",
            "855c008cb63052ef239f1909f06cd04e3728719ad7b2f06b3d6eb2102edd3c4d",
        ),
        (
            25.0,
            "BB0001031901004401063D00000000000000000000000000000000000000DF",
            "a499631892d2f17255351c7fd8ff2974532d508c01f1e589a49e49bd9a891515",
        ),
        (
            26.0,
            "BB0001031901004401053D00000000000000000000000000000000000000DC",
            "b83ec6908cebb518ca87af11dbf91a9a16818fea1fe9fb159c662a648dfc267c",
        ),
    ],
)
def test_generated_frames_match_exact_relay_captures(
    target_temperature: float,
    expected_hex: str,
    expected_hash: str,
):
    generated = build_captured_heat_high_vertical_temperature_command(
        target_temperature
    )
    assert generated.hex().upper() == expected_hex
    assert hashlib.sha256(generated).hexdigest() == expected_hash
    assert york_xor(generated) == 0
    assert (
        validate_captured_heat_high_vertical_temperature_command(generated)
        == target_temperature
    )


def test_setpoint_encoding_is_monotonic_across_supported_range():
    frames = {
        value: build_captured_heat_high_vertical_temperature_command(value)
        for value in range(16, 32)
    }
    assert [frames[value][9] for value in range(16, 32)] == list(
        range(15, -1, -1)
    )
    assert all(frame[10] == 0x3D for frame in frames.values())
    with pytest.raises(YorkProtocolError, match="between 16 and 31"):
        build_captured_heat_high_vertical_temperature_command(15)
    with pytest.raises(YorkProtocolError, match="between 16 and 31"):
        build_captured_heat_high_vertical_temperature_command(32)
    with pytest.raises(YorkProtocolError, match="0.5 °C increments"):
        build_captured_heat_high_vertical_temperature_command(24.25)


def test_alpha39_capture_manifest_remains_reproducible():
    manifest = json.loads(
        Path(
            "protocols/york/qualification/"
            "alpha39_heat_temperature_encoding.json"
        ).read_text(encoding="utf-8")
    )
    assert manifest["version"] == "1.0.0-alpha.39"
    assert manifest["encoding"]["formula"] == (
        "31 - whole-degree Celsius setpoint"
    )
    assert [item["target_temperature"] for item in manifest["cases"]] == [
        24.0,
        25.0,
        26.0,
    ]
    for item in manifest["cases"]:
        generated = build_captured_heat_high_vertical_temperature_command(
            item["target_temperature"]
        )
        assert bytes.fromhex(item["frame_hex"]) == generated
        assert item["sha256"] == hashlib.sha256(generated).hexdigest()


def test_alpha39_representative_write_still_has_one_write_and_four_sends():
    before = qualification._state(25.0)
    after = qualification._state(24.0)
    command = build_captured_heat_high_vertical_temperature_command(24.0)
    sock = FakeSocket(
        _state_frame(before),
        _state_frame(after),
        command,
    )
    decoder = YorkPacketDecoder()
    client = BroadlinkYorkOneShotWriteClient(
        "192.0.2.30",
        80,
        "02:00:00:00:00:30",
        3,
        command,
        socket_factory=lambda *_args: sock,
    )

    def approve(frame: bytes) -> None:
        observed = decoder.decode_state(frame).to_dict()
        assert qualification._compare(before, observed)["result"] == "MATCH"

    result = client.execute(approve, post_write_delay_seconds=0)
    assert result.send_count == 4
    assert qualification._compare(
        after,
        decoder.decode_state(result.after_frame).to_dict(),
    )["result"] == "MATCH"
    assert [packet[0x26] for packet in sock.sent] == [
        AUTH_COMMAND,
        QUERY_COMMAND,
        QUERY_COMMAND,
        QUERY_COMMAND,
    ]

def test_alpha39_representative_precondition_failure_sends_zero_writes():
    before = qualification._state(25.0)
    after = qualification._state(24.0)
    command = build_captured_heat_high_vertical_temperature_command(24.0)
    sock = FakeSocket(
        _state_frame(before),
        _state_frame(after),
        command,
    )
    client = BroadlinkYorkOneShotWriteClient(
        "192.0.2.30",
        80,
        "02:00:00:00:00:30",
        3,
        command,
        socket_factory=lambda *_args: sock,
    )
    with pytest.raises(RuntimeError, match="mismatch"):
        client.execute(
            lambda _frame: (_ for _ in ()).throw(RuntimeError("mismatch")),
            post_write_delay_seconds=0,
        )
    assert client.last_send_count == 2
    assert len(sock.sent) == 2


def test_temperature_tool_is_not_wired_into_normal_control():
    root = Path(__file__).parent
    for name in (
        "bridge.py",
        "mqtt_manager.py",
        "direct_power_manager.py",
        "direct_temperature_manager.py",
    ):
        source = (root / name).read_text(encoding="utf-8")
        assert "york_temperature_one_shot_qualification" not in source


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
    monkeypatch.setattr(sys, "argv", ["temperature-tool", str(config)])
    assert qualification.main() == 0
    output = capsys.readouterr().out
    assert output.count("Generator/capture match: exact (31/31 bytes)") == 2
    assert "Qualified whole-degree range: 16 to 31 °C inclusive" in output
    assert "setpoint byte = 31 - temperature" in output
    assert "no socket opened and no packet transmitted" in output


def test_wrong_confirmation_stops_before_socket(
    tmp_path: Path,
    monkeypatch,
):
    config = _enabled_config(tmp_path)

    def forbidden_socket(*_args, **_kwargs):
        raise AssertionError("wrong confirmation opened a socket")

    monkeypatch.setattr("adapters.york.broadlink.socket.socket", forbidden_socket)
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "temperature-tool",
            str(config),
            "--case",
            "30-to-31",
            "--execute",
            "--confirm",
            "WRONG",
        ],
    )
    with pytest.raises(SystemExit, match="exact confirmation token"):
        qualification.main()
