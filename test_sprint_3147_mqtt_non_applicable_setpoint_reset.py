from __future__ import annotations

from unittest.mock import Mock

import pytest

from bridge import ClimateBridge
from mqtt_manager import MqttManager


BASE = "climate_bridge/york"


def _bridge(*, previous_temperature=23.0) -> ClimateBridge:
    bridge = object.__new__(ClimateBridge)
    bridge.config = Mock(base_topic=BASE)
    bridge.mqtt = Mock()
    bridge.diagnostics = Mock()
    bridge.pending_temperature = None
    bridge.last_state = {}
    bridge.last_published_state = {
        "power": "on",
        "mode": "cool",
        "temperature": previous_temperature,
        "current_temperature": 16.0,
        "fan": "auto",
        "swing": "off",
        "turbo": "OFF",
        "eco": "OFF",
        "health": "OFF",
        "display": "ON",
        "sleep": "OFF",
    }
    return bridge


def _state(mode: str, temperature: float | None) -> dict[str, object]:
    state: dict[str, object] = {
        "power": True,
        "mode": mode,
        "indoor_temperature": 16.0,
        "fan": "auto",
        "swing": "off",
        "turbo": False,
        "eco": False,
        "health": False,
        "display": True,
        "sleep": False,
    }
    if temperature is not None:
        state["temperature"] = temperature
    return state


@pytest.mark.parametrize("mode", ("dry", "fan_only"))
def test_non_applicable_mode_resets_retained_setpoint_without_formatting(mode):
    bridge = _bridge()

    bridge.publish_state(_state(mode, None))

    bridge.mqtt.publish.assert_any_call(
        f"{BASE}/temperature/state", None, retain=True
    )
    bridge.mqtt.publish.assert_any_call(
        f"{BASE}/current_temperature/state", 16.0, retain=True
    )
    bridge.mqtt.publish.assert_any_call(
        f"{BASE}/activity/target_temperature", "", retain=True
    )
    assert bridge.last_published_state["temperature"] is None


@pytest.mark.parametrize("mode", ("dry", "fan_only"))
def test_first_poll_after_restart_always_resets_stale_broker_setpoint(mode):
    bridge = _bridge(previous_temperature=None)
    bridge.last_published_state = {}

    bridge.publish_state(_state(mode, None))

    bridge.mqtt.publish.assert_any_call(
        f"{BASE}/temperature/state", None, retain=True
    )


@pytest.mark.parametrize("mode", ("heat", "cool"))
def test_temperature_mode_restores_numeric_setpoint(mode):
    bridge = _bridge(previous_temperature=None)
    bridge.last_published_state["mode"] = "dry"
    bridge.last_published_state["temperature"] = None

    bridge.publish_state(_state(mode, 22.5))

    bridge.mqtt.publish.assert_any_call(
        f"{BASE}/temperature/state", 22.5, retain=True
    )
    bridge.mqtt.publish.assert_any_call(
        f"{BASE}/activity/target_temperature", 22.5, retain=True
    )
    assert bridge.last_published_state["temperature"] == 22.5


def test_mqtt_manager_serialises_none_as_home_assistant_reset_payload():
    manager = object.__new__(MqttManager)
    manager.connected = True
    manager.client = Mock()
    manager.client.publish.return_value = Mock(rc=0)

    assert manager.publish(f"{BASE}/temperature/state", None, retain=True) is True

    manager.client.publish.assert_called_once_with(
        f"{BASE}/temperature/state", "None", retain=True
    )
