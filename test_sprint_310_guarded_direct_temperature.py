from __future__ import annotations

import threading
from pathlib import Path
from types import SimpleNamespace

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
from adapters.york.temperature_command import build_qualified_temperature_command
from bridge import ClimateBridge
from configuration import load_config
from direct_temperature_manager import (
    DirectTemperatureManager,
    DirectTemperatureSafeStop,
    DirectTemperatureVerificationError,
)

SESSION_KEY = bytes.fromhex("00112233445566778899AABBCCDDEEFF")
DEVICE_ID = 0x12345678


def _state_frame(
    mode: str,
    temperature: float,
    *,
    fan: str = "low",
) -> bytes:
    whole = int(temperature)
    mode_nibble = {"cool": 0x01, "heat": 0x04}[mode]
    fan_nibble = {"auto": 0x00, "low": 0x10, "medium": 0x20, "high": 0x30}[fan]
    frame = bytearray.fromhex(
        "BB 01 00 03 0F 01 00 30 10 00 00 00 00 00 00 00 00 6E 00 00 00"
    )
    frame[7] = 0x30 | mode_nibble
    frame[8] = fan_nibble | (whole - 16)
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
        self.endpoint = ("192.0.2.29", 80)

    def __enter__(self):
        return self

    def __exit__(self, *_args):
        return False

    def settimeout(self, value: float) -> None:
        self.timeout = value

    def sendto(self, packet: bytes, endpoint: tuple[str, int]) -> int:
        assert endpoint == self.endpoint
        self.sent.append(packet)
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


def _relay_state(mode: str, temperature: float, *, fan: str = "low"):
    return {
        "power": True,
        "mode": mode,
        "temperature": temperature,
        "indoor_temperature": 21,
        "fan": fan,
        "swing": "off",
        "turbo": False,
        "eco": False,
        "health": False,
        "display": True,
    }


def _manager(mode: str, before: float, target: float, after: float):
    config = load_config(Path("config.example.yml"))
    command = build_qualified_temperature_command(mode, target)
    sock = FakeSocket(
        _state_frame(mode, before),
        _state_frame(mode, after),
        command,
    )

    def factory(host, port, mac, timeout, requested_mode, requested_target):
        assert requested_mode == mode
        assert requested_target == target
        return BroadlinkYorkTemperatureWriteClient(
            "192.0.2.29",
            port,
            "02:00:00:00:00:29",
            timeout,
            requested_mode,
            requested_target,
            socket_factory=lambda *_args: sock,
        )

    return DirectTemperatureManager(config, client_factory=factory), sock


@pytest.mark.parametrize(
    ("mode", "before", "target"),
    [
        ("heat", 23.5, 22.5),
    ],
)
def test_guarded_normal_temperature_control_passes_once(mode, before, target):
    manager, sock = _manager(mode, before, target, target)
    response = manager.command(target, _relay_state(mode, before))

    assert response["temperature"] == target
    assert response["indoor_temperature"] == 21
    assert response["_transaction"]["source"] == "york_direct_temperature"
    assert response["_transaction"]["verification"]["matched_fields"] == 9
    assert response["_transaction"]["automatic_retries"] == 0
    assert manager.last_udp_sends == 4
    assert len(sock.sent) == 4


def test_ineligible_relay_shape_stops_before_client_or_socket():
    config = load_config(Path("config.example.yml"))

    def forbidden_client(*_args, **_kwargs):
        raise AssertionError("client created for an ineligible relay state")

    manager = DirectTemperatureManager(config, client_factory=forbidden_client)
    with pytest.raises(DirectTemperatureSafeStop, match="fan"):
        manager.command(24.5, _relay_state("cool", 25, fan="medium"))


def test_live_pre_read_mismatch_sends_no_write():
    manager, sock = _manager("heat", 23.0, 24.0, 24.0)
    with pytest.raises(DirectTemperatureSafeStop, match="direct pre-read"):
        manager.command(24.0, _relay_state("heat", 23.5))
    assert len(sock.sent) == 2
    assert manager.last_udp_sends == 2


