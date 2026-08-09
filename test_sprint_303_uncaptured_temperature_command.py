from __future__ import annotations

import hashlib
import sys
from pathlib import Path

import pytest

from adapters.york.broadlink import (
    AUTH_COMMAND,
    AUTH_REPLY,
    INITIAL_KEY,
    MAGIC,
    QUERY_COMMAND,
    QUERY_REPLY,
    BroadlinkYorkTemperatureWriteClient,
    _crypt,
    broadlink_checksum,
)
from adapters.york.decoder import YorkPacketDecoder
from adapters.york.temperature_command import (
    build_qualified_temperature_command,
    validate_qualified_temperature_command,
)
import york_uncaptured_temperature_qualification as qualification


SESSION_KEY = bytes.fromhex("00112233445566778899AABBCCDDEEFF")
DEVICE_ID = 0x12345678


def _state_frame(mode: str, temperature: float) -> bytes:
    whole = int(temperature)
    mode_nibble = {"cool": 0x01, "heat": 0x04}[mode]
    frame = bytearray.fromhex(
        "BB 01 00 03 0F 01 00 30 10 00 00 00 00 00 00 00 00 6E 00 00 00"
    )
    frame[7] = 0x30 | mode_nibble
    frame[8] = 0x10 | (whole - 16)
    frame[9] = 0x02 if temperature != whole else 0x00
    checksum = 0
    for value in frame[:-1]:
        checksum ^= value
    frame[-1] = checksum
    return bytes(frame)


def _reply(request: bytes, command: int, clear: bytes, key: bytes) -> bytes:
    packet = bytearray(0x38)
    packet[:8] = MAGIC
    packet[0x26] = command
    packet[0x28:0x2A] = request[0x28:0x2A]
    padded = clear + bytes((-len(clear)) % 16)
    packet[0x34:0x36] = broadlink_checksum(padded).to_bytes(2, "little")
    packet.extend(_crypt(key, padded, encrypt=True))
    packet[0x20:0x22] = broadlink_checksum(packet).to_bytes(2, "little")
    return bytes(packet)


class FakeSocket:
    def __init__(self, before: bytes, after: bytes, command: bytes) -> None:
        self.before = before
        self.after = after
        self.command = command
        self.sent: list[bytes] = []
        self.query_count = 0

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False

    def settimeout(self, value: float) -> None:
        self.timeout = value

    def sendto(self, packet: bytes, endpoint: tuple[str, int]) -> int:
        self.sent.append(packet)
        self.endpoint = endpoint
        return len(packet)

    def recvfrom(self, size: int):
        request = self.sent[-1]
        command = request[0x26]
        if command == AUTH_COMMAND:
            clear = DEVICE_ID.to_bytes(4, "little") + SESSION_KEY + bytes(60)
            response = _reply(request, AUTH_REPLY, clear, INITIAL_KEY)
        else:
            clear_request = _crypt(SESSION_KEY, request[0x38:], encrypt=False)
            length = int.from_bytes(clear_request[:2], "little")
            inner = clear_request[2 : 2 + length]
            if self.query_count == 0:
                assert inner != self.command
                frame = self.before
            elif self.query_count == 1:
                assert inner == self.command
                frame = self.after
            else:
                assert inner != self.command
                frame = self.after
            self.query_count += 1
            clear = len(frame).to_bytes(2, "little") + frame
            response = _reply(request, QUERY_REPLY, clear, SESSION_KEY)
        return response, self.endpoint


@pytest.mark.parametrize(
    ("case_name", "mode", "target", "expected_hex", "expected_hash"),
    [
        (
            "heat",
            "heat",
            22.5,
            "BB0001031901004401090202000000000000000000000000000000000000ED",
            "048b2814020e6119baa087f93eac0f6d980020b78bda74dbfa2b426a57a83601",
        ),
        (
            "cool",
            "cool",
            24.5,
            "BB0001031901004403070202000000000000000000000000000000000000E1",
            "bb1289158a8647707f985b85c5958aa32d6d3d6ee2a8e46945d74f2f0b5fa7c4",
        ),
    ],
)
def test_uncaptured_fixtures_are_exact_and_canonical(
    case_name: str,
    mode: str,
    target: float,
    expected_hex: str,
    expected_hash: str,
):
    command = build_qualified_temperature_command(mode, target)
    assert command.hex().upper() == expected_hex
    assert hashlib.sha256(command).hexdigest() == expected_hash
    assert validate_qualified_temperature_command(command) == (mode, target)
    assert qualification._validated_generated_command(
        qualification.CASES[case_name]
    ) == command


