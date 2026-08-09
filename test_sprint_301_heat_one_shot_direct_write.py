from __future__ import annotations

import hashlib
import json
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
    YORK_QUALIFICATION_HEAT_23_TO_24,
    BroadlinkYorkOneShotWriteClient,
    _SessionEnvelope,
    _crypt,
    broadlink_checksum,
    york_xor,
)
from adapters.york.decoder import YorkPacketDecoder
from adapters.york.errors import YorkProtocolError
import york_heat_one_shot_write_qualification as heat_tool

def _heat_low_frame(temperature: int) -> bytes:
    frame = bytearray.fromhex(
        "BB 01 00 03 0F 01 00 34 18 20 00 00 00 00 00 00 00 6E 00 00 00"
    )
    frame[8] = 0x10 | (temperature - 16)
    checksum = 0
    for value in frame[:-1]:
        checksum ^= value
    frame[-1] = checksum
    return bytes(frame)


BEFORE = _heat_low_frame(23)
AFTER = _heat_low_frame(24)
SESSION_KEY = bytes.fromhex("00112233445566778899AABBCCDDEEFF")
DEVICE_ID = 0x12345678


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
    def __init__(self, *args, **kwargs) -> None:
        self.sent: list[bytes] = []
        self.timeout = 0.0
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
            encrypted = request[0x38:]
            clear_request = _crypt(SESSION_KEY, encrypted, encrypt=False)
            length = int.from_bytes(clear_request[:2], "little")
            inner = clear_request[2 : 2 + length]
            if self.query_count == 0:
                assert inner != YORK_QUALIFICATION_HEAT_23_TO_24
                frame = BEFORE
            elif self.query_count == 1:
                assert inner == YORK_QUALIFICATION_HEAT_23_TO_24
                frame = AFTER
            else:
                assert inner != YORK_QUALIFICATION_HEAT_23_TO_24
                frame = AFTER
            self.query_count += 1
            clear = len(frame).to_bytes(2, "little") + frame
            response = _reply(request, QUERY_REPLY, clear, SESSION_KEY)
        return response, self.endpoint


def test_embedded_command_matches_official_relay_transaction_25():
    assert len(YORK_QUALIFICATION_HEAT_23_TO_24) == 31
    assert YORK_QUALIFICATION_HEAT_23_TO_24.hex(" ").upper() == (
        "BB 00 01 03 19 01 00 44 01 07 02 00 00 00 00 00 00 00 "
        "00 00 00 00 00 00 00 00 00 00 00 00 E1"
    )
    assert york_xor(YORK_QUALIFICATION_HEAT_23_TO_24) == 0
    assert hashlib.sha256(YORK_QUALIFICATION_HEAT_23_TO_24).hexdigest() == (
        "c55bd6793f3c6a84934195822cec2e5834fc0fa4429252e13a17659cbc770925"
    )


def test_qualification_evidence_matches_embedded_command():
    path = (
        __import__("pathlib").Path(__file__).parent
        / "protocols/york/qualification/alpha26_heat_one_shot_write.json"
    )
    evidence = json.loads(path.read_text(encoding="utf-8"))
    assert bytes.fromhex(evidence["frame_hex"]) == YORK_QUALIFICATION_HEAT_23_TO_24
    assert evidence["source"]["transaction_id"] == 25
    assert evidence["source"]["relay_verification_success"] is True
    assert evidence["execution_policy"]["write_count"] == 1
    assert evidence["execution_policy"]["automatic_retries"] == 0


def test_exact_pre_read_write_post_read_sequence():
    sock = FakeSocket()
    decoder = YorkPacketDecoder()
    client = BroadlinkYorkOneShotWriteClient(
        "192.0.2.25",
        80,
        "02:00:00:00:00:25",
        3,
        YORK_QUALIFICATION_HEAT_23_TO_24,
        socket_factory=lambda *args: sock,
    )

    def approve(frame: bytes) -> None:
        state = decoder.decode_state(frame)
        assert state.power is True
        assert state.mode == "heat"
        assert state.temperature == 23.0
        assert state.fan == "low"
        assert state.swing == "off"

    result = client.execute(approve, post_write_delay_seconds=0)
    assert result.send_count == 4
    assert result.before_frame == BEFORE
    assert result.command_reply_frame == AFTER
    assert result.after_frame == AFTER
    assert decoder.decode_state(result.after_frame).temperature == 24.0
    assert [packet[0x26] for packet in sock.sent] == [
        AUTH_COMMAND,
        QUERY_COMMAND,
        QUERY_COMMAND,
        QUERY_COMMAND,
    ]


def test_precondition_failure_sends_no_write_command():
    sock = FakeSocket()
    client = BroadlinkYorkOneShotWriteClient(
        "192.0.2.25",
        80,
        "02:00:00:00:00:25",
        3,
        YORK_QUALIFICATION_HEAT_23_TO_24,
        socket_factory=lambda *args: sock,
    )

    def reject(frame: bytes) -> None:
        raise RuntimeError("state mismatch")

    with pytest.raises(RuntimeError, match="state mismatch"):
        client.execute(reject, post_write_delay_seconds=0)
    assert client.last_send_count == 2
    assert len(sock.sent) == 2


def test_session_interlock_rejects_any_modified_command():
    session = _SessionEnvelope(
        mac=bytes.fromhex("020000000025"),
        counter=0x8000,
        device_id=DEVICE_ID,
        key=SESSION_KEY,
    )
    modified = bytearray(YORK_QUALIFICATION_HEAT_23_TO_24)
    modified[9] ^= 0x01
    modified[-1] ^= 0x01
    with pytest.raises(YorkProtocolError, match="non-qualification"):
        session.build_qualification_write_packet(bytes(modified))


def test_normal_direct_transport_remains_read_only():
    source = (
        __import__("pathlib").Path(__file__).with_name("transport")
        / "york_direct_transport.py"
    ).read_text(encoding="utf-8")
    assert "direct LAN integration is read-only" in source


def test_heat_one_shot_tool_is_not_wired_into_bridge_or_mqtt():
    root = __import__("pathlib").Path(__file__).parent
    for name in ("bridge.py", "mqtt_manager.py", "transport/factory.py"):
        source = (root / name).read_text(encoding="utf-8")
        assert "york_heat_one_shot_write_qualification" not in source
        assert "YORK_QUALIFICATION_HEAT_23_TO_24" not in source


def test_client_rejects_unverified_command_before_opening_socket():
    with pytest.raises(YorkProtocolError, match="non-qualification"):
        BroadlinkYorkOneShotWriteClient(
            "192.0.2.25",
            80,
            "02:00:00:00:00:25",
            3,
            bytes.fromhex("BB000104020100BD"),
        )


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
    monkeypatch.setattr(sys, "argv", ["heat-tool", str(config)])
    assert heat_tool.main() == 0
    output = capsys.readouterr().out
    assert "VALIDATION PASSED" in output
    assert "no socket opened and no packet transmitted" in output
