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

from configuration import Config, load_config
from diagnostics_manager import DiagnosticsManager, utc_now
from direct_power_manager import DirectPowerManager
from direct_fan_manager import DirectFanManager
from direct_swing_manager import DirectSwingManager
from direct_read_manager import DirectReadManager
from direct_temperature_manager import DirectTemperatureManager
from discovery_manager import DiscoveryManager
from mqtt_manager import MqttManager
from transport import create_transport
from recovery_manager import RecoveryManager
from health_manager import HealthManager
from version import APP_NAME, APP_VERSION
from version import ADAPTER_NAME
LOG = logging.getLogger("climate_bridge")
READY_FILE = Path("/tmp/climate_bridge.ready")
HEARTBEAT_FILE = Path("/tmp/climate_bridge.heartbeat")


class NativeCommandRejected(RuntimeError):
    """A requested command did not match a qualified native write envelope."""

# Compatibility import for third-party tests written against Alpha.58.
RelayFreeCommandRejected = NativeCommandRejected


def log_startup_banner(config: Config, transport_name: str) -> None:
    """Write a compact, credential-free startup summary."""
    lines = [
        "=" * 57,
        f"{APP_NAME:^57}",
        f"Version {APP_VERSION:^49}",
        "=" * 57,
        f"Adapter      : {ADAPTER_NAME}",
        (
            "Transport    : Native LAN (no Relay runtime)"
            if config.direct_read_enabled
            else f"Transport    : {transport_name}"
        ),
        f"Device       : {config.device_name}",
        f"MQTT Broker  : {config.mqtt_host}:{config.mqtt_port}",
        f"MQTT Topic   : {config.base_topic}",
        f"Discovery    : {config.discovery_prefix}",
        (
            "Direct Temp : enabled (guarded)"
            if config.direct_control_enabled
            else "Direct Temp : disabled"
        ),
        (
            "Direct Power: enabled (guarded)"
            if config.direct_power_control_enabled
            else "Direct Power: disabled"
        ),
        (
            "Direct Mode : enabled (guarded)"
            if config.direct_power_control_enabled
            else "Direct Mode : disabled"
        ),
        (
            "Direct Fan  : enabled (Low/High guarded)"
            if config.direct_control_enabled
            else "Direct Fan  : disabled"
        ),
        (
            "Direct Swing: enabled (guarded; grouped Heat matrix)"
            if config.direct_control_enabled
            else "Direct Swing: disabled"
        ),
        (
            "State Source : authenticated direct LAN read"
            if config.direct_read_enabled
            else "State Source : configured transport"
        ),
        "=" * 57,
    ]
    for line in lines:
        LOG.info(line)



