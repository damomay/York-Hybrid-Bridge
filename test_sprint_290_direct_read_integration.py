from __future__ import annotations

from pathlib import Path

import pytest

from adapters.york.broadlink import (
    AUTH_COMMAND,
    AUTH_REPLY,
    INITIAL_KEY,
    MAGIC,
    QUERY_COMMAND,
    QUERY_REPLY,
    YORK_DEVICE_TYPE,
    BroadlinkYorkReadClient,
    _crypt,
    broadlink_checksum,
)
from adapters.york.errors import YorkProtocolError, YorkProtocolNotReady
from configuration import load_config
from direct_read_manager import DirectReadManager
from transport.york_direct_transport import YorkDirectTransport


class FakeYorkSocket:
    session_key = bytes.fromhex("00112233445566778899AABBCCDDEEFF")
    session_id = 2
    state_frame = bytes.fromhex(
        "BB0100030F0100340920000000000000005C0800FE"
    )

    def __init__(self, *_args) -> None:
        self.requests: list[bytes] = []
        self.pending: bytes | None = None
        self.endpoint = ("192.0.2.1", 80)

    def __enter__(self):
        return self

    def __exit__(self, *_args) -> None:
        return None

    def settimeout(self, _timeout: float) -> None:
        return None

    @staticmethod
    def _reply(request: bytes, command: int, clear: bytes, key: bytes) -> bytes:
        packet = bytearray(0x38)
        packet[:8] = MAGIC
        packet[0x24:0x26] = YORK_DEVICE_TYPE.to_bytes(2, "little")
        packet[0x26] = command
        packet[0x27] = 0x03
        packet[0x28:0x2A] = request[0x28:0x2A]
        packet[0x34:0x36] = broadlink_checksum(clear).to_bytes(2, "little")
        packet.extend(_crypt(key, clear + bytes((-len(clear)) % 16), encrypt=True))
        packet[0x20:0x22] = broadlink_checksum(packet).to_bytes(2, "little")
        return bytes(packet)

    def sendto(self, packet: bytes, endpoint: tuple[str, int]) -> int:
        assert endpoint == self.endpoint
        self.requests.append(packet)
        command = packet[0x26]
        if command == AUTH_COMMAND:
            clear = self.session_id.to_bytes(4, "little") + self.session_key + bytes(60)
            self.pending = self._reply(packet, AUTH_REPLY, clear, INITIAL_KEY)
        elif command == QUERY_COMMAND:
            clear = len(self.state_frame).to_bytes(2, "little") + self.state_frame
            self.pending = self._reply(packet, QUERY_REPLY, clear, self.session_key)
        else:
            raise AssertionError(f"unexpected Broadlink command 0x{command:02X}")
        return len(packet)

    def recvfrom(self, _max_bytes: int):
        assert self.pending is not None
        reply = self.pending
        self.pending = None
        return reply, self.endpoint


def test_qualified_direct_read_uses_two_sends_and_dynamic_session_id() -> None:
    fake = FakeYorkSocket()
    client = BroadlinkYorkReadClient(
        "192.0.2.1",
        80,
        "02:00:00:00:00:01",
        3,
        socket_factory=lambda *_args: fake,
    )
    assert client.read_state_frame() == fake.state_frame
    assert client.last_send_count == 2
    assert client.last_session_id == 2
    assert [packet[0x26] for packet in fake.requests] == [
        AUTH_COMMAND,
        QUERY_COMMAND,
    ]
    assert int.from_bytes(fake.requests[1][0x30:0x34], "little") == 2


def test_direct_transport_has_no_control_encoder() -> None:
    transport = YorkDirectTransport(load_config(Path("config.example.yml")))
    with pytest.raises(YorkProtocolNotReady, match="read-only"):
        transport.command(temperature=25)


def test_zero_session_id_stops_after_authentication() -> None:
    fake = FakeYorkSocket()
    fake.session_id = 0
    client = BroadlinkYorkReadClient(
        "192.0.2.1",
        80,
        "02:00:00:00:00:01",
        3,
        socket_factory=lambda *_args: fake,
    )
    with pytest.raises(YorkProtocolError, match="zero session ID"):
        client.read_state_frame()
    assert len(fake.requests) == 1
    assert fake.requests[0][0x26] == AUTH_COMMAND


class FakeDirectTransport:
    last_response_length = 21
    last_send_count = 2
    last_raw_frame_hex = (
        "BB0100030F0100340920000000000000005C0800FE"
    )
    last_fan_status_byte = 0x09
    last_fan_status_nibble = 0

    def __init__(self, _config) -> None:
        self.calls = 0

    def get_state(self):
        self.calls += 1
        return {"power": True, "mode": "heat", "fan": "auto"}

    def close(self) -> None:
        return None


def test_shadow_manager_compares_without_immediate_retry() -> None:
    config = load_config(Path("config.example.yml"))
    fake = FakeDirectTransport(config)
    manager = DirectReadManager(config, transport_factory=lambda _config: fake)
    relay = {"power": True, "mode": "heat", "fan": "auto", "temperature": 24}

    result = manager.observe(relay, now=100)
    assert result is not None
    assert result.comparison == "match (3/3)"
    assert result.udp_sends == 2
    assert result.raw_frame_hex == FakeDirectTransport.last_raw_frame_hex
    assert result.fan_status_byte == 0x09
    assert result.fan_status_nibble == 0
    assert fake.calls == 1

    assert manager.observe(relay, now=101) is None
    assert fake.calls == 1


def test_stable_example_enables_authoritative_direct_read_only() -> None:
    config = load_config(Path("config.example.yml"))
    assert config.transport_type == "native"
    assert config.direct_read_enabled is True
    assert config.direct_control_enabled is False


def test_direct_transport_exposes_status_fan_diagnostics() -> None:
    fake = FakeYorkSocket()
    client = BroadlinkYorkReadClient(
        "192.0.2.1",
        80,
        "02:00:00:00:00:01",
        3,
        socket_factory=lambda *_args: fake,
    )
    config = load_config(Path("config.example.yml"))
    transport = YorkDirectTransport(config)
    transport.client = client

    state = transport.get_state()

    assert state["fan"] == "auto"
    assert transport.last_raw_frame_hex == fake.state_frame.hex().upper()
    assert transport.last_fan_status_byte == 0x09
    assert transport.last_fan_status_nibble == 0