@pytest.mark.parametrize("case_name", ["heat", "cool"])
def test_each_case_has_exact_four_send_sequence(case_name: str):
    case = qualification.CASES[case_name]
    command = build_qualified_temperature_command(
        case.mode, case.target_temperature
    )
    sock = FakeSocket(
        _state_frame(case.mode, case.before_temperature),
        _state_frame(case.mode, case.target_temperature),
        command,
    )
    decoder = YorkPacketDecoder()
    client = BroadlinkYorkTemperatureWriteClient(
        "192.0.2.28",
        80,
        "02:00:00:00:00:28",
        3,
        case.mode,
        case.target_temperature,
        socket_factory=lambda *args: sock,
    )

    def approve(frame: bytes) -> None:
        observed = decoder.decode_state(frame).to_dict()
        assert qualification._compare(
            case.expected_before, observed
        )["result"] == "MATCH"

    result = client.execute(approve, post_write_delay_seconds=0)
    assert result.send_count == 4
    assert decoder.decode_state(result.after_frame).temperature == (
        case.target_temperature
    )
    assert [packet[0x26] for packet in sock.sent] == [
        AUTH_COMMAND,
        QUERY_COMMAND,
        QUERY_COMMAND,
        QUERY_COMMAND,
    ]


@pytest.mark.parametrize("case_name", ["heat", "cool"])
def test_precondition_failure_sends_zero_writes(case_name: str):
    case = qualification.CASES[case_name]
    command = build_qualified_temperature_command(
        case.mode, case.target_temperature
    )
    sock = FakeSocket(
        _state_frame(case.mode, case.before_temperature),
        _state_frame(case.mode, case.target_temperature),
        command,
    )
    client = BroadlinkYorkTemperatureWriteClient(
        "192.0.2.28",
        80,
        "02:00:00:00:00:28",
        3,
        case.mode,
        case.target_temperature,
        socket_factory=lambda *args: sock,
    )

    def reject(frame: bytes) -> None:
        raise RuntimeError("state mismatch")

    with pytest.raises(RuntimeError, match="state mismatch"):
        client.execute(reject, post_write_delay_seconds=0)
    assert client.last_send_count == 2
    assert len(sock.sent) == 2


def test_cases_use_distinct_confirmation_tokens():
    assert qualification.CASES["heat"].confirmation_token != (
        qualification.CASES["cool"].confirmation_token
    )


def test_uncaptured_tool_is_not_wired_into_normal_control():
    root = Path(__file__).parent
    for name in ("bridge.py", "mqtt_manager.py", "transport/factory.py"):
        source = (root / name).read_text(encoding="utf-8")
        assert "york_uncaptured_temperature_qualification" not in source


def test_validation_mode_opens_no_socket(tmp_path: Path, monkeypatch, capsys):
    config = tmp_path / "config.yml"
    config.write_text(
        Path("config.example.yml")
        .read_text(encoding="utf-8")
        .replace("direct_read:\n  enabled: false", "direct_read:\n  enabled: true"),
        encoding="utf-8",
    )

    def forbidden_socket(*_args, **_kwargs):
        raise AssertionError("validation mode opened a socket")

    monkeypatch.setattr("adapters.york.broadlink.socket.socket", forbidden_socket)
    monkeypatch.setattr(
        sys,
        "argv",
        ["uncaptured-tool", str(config)],
    )
    assert qualification.main() == 0
    output = capsys.readouterr().out
    assert "Heat case:" in output
    assert "Cool case:" in output
    assert output.count("Fixture match: exact (31/31 bytes)") == 2
    assert "no socket opened and no packet transmitted" in output


def test_execute_without_case_stops_before_socket(
    tmp_path: Path, monkeypatch
):
    config = tmp_path / "config.yml"
    config.write_text(
        Path("config.example.yml")
        .read_text(encoding="utf-8")
        .replace("direct_read:\n  enabled: false", "direct_read:\n  enabled: true"),
        encoding="utf-8",
    )

    def forbidden_socket(*_args, **_kwargs):
        raise AssertionError("missing case opened a socket")

    monkeypatch.setattr("adapters.york.broadlink.socket.socket", forbidden_socket)
    monkeypatch.setattr(
        sys,
        "argv",
        ["uncaptured-tool", str(config), "--execute"],
    )
    with pytest.raises(SystemExit, match="--case heat or --case cool"):
        qualification.main()