class ClimateBridge:
    def __init__(self, config: Config) -> None:
        self.config = config
        self.stop_event = threading.Event()
        self.command_lock = threading.Lock()
        self.transport = create_transport(config)
        self.mqtt = MqttManager(
            config,
            on_message=self.on_mqtt_message,
            on_connected=self.on_mqtt_connected,
            on_disconnected=self.on_mqtt_disconnected,
        )
        self.diagnostics = DiagnosticsManager(
            diagnostic_base=f"{config.base_topic}/diagnostic",
            app_version=APP_VERSION,
            publish_fn=self._publish_adapter,
        )
        self.diagnostics.transport_type = self.transport.name
        self.diagnostics.debug_mode = "enabled" if config.debug_enabled else "disabled"
        self.diagnostics.native_compare_status = "waiting" if config.debug_enabled and config.debug_native_compare else "disabled"
        self.direct_read = DirectReadManager(config) if config.direct_read_enabled else None
        self.direct_temperature = (
            DirectTemperatureManager(config)
            if config.direct_control_enabled
            else None
        )
        self.direct_power = (
            DirectPowerManager(config)
            if config.direct_power_control_enabled
            else None
        )
        self.direct_fan = (
            DirectFanManager(config)
            if config.direct_control_enabled
            else None
        )
        self.direct_swing = (
            DirectSwingManager(config)
            if config.direct_control_enabled
            else None
        )
        if self.direct_read is not None:
            self.diagnostics.native_compare_status = "waiting"
            self.diagnostics.native_probe_status = "waiting"
        self.discovery = DiscoveryManager(config, APP_VERSION, self._publish_adapter)
        self.recovery = RecoveryManager()
        self.health = HealthManager()
        self.consecutive_poll_failures = 0
        self.authoritative_state_confirmed = False
        self.ready = False
        self.last_state: dict[str, Any] = {}
        self.last_published_state: dict[str, Any] = {}
        self.pending_temperature: float | None = None

    def _record_authoritative_read(self, result: Any) -> None:
        """Record direct-read evidence without importing Relay state."""

        self.diagnostics.native_probe_status = (
            f"pass ({result.udp_sends} UDP sends, 0 retries)"
        )
        self.diagnostics.native_compare_status = result.comparison
        self.diagnostics.native_response_length = result.response_length
        self.diagnostics.native_last_probe = utc_now()
        self.diagnostics.publish("state_source", "direct_lan_authoritative")
        native_payload = dict(result.state)
        native_payload["_diagnostic"] = {
            "authority": "direct_lan",
            "raw_frame_hex": result.raw_frame_hex,
            "fan_status_byte": result.fan_status_byte,
            "fan_status_nibble": result.fan_status_nibble,
        }
        self.mqtt.publish(
            f"{self.config.base_topic}/diagnostic/native_state",
            json.dumps(native_payload, sort_keys=True),
            retain=True,
        )
        LOG.info(
            "Direct LAN authoritative read passed: %s; %s; "
            "fan=%r status_byte=%s status_nibble=%s; temperature=%r",
            self.diagnostics.native_probe_status,
            result.comparison,
            result.state.get("fan"),
            (
                f"0x{result.fan_status_byte:02X}"
                if result.fan_status_byte is not None
                else "unknown"
            ),
            (
                f"0x{result.fan_status_nibble:X}"
                if result.fan_status_nibble is not None
                else "unknown"
            ),
            result.state.get("temperature"),
        )

    def _read_authoritative_state(self) -> dict[str, Any]:
        if self.direct_read is None:
            raise RuntimeError("direct LAN state authority is not enabled")
        result = self.direct_read.read_authoritative()
        self._record_authoritative_read(result)
        return dict(result.state)

    def _refresh_command_guard_state(self) -> None:
        """Require fresh direct evidence before choosing any command path."""

        if getattr(self, "direct_read", None) is not None:
            self.last_state = self._read_authoritative_state()

    def _publish_adapter(self, topic: str, payload: Any, retain: bool = True) -> bool:
        return self.mqtt.publish(topic, payload, retain=retain)

    def on_mqtt_connected(self, reconnect: bool) -> None:
        self.diagnostics.mqtt_status = "connected"
        if reconnect:
            self.diagnostics.mqtt_reconnect_count += 1
        self.mqtt.publish(f"{self.config.base_topic}/bridge/availability", "online", retain=True)
        if self.direct_read is not None:
            # An MQTT session is not proof that the York module is reachable.
            # Keep the climate entity unavailable until the poll loop completes
            # a fresh authenticated read. This is especially important after a
            # container or broker restart.
            self.authoritative_state_confirmed = False
            self.mqtt.publish(
                f"{self.config.base_topic}/availability", "offline", retain=True
            )
            self.diagnostics.publish("state_source_status", "validating")
        else:
            self.mqtt.publish(
                f"{self.config.base_topic}/availability", "online", retain=True
            )
        self.discovery.publish_all()
        if not self.ready:
            self.diagnostics.bridge_status = "ready"
            self._update_health()
            self.diagnostics.initialize()
            self.diagnostics.record_event("INFO", "Bridge ready")
            self.diagnostics.publish_metrics()
            self.ready = True
            READY_FILE.touch()
            LOG.info("Bridge READY")
        else:
            self.diagnostics.bridge_status = (
                "recovering" if self.direct_read is not None else "ready"
            )
            self._update_health()
            event = (
                "MQTT restored; direct LAN state validation pending"
                if self.direct_read is not None
                else "MQTT connection restored"
            )
            self.diagnostics.record_event("RECOVERY", event)
            self.diagnostics.publish_metrics()
            if self.direct_read is not None:
                LOG.info(
                    "Bridge MQTT session restored; direct LAN validation pending"
                )
            else:
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
            relay_offline_after_failures=self.config.transport_offline_after_failures,
            average_command_time_ms=self.diagnostics.average_command_time_ms,
            bridge_status=self.diagnostics.bridge_status,
            state_source_label=(
                "Direct LAN state source"
                if self.direct_read is not None
                else "Active transport"
            ),
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
        except NativeCommandRejected as error:
            # Republish the fresh direct state read by execute_command so Home
            # Assistant cannot retain an optimistic value for a rejected
            # unqualified control.
            if self.last_state:
                self.publish_state(self.last_state)
            LOG.warning("Command rejected by native safety boundary: %s", error)
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
        self.diagnostics.command_count += 1

        # Every command starts from a fresh authenticated direct read.
        self._refresh_command_guard_state()

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
        def reject(reason: str) -> None:
            message = (
                "command is outside the qualified native allowlist; "
                f"native command rejected ({reason})"
            )
            self.diagnostics.command_failure_count += 1
            self.diagnostics.last_error = f"command rejected: {message}"
            self.diagnostics.publish_command(
                command_json=command_json,
                result=f"rejected: {message}",
            )
            severity = "CRITICAL" if "CRITICAL:" in reason else "WARNING"
            self.diagnostics.record_event(severity, "Native command rejected")
            if severity == "CRITICAL":
                LOG.critical("Native command critical verification failure: %s", reason)
            self.diagnostics.publish_metrics()
            raise NativeCommandRejected(message)

        direct_power = getattr(self, "direct_power", None)
        if direct_power is not None and set(effective_command) in (
            {"power"},
            {"power", "mode"},
        ):
            try:
                response = direct_power.command(
                    effective_command,
                    self.last_state,
                )
                return self._complete_command_response(
                    response,
                    command_json,
                    applying_pending_temperature,
                )
            except Exception as error:
                reject(f"{type(error).__name__}: {error}")

        if (
            self.direct_temperature is not None
            and set(effective_command) == {"temperature"}
        ):
            try:
                response = self.direct_temperature.command(
                    float(effective_command["temperature"]),
                    self.last_state,
                )
                return self._complete_command_response(
                    response,
                    command_json,
                    applying_pending_temperature,
                )
            except Exception as error:
                reject(f"{type(error).__name__}: {error}")

        direct_fan = getattr(self, "direct_fan", None)
        if direct_fan is not None and set(effective_command) == {"fan"}:
            try:
                response = direct_fan.command(
                    str(effective_command["fan"]),
                    self.last_state,
                )
                return self._complete_command_response(
                    response,
                    command_json,
                    applying_pending_temperature,
                )
            except Exception as error:
                reject(f"{type(error).__name__}: {error}")

        direct_swing = getattr(self, "direct_swing", None)
        if direct_swing is not None and set(effective_command) == {"swing"}:
            try:
                response = direct_swing.command(
                    str(effective_command["swing"]),
                    self.last_state,
                )
                return self._complete_command_response(
                    response,
                    command_json,
                    applying_pending_temperature,
                )
            except Exception as error:
                reject(f"{type(error).__name__}: {error}")

        reject("no qualified native command path")

    def _complete_command_response(
        self,
        response: dict[str, Any],
        command_json: str,
        applying_pending_temperature: bool,
    ) -> dict[str, Any]:
        transaction = response.get("_transaction", {})
        success = bool(transaction.get("success", True))
        result = "success" if success else "verification_failed"
        if not success:
            self.diagnostics.bridge_status = "error"
            self.diagnostics.command_failure_count += 1
            self.diagnostics.last_error = "command verification failed"
            LOG.warning("Command returned verification mismatch: %s", transaction)
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
                None
                if mode in {"dry", "fan_only"}
                else (
                    self.pending_temperature
                    if self.pending_temperature is not None and not state.get("power")
                    else state.get("temperature")
                )
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
            if key == "power":
                continue
            if key == "temperature" and value is None:
                # Home Assistant's MQTT climate integration uses the literal
                # payload "None" to reset a target setpoint.  Publish it on
                # every Dry/Fan-only state, including the first poll after a
                # restart, so an older retained Heat/Cool value cannot survive.
                self.mqtt.publish(f"{base}/{key}/state", None, retain=True)
            elif value is not None:
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
                if value is None:
                    # A non-applicable setpoint is a valid semantic transition,
                    # not a numeric temperature event.  Clear the retained
                    # activity value and never pass None to the formatter.
                    if source_key == "temperature":
                        self.mqtt.publish(
                            f"{base}/activity/{activity_key}", "", retain=True
                        )
                    changed = True
                    continue
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
        self.diagnostics.publish("transport_status", "connected")
        # Avoid flooding the Home Assistant activity panel: this timestamp now
        # represents a meaningful state change, not every routine poll.
        if changed:
            self.diagnostics.publish("last_state_change_timestamp", utc_now())

    def poll_once(self) -> None:
        started = time.monotonic()
        with self.command_lock:
            if self.direct_read is not None:
                # Direct LAN state is authoritative in Alpha.55. Relay v2 is
                # not read during polling and remains command-fallback only.
                state = self._read_authoritative_state()
            else:
                state = self.transport.get_state()
        self.diagnostics.record_poll_duration((time.monotonic() - started) * 1000)
        self.diagnostics.poll_count += 1
        self.diagnostics.record_stability_event(True)
        had_failures = self.consecutive_poll_failures > 0 or self.recovery.active
        self.consecutive_poll_failures = 0
        self.authoritative_state_confirmed = self.direct_read is not None
        self.diagnostics.last_error = "none"
        self.diagnostics.bridge_status = "ready"
        if had_failures and self.recovery.complete():
            self._sync_recovery_diagnostics()
            source = "Direct LAN state" if self.direct_read is not None else "Transport"
            self.diagnostics.record_event("RECOVERY", f"{source} restored in {self.recovery.last_duration_ms} ms")
            LOG.info("%s recovered in %s ms", source, self.recovery.last_duration_ms)
        if self.direct_read is not None:
            self.diagnostics.publish("state_source_status", "authoritative")
        self._update_health()
        self.publish_state(state)

    def _observe_direct_read(self, relay_state: dict[str, Any]) -> None:
        if self.direct_read is None:
            return
        try:
            result = self.direct_read.observe(relay_state)
            if result is None:
                return
            self.diagnostics.native_probe_status = (
                f"pass ({result.udp_sends} UDP sends, 0 retries)"
            )
            self.diagnostics.native_compare_status = result.comparison
            self.diagnostics.native_response_length = result.response_length
            self.diagnostics.native_last_probe = utc_now()
            native_payload = dict(result.state)
            native_payload["_diagnostic"] = {
                "raw_frame_hex": result.raw_frame_hex,
                "fan_status_byte": result.fan_status_byte,
                "fan_status_nibble": result.fan_status_nibble,
                "relay_fan": relay_state.get("fan"),
                "direct_fan": result.state.get("fan"),
                "relay_temperature": relay_state.get("temperature"),
                "direct_temperature": result.state.get("temperature"),
            }
            self.mqtt.publish(
                f"{self.config.base_topic}/diagnostic/native_state",
                json.dumps(native_payload, sort_keys=True),
                retain=True,
            )
            LOG.info(
                "Direct LAN read passed: %s; %s; "
                "fan relay=%r direct=%r status_byte=%s status_nibble=%s; "
                "temperature relay=%r direct=%r",
                self.diagnostics.native_probe_status,
                result.comparison,
                relay_state.get("fan"),
                result.state.get("fan"),
                (
                    f"0x{result.fan_status_byte:02X}"
                    if result.fan_status_byte is not None
                    else "unknown"
                ),
                (
                    f"0x{result.fan_status_nibble:X}"
                    if result.fan_status_nibble is not None
                    else "unknown"
                ),
                relay_state.get("temperature"),
                result.state.get("temperature"),
            )
        except Exception as error:
            self.diagnostics.native_probe_status = f"error: {type(error).__name__}"
            self.diagnostics.native_compare_status = "unavailable"
            self.diagnostics.native_last_probe = utc_now()
            LOG.warning("Direct LAN read observation failed: %s", error)

    def _handle_poll_failure(self, error: Exception) -> None:
        """Record a failed poll without making Relay availability authoritative."""

        self.diagnostics.poll_error_count += 1
        self.diagnostics.record_stability_event(False)
        self.consecutive_poll_failures += 1
        self.diagnostics.last_error = f"poll: {type(error).__name__}: {error}"
        self.diagnostics.bridge_status = "recovering"
        recovery_reason = (
            f"Direct LAN state read: {type(error).__name__}: {error}"
            if self.direct_read is not None
            else self.diagnostics.last_error
        )
        self.recovery.begin(recovery_reason)
        source = "Direct LAN state" if self.direct_read is not None else "Transport"
        displayed_failure_count = min(
            self.consecutive_poll_failures,
            self.config.transport_offline_after_failures,
        )
        self.diagnostics.record_event(
            "WARNING", f"{source} communication interrupted"
        )
        self._sync_recovery_diagnostics()
        LOG.warning(
            "Transport poll failed (%s/%s): %s",
            displayed_failure_count,
            self.config.transport_offline_after_failures,
            error,
        )
        self.diagnostics.publish(
            "transport_status", f"retrying ({displayed_failure_count})"
        )
        if self.direct_read is not None:
            self.diagnostics.publish(
                "state_source_status",
                f"retrying ({displayed_failure_count})",
            )
        if (
            self.consecutive_poll_failures
            >= self.config.transport_offline_after_failures
        ):
            self.authoritative_state_confirmed = False
            LOG.error("%s considered unavailable after repeated failures", source)
            self.mqtt.publish(
                f"{self.config.base_topic}/availability", "offline", retain=True
            )
            self.diagnostics.publish("transport_status", "unavailable")
            if self.direct_read is not None:
                self.diagnostics.publish("state_source_status", "unavailable")
            self.diagnostics.bridge_status = "error"
            self.recovery.fail(self.diagnostics.last_error)
            self.diagnostics.record_event("ERROR", f"{source} unavailable")
            self._sync_recovery_diagnostics()

    def poll_loop(self) -> None:
        while not self.stop_event.is_set():
            HEARTBEAT_FILE.touch()
            if not self.mqtt.connected:
                LOG.debug("MQTT unavailable; pausing transport polling")
                self.stop_event.wait(1)
                continue
            try:
                if self.discovery.due():
                    self.discovery.publish_all()
                self.poll_once()
            except Exception as error:
                self._handle_poll_failure(error)
            self._update_health()
            self.diagnostics.publish_metrics()
            HEARTBEAT_FILE.touch()
            self.stop_event.wait(self.config.poll_seconds)

    def run(self) -> None:
        self.diagnostics.record_event("INFO", "Bridge starting")
        log_startup_banner(self.config, self.transport.display_name)
        LOG.info("%s %s starting", APP_NAME, APP_VERSION)
        READY_FILE.unlink(missing_ok=True)
        HEARTBEAT_FILE.touch()
        self.mqtt.start()
        if not self.mqtt.wait_until_connected():
            LOG.error(
                "MQTT did not connect within %.0f seconds; automatic retries will continue",
                self.config.startup_connect_timeout_seconds,
            )
        try:
            self.poll_loop()
        finally:
            READY_FILE.unlink(missing_ok=True)
            HEARTBEAT_FILE.unlink(missing_ok=True)
            if self.direct_read is not None:
                self.direct_read.close()
            self.transport.close()
            self.mqtt.stop()

    def stop(self) -> None:
        self.stop_event.set()


# Historical public name retained for downstream integrations.
YorkBridge = ClimateBridge


def main() -> int:
    config_path = Path(sys.argv[1] if len(sys.argv) > 1 else "/config/config.yml")
    if not config_path.is_file():
        print(f"Config file not found: {config_path}", file=sys.stderr)
        return 2

    config = load_config(config_path)
    logging.basicConfig(
        level=getattr(logging, config.log_level, logging.INFO),
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )
    bridge = ClimateBridge(config)

    def shutdown(signum: int, frame: object) -> None:
        LOG.info("Stopping on signal %s", signum)
        bridge.stop()

    signal.signal(signal.SIGTERM, shutdown)
    signal.signal(signal.SIGINT, shutdown)
    bridge.run()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
