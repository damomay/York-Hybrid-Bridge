from __future__ import annotations

import threading
from pathlib import Path
from types import SimpleNamespace

import pytest

from adapters.york.broadlink import YorkOneShotWriteResult, york_xor
from bridge import ClimateBridge
from configuration import load_config
from direct_power_manager import (
    DIRECT_POWER_CASES,
    DirectPowerManager,
    DirectPowerSafeStop,
    DirectPowerVerificationError,
)


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


class FakeClient:
    def __init__(self, command: bytes, before: dict, after: dict) -> None:
        self.command = command
        self.before = before
        self.after = after
        self.last_send_count = 0

    def execute(self, approve_precondition, *, post_write_delay_seconds):
        assert post_write_delay_seconds == 2
        self.last_send_count = 2
        approve_precondition(_state_frame(self.before))
        self.last_send_count = 4
        return YorkOneShotWriteResult(
            before_frame=_state_frame(self.before),
            command_reply_frame=_state_frame(self.after),
            after_frame=_state_frame(self.after),
            send_count=4,
            session_id=0x12345678,
        )


def _manager(case, *, live_before=None, live_after=None):
    config = load_config(Path("config.example.yml"))
    clients = []

    def factory(host, port, mac, timeout, command):
        assert command == case.command
        client = FakeClient(
            command,
            live_before or case.before,
            live_after or case.after,
        )
        clients.append(client)
        return client

    return DirectPowerManager(config, client_factory=factory), clients


@pytest.mark.parametrize("case", DIRECT_POWER_CASES, ids=lambda case: case.name)
def test_each_qualified_power_case_passes_once(case):
    manager, clients = _manager(case)
    response = manager.command(dict(case.requested), dict(case.before))

    assert response["_transaction"]["source"] == "york_direct_power"
    assert response["_transaction"]["case"] == case.name
    assert response["_transaction"]["verification"]["matched_fields"] == 9
    assert response["_transaction"]["automatic_retries"] == 0
    assert response["_transaction"]["fallback_used"] is False
    assert manager.last_udp_sends == 4
    assert len(clients) == 1


def test_unqualified_request_stops_before_client_creation():
    config = load_config(Path("config.example.yml"))

    def forbidden_client(*_args, **_kwargs):
        raise AssertionError("client created for an unqualified request")

    manager = DirectPowerManager(config, client_factory=forbidden_client)
    with pytest.raises(DirectPowerSafeStop, match="exact qualified"):
        manager.command(
            {"power": True, "mode": "cool", "temperature": 24.0},
            dict(DIRECT_POWER_CASES[2].before),
        )


def test_ineligible_relay_state_stops_before_client_creation():
    case = DIRECT_POWER_CASES[0]
    config = load_config(Path("config.example.yml"))

    def forbidden_client(*_args, **_kwargs):
        raise AssertionError("client created for an ineligible relay state")

    manager = DirectPowerManager(config, client_factory=forbidden_client)
    state = {**case.before, "fan": "low"}
    with pytest.raises(DirectPowerSafeStop, match="qualified power shape"):
        manager.command(dict(case.requested), state)


def test_live_pre_read_mismatch_sends_zero_writes():
    case = DIRECT_POWER_CASES[1]
    manager, clients = _manager(
        case,
        live_before={**case.before, "temperature": 24.0},
    )
    with pytest.raises(DirectPowerSafeStop, match="direct pre-read"):
        manager.command(dict(case.requested), dict(case.before))
    assert clients[0].last_send_count == 2
    assert manager.last_udp_sends == 2


def test_post_read_mismatch_fails_with_no_retry():
    case = DIRECT_POWER_CASES[2]
    manager, clients = _manager(
        case,
        live_after={**case.after, "power": False},
    )
    with pytest.raises(
        DirectPowerVerificationError,
        match="post-read verification",
    ):
        manager.command(dict(case.requested), dict(case.before))
    assert clients[0].last_send_count == 4
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


class PassingDirectPower:
    def __init__(self, response):
        self.response = response
        self.calls = []

    def command(self, command, relay_state):
        self.calls.append((command, relay_state))
        return self.response


class StoppedDirectPower:
    def __init__(self):
        self.calls = []

    def command(self, command, relay_state):
        self.calls.append((command, relay_state))
        raise DirectPowerSafeStop("test safe stop")


def _bridge(state, relay_response, direct_power):
    bridge = ClimateBridge.__new__(ClimateBridge)
    bridge.config = load_config(Path("config.example.yml"))
    bridge.stop_event = threading.Event()
    bridge.diagnostics = DummyDiagnostics()
    bridge.mqtt = DummyMqtt()
    bridge.transport = DummyRelay(relay_response)
    bridge.direct_temperature = None
    bridge.direct_power = direct_power
    bridge.last_state = state
    bridge.pending_temperature = None
    bridge._update_health = lambda: None
    return bridge


def test_bridge_routes_exact_power_request_to_direct_manager():
    case = DIRECT_POWER_CASES[0]
    direct_response = {
        **case.after,
        "_transaction": {"success": True, "source": "york_direct_power"},
    }
    direct = PassingDirectPower(direct_response)
    bridge = _bridge(case.before, case.after, direct)

    response = bridge.execute_command(dict(case.requested))

    assert response["_transaction"]["source"] == "york_direct_power"
    assert len(direct.calls) == 1
    assert bridge.transport.calls == []


def test_bridge_rejects_after_direct_power_safe_stop_without_fallback():
    case = DIRECT_POWER_CASES[1]
    relay_response = {
        **case.after,
        "_transaction": {"success": True, "source": "relay"},
    }
    direct = StoppedDirectPower()
    bridge = _bridge(case.before, relay_response, direct)

    with pytest.raises(Exception, match="native command rejected"):
        bridge.execute_command(dict(case.requested))

    assert bridge.transport.calls == []
    assert bridge.diagnostics.events == [
        ("WARNING", "Native command rejected")
    ]


def test_pending_temperature_power_on_is_rejected_when_combined_shape_is_unqualified():
    case = next(case for case in DIRECT_POWER_CASES if case.name == "on-cool")
    relay_response = {**case.after, "temperature": 24.0}
    direct = PassingDirectPower(case.after)
    bridge = _bridge(case.before, relay_response, direct)
    bridge.pending_temperature = 24.0

    with pytest.raises(Exception, match="native command rejected"):
        bridge.execute_command(dict(case.requested))

    assert direct.calls == []
    assert bridge.transport.calls == []


def test_direct_power_is_disabled_by_default_and_separate_from_temperature():
    config = load_config(Path("config.example.yml"))
    assert config.direct_control_enabled is False
    assert config.direct_power_control_enabled is False
    assert tuple(case.name for case in DIRECT_POWER_CASES) == (
        "off",
        "off-heat",
        "on-heat",
        "on-cool",
        "heat-to-cool",
        "cool-to-heat",
    )


def test_direct_power_requires_explicit_opt_in(tmp_path: Path):
    path = tmp_path / "config.yml"
    path.write_text(
        Path("config.example.yml")
        .read_text(encoding="utf-8")
        .replace("direct_control:\n  enabled: false", "direct_control:\n  enabled: true")
        .replace("  power_enabled: false", "  power_enabled: true"),
        encoding="utf-8",
    )
    config = load_config(path)
    assert config.direct_control_enabled is True
    assert config.direct_power_control_enabled is True