def test_post_read_mismatch_is_a_failure_with_no_retry():
    manager, sock = _manager("heat", 25.0, 24.5, 25.0)
    with pytest.raises(
        DirectTemperatureVerificationError,
        match="post-read verification",
    ):
        manager.command(24.5, _relay_state("heat", 25.0))
    assert len(sock.sent) == 4
    assert manager.last_udp_sends == 4


class DummyDiagnostics:
    command_count = 0
    command_failure_count = 0
    command_deferred_count = 0
    bridge_status = "ready"
    last_error = "none"

    def __init__(self):
        self.events = []

    def publish_command(self, **_kwargs):
        return None

    def publish_metrics(self):
        return None

    def record_event(self, level, message):
        self.events.append((level, message))

    def record_stability_event(self, _success):
        return None


class DummyMqtt:
    def publish(self, *_args, **_kwargs):
        return True


class DummyRelay:
    def __init__(self, response):
        self.response = response
        self.calls = []

    def command(self, **changes):
        self.calls.append(changes)
        return self.response


class StoppedDirect:
    def __init__(self):
        self.calls = []

    def command(self, target, relay_state):
        self.calls.append((target, relay_state))
        raise DirectTemperatureSafeStop("test safe stop")


def test_bridge_rejects_after_one_direct_safe_stop_without_fallback():
    state = _relay_state("heat", 23.0)
    relay_response = {**state, "temperature": 24.0}
    bridge = ClimateBridge.__new__(ClimateBridge)
    bridge.config = load_config(Path("config.example.yml"))
    bridge.stop_event = threading.Event()
    bridge.diagnostics = DummyDiagnostics()
    bridge.mqtt = DummyMqtt()
    bridge.transport = DummyRelay(relay_response)
    bridge.direct_temperature = StoppedDirect()
    bridge.last_state = state
    bridge.pending_temperature = None
    bridge._update_health = lambda: None

    with pytest.raises(Exception, match="native command rejected"):
        bridge.execute_command({"temperature": 24.0})

    assert len(bridge.direct_temperature.calls) == 1
    assert bridge.transport.calls == []
    assert bridge.diagnostics.events == [
        ("WARNING", "Native command rejected")
    ]


def test_unqualified_non_temperature_command_is_rejected():
    state = _relay_state("heat", 23.0)
    relay_response = {**state, "fan": "auto"}
    bridge = ClimateBridge.__new__(ClimateBridge)
    bridge.config = load_config(Path("config.example.yml"))
    bridge.stop_event = threading.Event()
    bridge.diagnostics = DummyDiagnostics()
    bridge.mqtt = DummyMqtt()
    bridge.transport = DummyRelay(relay_response)
    bridge.direct_temperature = StoppedDirect()
    bridge.last_state = state
    bridge.pending_temperature = None
    bridge._update_health = lambda: None

    with pytest.raises(Exception, match="native command rejected"):
        bridge.execute_command({"fan": "auto"})

    assert bridge.direct_temperature.calls == []
    assert bridge.transport.calls == []


def test_direct_control_is_disabled_by_default():
    config = load_config(Path("config.example.yml"))
    assert config.direct_control_enabled is False
    assert not hasattr(config, "direct_control_fallback_to_relay")


def test_direct_control_can_be_explicitly_enabled(tmp_path: Path):
    path = tmp_path / "config.yml"
    path.write_text(
        Path("config.example.yml")
        .read_text(encoding="utf-8")
        .replace("direct_read:\n  enabled: false", "direct_read:\n  enabled: true")
        .replace("direct_control:\n  enabled: false", "direct_control:\n  enabled: true"),
        encoding="utf-8",
    )
    config = load_config(path)
    assert config.direct_read_enabled is True
    assert config.direct_control_enabled is True
    assert not hasattr(config, "direct_control_fallback_to_relay")
    assert config.direct_control_post_write_delay_seconds == 2
