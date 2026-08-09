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
    BroadlinkYorkOneShotWriteClient,
    YorkProtocolError,
    _crypt,
    broadlink_checksum,
    york_xor,
)
from adapters.york.decoder import YorkPacketDecoder
import york_power_one_shot_qualification as qualification


SESSION_KEY = bytes.fromhex("00112233445566778899AABBCCDDEEFF")
DEVICE_ID = 0x12345678


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

    def __exit__(self, *_args):
        return False

    def settimeout(self, value: float) -> None:
        self.timeout = value

    def sendto(self, packet: bytes, endpoint: tuple[str, int]) -> int:
        self.sent.append(packet)
        self.endpoint = endpoint
        return len(packet)

    def recvfrom(self, _size: int):
        request = self.sent[-1]
        if request[0x26] == AUTH_COMMAND:
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
    ("case_name", "expected_hex", "expected_hash", "source"),
    [
        (
            "off",
            "BB0001031901004003063D00000000000000000000000000000000000000D9",
            "46b8d41444e8363bf591b41c4334386fe509b2063a42863bd143900c0cbfc629",
            "Relay v2 transaction 46",
        ),
        (
            "off-heat",
            "BB0001031901004001063D00000000000000000000000000000000000000DB",
            "6be1093e8fb776faf047513d3b0bd6b9cca2166fac49d60346ce1f3575707b58",
            "successful Relay v2 Power Off from Heat transaction #7 (2026-07-30)",
        ),
        (
            "on-heat",
            "BB0001031901004401063D00000000000000000000000000000000000000DF",
            "a499631892d2f17255351c7fd8ff2974532d508c01f1e589a49e49bd9a891515",
            "fresh successful Relay v2 Power On + Heat log (2026-07-29)",
        ),
        (
            "on-cool",
            "BB0001031901004403063D00000000000000000000000000000000000000DD",
            "41fc632383cbbe62b9db91e018f9b9f73eaac3315e218439fa4e6f93c01e667c",
            "fresh successful Relay v2 Power On + Cool transaction #4 (2026-07-29)",
        ),
    ],
)
def test_power_frames_are_exact_captured_fixtures(
    case_name: str, expected_hex: str, expected_hash: str, source: str
):
    case = qualification.CASES[case_name]
    assert case.command.hex().upper() == expected_hex
    assert hashlib.sha256(case.command).hexdigest() == expected_hash
    assert york_xor(case.command) == 0
    assert case.source_reference == source
    qualification._validate_case(case)


@pytest.mark.parametrize("case_name", ["off", "off-heat", "on-heat", "on-cool"])
def test_each_power_case_has_one_write_and_four_sends(case_name: str):
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


@pytest.mark.parametrize("case_name", ["off", "off-heat", "on-heat", "on-cool"])
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


def test_modified_power_frame_is_rejected_even_with_valid_xor():
    modified = bytearray(qualification.CASES["off"].command)
    modified[9] ^= 0x01
    modified[-1] = york_xor(modified[:-1])
    assert york_xor(modified) == 0
    with pytest.raises(YorkProtocolError, match="non-qualification"):
        BroadlinkYorkOneShotWriteClient(
            "192.0.2.30",
            80,
            "02:00:00:00:00:30",
            3,
            bytes(modified),
        )


def test_alpha30_extra_zero_frame_is_rejected():
    rejected = bytes.fromhex(
        "BB0001031901004003063D0000000000000000000000000000000000000000D9"
    )
    corrected = qualification.CASES["off"].command
    assert len(rejected) == 32
    assert len(corrected) == 31
    assert york_xor(rejected) == 0
    assert york_xor(corrected) == 0
    assert rejected[:-2] == corrected[:-1]
    assert rejected[-2:] == b"\x00\xd9"
    with pytest.raises(YorkProtocolError, match="non-qualification"):
        BroadlinkYorkOneShotWriteClient(
            "192.0.2.30",
            80,
            "02:00:00:00:00:30",
            3,
            rejected,
        )


def test_package_exposes_only_proven_power_cases():
    assert tuple(qualification.CASES) == (
        "off",
        "off-heat",
        "on-heat",
        "on-cool",
    )
    assert qualification.CASES["off"].before["power"] is True
    assert qualification.CASES["off"].after["power"] is False
    assert qualification.CASES["off-heat"].before["power"] is True
    assert qualification.CASES["off-heat"].before["mode"] == "heat"
    assert qualification.CASES["off-heat"].after["power"] is False
    assert qualification.CASES["off-heat"].after["mode"] == "heat"
    assert qualification.CASES["on-heat"].before["power"] is False
    assert qualification.CASES["on-heat"].before["mode"] == "cool"
    assert qualification.CASES["on-heat"].after["power"] is True
    assert qualification.CASES["on-heat"].after["mode"] == "heat"
    assert qualification.CASES["on-cool"].before["power"] is False
    assert qualification.CASES["on-cool"].before["mode"] == "heat"
    assert qualification.CASES["on-cool"].after["power"] is True
    assert qualification.CASES["on-cool"].after["mode"] == "cool"


def test_power_tool_is_not_wired_into_normal_control():
    root = Path(__file__).parent
    for name in ("bridge.py", "mqtt_manager.py", "direct_temperature_manager.py"):
        source = (root / name).read_text(encoding="utf-8")
        assert "york_power_one_shot_qualification" not in source


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
    monkeypatch.setattr(sys, "argv", ["power-tool", str(config)])
    assert qualification.main() == 0
    output = capsys.readouterr().out
    assert "Power Off case:" in output
    assert "Power Off Heat case:" in output
    assert "Power On Heat case:" in output
    assert "Power On Cool case:" in output
    assert "Captured frame: exact (31/31 bytes)" in output
    assert "transaction 46" in output
    assert "Power Off from Heat transaction #7 (2026-07-30)" in output
    assert "Power On + Heat log (2026-07-29)" in output
    assert "Power On + Cool transaction #4 (2026-07-29)" in output
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
        sys, "argv", ["power-tool", str(config), "--execute"]
    )
    with pytest.raises(
        SystemExit,
        match="--case off, --case off-heat, --case on-heat, or --case on-cool",
    ):
        qualification.main()
