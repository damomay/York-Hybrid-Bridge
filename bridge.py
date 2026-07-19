from __future__ import annotations

import json
import logging
import signal
import sys
import threading
import time
from pathlib import Path
from typing import Any

import paho.mqtt.client as mqtt

from configuration import Config, ConfigError, load_config
from diagnostics_manager import DiagnosticsManager, utc_now
from discovery_manager import DiscoveryManager
from mqtt_manager import MqttManager
from relay_manager import RelayManager
from recovery_manager import RecoveryManager
from health_manager import HealthManager
from version import __version__
LOG = logging.getLogger("york_bridge")


class YorkBridge:
    """Coordinate MQTT, relay, discovery, diagnostics, recovery, and health."""

    def __init__(self, config: Config) -> None:
        self.config = config
        self.stop_event = threading.Event()
        self.command_lock = threading.Lock()
        self.relay = RelayManager(config)
        self.mqtt = MqttManager(
            config,
            on_message=self.on_mqtt_message,
            on_connected=self.on_mqtt_connected,
            on_disconnected=self.on_mqtt_disconnected,
        )
        self.diagnostics = DiagnosticsManager(
            diagnostic_base=f"{config.base_topic}/diagnostic",
            app_version=__version__,
            publish_fn=self._publish_adapter,
        )
        self.discovery = DiscoveryManager(config, __version__, self._publish_adapter)
        self.recovery = RecoveryManager()
        self.health = HealthManager()
        self.consecutive_poll_failures = 0
        self.ready = False
        self.last_state: dict[str, Any] = {}
        self.last_published_state: dict[str, Any] = {}
        self.pending_temperature: float | None = None

    def _publish_adapter(self, topic: str, payload: Any, retain: bool = True) -> bool:
        return self.mqtt.publish(topic, payload, retain=retain)

    def on_mqtt_connected(self, reconnect: bool) -> None:
        self.diagnostics.mqtt_status = "connected"
        if reconnect:
            self.diagnostics.mqtt_reconnect_count += 1
            self.recovery.complete()
            self._sync_recovery_diagnostics()
        self.mqtt.publish(f"{self.config.base_topic}/bridge/availability", "online", retain=True)
        self.mqtt.publish(f"{self.config.base_topic}/availability", "online", retain=True)
        self.discovery.publish_all()
        if not self.ready:
            self.diagnostics.bridge_status = "ready"
            self._update_health()
            self.diagnostics.initialize()
            self.diagnostics.record_event("INFO", "Bridge ready")
            self.diagnostics.publish_metrics()
            self.ready = True
            LOG.info("Bridge READY")
        else:
            self.diagnostics.bridge_status = "ready"
            self._update_health()
            self.diagnostics.record_event("RECOVERY", "MQTT connection restored")
            self.diagnostics.publish_metrics()
            LOG.info("Bridge MQTT session restored")

    def on_mqtt_disconnected(self, reason: str) -> None:
        self.diagnostics.mqtt_status = "reconnecting"
        self.diagnostics.bridge_status = "recovering"
        self.recovery.begin(f"MQTT disconnected: {reason}")
        self.diagnostics.record_event("WARNING", "MQTT connection lost")
        self._sync_recovery_diagnostics()
        self._update_health()

    def _sync_recovery_diagnostics(self) -> None:
        self.diagnostics.recovery_count = self.recovery.recovery_count
        self.diagnostics.last_recovery = self.recovery.last_recovery
        self.diagnostics.recovery_reason = self.recovery.last_reason
        self.diagnostics.recovery_failure_count = self.recovery.failure_count
        self.diagnostics.last_recovery_duration_ms = self.recovery.last_duration_ms
        self.diagnostics.average_recovery_time_ms = self.recovery.average_duration_ms
        self.diagnostics.longest_recovery_time_ms = self.recovery.longest_duration_ms

    def _update_health(self) -> None:
        snapshot = self.health.evaluate(
            mqtt_connected=self.mqtt.connected,
            consecutive_poll_failures=self.consecutive_poll_failures,
            relay_offline_after_failures=self.config.relay_offline_after_failures,
            average_command_time_ms=self.diagnostics.average_command_time_ms,
            bridge_status=self.diagnostics.bridge_status,
        )
        self.diagnostics.health_score = snapshot.score
        self.diagnostics.health_status = snapshot.status
        self.diagnostics.health_reason = snapshot.reason

    def on_mqtt_message(self, message: mqtt.MQTTMessage) -> None:
        try:
            leaf = message.topic.removeprefix(f"{self.config.base_topic}/").removesuffix("/set")
            payload = message.payload.decode("utf-8").strip()
            LOG.info("Command %s=%s", leaf, payload)
            command = self.command_from_topic(leaf, payload)
            if command is None:
                return
            with self.command_lock:
                response = self.execute_command(command)
                self.publish_state(response)
        except Exception as error:
            self.diagnostics.last_error = f"command: {type(error).__name__}: {error}"
            self.diagnostics.publish_metrics()
            LOG.exception("Failed to handle MQTT command")

    def command_from_topic(self, leaf: str, payload: str) -> dict[str, Any] | None:
        if leaf == "mode":
            if payload == "off":
                return {"power": False}
            return {"power": True, "mode": payload}
        if leaf == "temperature":
            return {"temperature": float(payload)}
        if leaf == "fan":
            return {"fan": payload}
        if leaf == "swing":
            return {"swing": payload}
        if leaf in {"turbo", "eco", "health", "display", "sleep"}:
            return {leaf: payload.upper() == "ON"}
        LOG.warning("Unknown command topic: %s", leaf)
        return None

    def execute_command(self, command: dict[str, Any]) -> dict[str, Any]:
        cfg = self.config
        last_error: Exception | None = None
        self.diagnostics.command_count += 1

        # The TFIAC unit rejects setpoint-only commands while powered off. Treat
        # this as a valid deferred request rather than a transport failure.
        if set(command) == {"temperature"} and self.last_state and not bool(self.last_state.get("power")):
            self.pending_temperature = float(command["temperature"])
            command_json = json.dumps(command, sort_keys=True)
            self.diagnostics.command_deferred_count += 1
            self.diagnostics.last_error = "none"
            self.diagnostics.publish_command(command_json=command_json, result="deferred")
            self.diagnostics.record_event(
                "INFO",
                f"Temperature {self.pending_temperature:g} °C deferred until power on",
            )
            self.diagnostics.publish_metrics()
            deferred_state = dict(self.last_state)
            deferred_state["temperature"] = self.pending_temperature
            return deferred_state

        # Apply a setpoint selected while off as part of the next power-on/mode
        # transaction, which the unit accepts and confirms reliably.
        effective_command = dict(command)
        applying_pending_temperature = bool(effective_command.get("power")) and self.pending_temperature is not None
        if applying_pending_temperature and "temperature" not in effective_command:
            effective_command["temperature"] = self.pending_temperature

        command_json = json.dumps(command, sort_keys=True)
        self.diagnostics.publish_command(command_json=command_json, result="running")
        self.diagnostics.publish_metrics()

        for attempt in range(cfg.command_retries + 1):
            try:
                response = self.relay.command(**effective_command)
                transaction = response.get("_transaction", {})
                success = bool(transaction.get("success", True))
                result = "success" if success else "verification_failed"
                if not success:
                    self.diagnostics.bridge_status = "error"
                    self.diagnostics.command_failure_count += 1
                    self.diagnostics.last_error = "command verification failed"
                    LOG.warning("Relay returned verification mismatch: %s", transaction)
                else:
                    self.diagnostics.bridge_status = "ready"
                    self.diagnostics.last_error = "none"
                self.diagnostics.publish_command(
                    command_json=command_json,
                    result=result,
                    transaction=transaction,
                )
                if success and applying_pending_temperature:
                    self.pending_temperature = None
                if success:
                    self.last_state = dict(response)
                if transaction:
                    self.mqtt.publish(
                        f"{self.config.base_topic}/last_transaction",
                        json.dumps(transaction, sort_keys=True),
                        retain=True,
                    )
                self.diagnostics.record_stability_event(success)
                self._update_health()
                self.diagnostics.publish_metrics()
                return response
            except Exception as error:
                last_error = error
                LOG.warning(
                    "Command attempt %s/%s failed: %s",
                    attempt + 1,
                    cfg.command_retries + 1,
                    error,
                )
                if attempt < cfg.command_retries:
                    self.stop_event.wait(cfg.retry_delay_seconds)

        self.diagnostics.bridge_status = "error"
        self.diagnostics.command_failure_count += 1
        self.diagnostics.last_error = f"command: {type(last_error).__name__}: {last_error}"
        self.diagnostics.publish_command(command_json=command_json, result=f"failed: {last_error}")
        self.diagnostics.record_stability_event(False)
        self._update_health()
        self.diagnostics.publish_metrics()
        if last_error is not None:
            raise last_error
        raise RuntimeError("Command failed without an exception")

    def _publish_ac_activity(self, key: str, value: Any, event_text: str | None = None) -> None:
        base = f"{self.config.base_topic}/activity"
        self.mqtt.publish(f"{base}/{key}", value, retain=True)
        if event_text:
            self.mqtt.publish(f"{base}/last_event", event_text, retain=True)

    def publish_state(self, state: dict[str, Any]) -> None:
        base = self.config.base_topic
        self.last_state = dict(state)
        mode = state.get("mode", "off") if state.get("power") else "off"
        values = {
            "power": "on" if state.get("power") else "off",
            "mode": mode,
            "temperature": (
                self.pending_temperature
                if self.pending_temperature is not None and not state.get("power")
                else state.get("temperature")
            ),
            "current_temperature": state.get("indoor_temperature"),
            "fan": state.get("fan", "auto"),
            "swing": state.get("swing", "off"),
            "turbo": "ON" if state.get("turbo") else "OFF",
            "eco": "ON" if state.get("eco") else "OFF",
            "health": "ON" if state.get("health") else "OFF",
            "display": "ON" if state.get("display") else "OFF",
            "sleep": "ON" if state.get("sleep") else "OFF",
        }
        for key, value in values.items():
            if value is not None and key != "power":
                self.mqtt.publish(f"{base}/{key}/state", value, retain=True)

        activity_map = {
            "power": ("power_state", lambda v: f"Power changed to {str(v).upper()}"),
            "temperature": ("target_temperature", lambda v: f"Target temperature changed to {v:g} °C"),
            "mode": ("operating_mode", lambda v: f"Operating mode changed to {str(v).replace('_', ' ').title()}"),
            "fan": ("fan_mode", lambda v: f"Fan mode changed to {str(v).title()}"),
            "swing": ("swing_mode", lambda v: f"Swing mode changed to {str(v).title()}"),
        }
        changed = False
        for source_key, (activity_key, formatter) in activity_map.items():
            value = values.get(source_key)
            previous = self.last_published_state.get(source_key)
            if value is not None:
                self._publish_ac_activity(activity_key, value)
            if previous is not None and value != previous:
                event_text = formatter(value)
                if source_key == "temperature" and self.pending_temperature is not None and not state.get("power"):
                    event_text = f"Target temperature changed to {float(value):g} °C (deferred)"
                self._publish_ac_activity(activity_key, value, event_text)
                changed = True

        # Feature switches already have their own entities, but also update the
        # concise AC event sensor when their physical state changes.
        for key in ("turbo", "eco", "health", "display", "sleep"):
            value = values[key]
            previous = self.last_published_state.get(key)
            if previous is not None and value != previous:
                label = key.title()
                self._publish_ac_activity("last_event", f"{label} changed to {value}")
                changed = True

        first_state = not self.last_published_state
        self.last_published_state = dict(values)
        if first_state:
            self._publish_ac_activity("last_event", "AC state synchronised")
            changed = True

        self.mqtt.publish(f"{base}/raw_state", json.dumps(state, sort_keys=True), retain=True)
        self.mqtt.publish(f"{base}/availability", "online", retain=True)
        self.diagnostics.publish("relay_status", "connected")
        # Avoid flooding the Home Assistant activity panel: this timestamp now
        # represents a meaningful state change, not every routine poll.
        if changed:
            self.diagnostics.publish("last_state_change_timestamp", utc_now())

    def poll_once(self) -> None:
        started = time.monotonic()
        with self.command_lock:
            state = self.relay.get_state()
        self.diagnostics.record_poll_duration((time.monotonic() - started) * 1000)
        self.diagnostics.poll_count += 1
        self.diagnostics.record_stability_event(True)
        had_failures = self.consecutive_poll_failures > 0
        self.consecutive_poll_failures = 0
        self.diagnostics.last_error = "none"
        self.diagnostics.bridge_status = "ready"
        if had_failures and self.recovery.complete():
            self._sync_recovery_diagnostics()
            self.diagnostics.record_event("RECOVERY", f"Relay communication restored in {self.recovery.last_duration_ms} ms")
            LOG.info("Relay communication recovered in %s ms", self.recovery.last_duration_ms)
        self._update_health()
        self.publish_state(state)

    def poll_loop(self) -> None:
        while not self.stop_event.is_set():
            if not self.mqtt.connected:
                LOG.debug("MQTT unavailable; pausing relay polling")
                self.stop_event.wait(1)
                continue
            try:
                if self.discovery.due():
                    self.discovery.publish_all()
                self.poll_once()
            except Exception as error:
                self.diagnostics.poll_error_count += 1
                self.diagnostics.record_stability_event(False)
                self.consecutive_poll_failures += 1
                self.diagnostics.last_error = f"poll: {type(error).__name__}: {error}"
                self.diagnostics.bridge_status = "recovering"
                self.recovery.begin(self.diagnostics.last_error)
                self.diagnostics.record_event("WARNING", "Tablet relay communication interrupted")
                self._sync_recovery_diagnostics()
                LOG.warning(
                    "Relay poll failed (%s/%s): %s",
                    self.consecutive_poll_failures,
                    self.config.relay_offline_after_failures,
                    error,
                )
                self.diagnostics.publish("relay_status", f"retrying ({self.consecutive_poll_failures})")
                if self.consecutive_poll_failures >= self.config.relay_offline_after_failures:
                    LOG.error("Relay considered unavailable after repeated failures")
                    self.mqtt.publish(f"{self.config.base_topic}/availability", "offline", retain=True)
                    self.diagnostics.publish("relay_status", "unavailable")
                    self.diagnostics.bridge_status = "error"
                    self.recovery.fail(self.diagnostics.last_error)
                    self.diagnostics.record_event("ERROR", "Tablet relay unavailable")
                    self._sync_recovery_diagnostics()
            self._update_health()
            self.diagnostics.publish_metrics()
            self.stop_event.wait(self.config.poll_seconds)

    def run(self) -> None:
        self.diagnostics.record_event("INFO", "Bridge starting")
        LOG.info("York Hybrid Bridge %s starting", __version__)
        LOG.info("Starting MQTT connection")
        self.mqtt.start()
        if not self.mqtt.wait_until_connected():
            LOG.error(
                "MQTT did not connect within %.0f seconds; automatic retries will continue",
                self.config.startup_connect_timeout_seconds,
            )
        try:
            self.poll_loop()
        finally:
            self.mqtt.stop()

    def stop(self) -> None:
        self.stop_event.set()


def main() -> int:
    config_path = Path(sys.argv[1] if len(sys.argv) > 1 else "/config/config.yml")
    if not config_path.is_file():
        print(f"Config file not found: {config_path}", file=sys.stderr)
        return 2

    try:
        config = load_config(config_path)
    except ConfigError as error:
        print(f"Configuration error: {error}", file=sys.stderr)
        return 2

    logging.basicConfig(
        level=getattr(logging, config.log_level, logging.INFO),
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )
    bridge = YorkBridge(config)

    def shutdown(signum: int, frame: object) -> None:
        LOG.info("Stopping on signal %s", signum)
        bridge.stop()

    signal.signal(signal.SIGTERM, shutdown)
    signal.signal(signal.SIGINT, shutdown)
    bridge.run()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())