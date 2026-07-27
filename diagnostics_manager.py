from __future__ import annotations

import time
from collections import deque
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Callable

PublishFn = Callable[[str, Any, bool], bool]

DEFAULT_STABILITY_WINDOW = 100
MIN_STABILITY_WINDOW = 10
STABILITY_EXCELLENT = 99.0
STABILITY_GOOD = 95.0
STABILITY_WARNING = 85.0
TREND_THRESHOLD = 0.2
SLOW_POLL_WARNING_MS = 2_000


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def format_duration(seconds: int) -> str:
    seconds = max(0, int(seconds))
    days, remainder = divmod(seconds, 86400)
    hours, remainder = divmod(remainder, 3600)
    minutes, secs = divmod(remainder, 60)
    parts: list[str] = []
    if days:
        parts.append(f"{days}d")
    if hours or days:
        parts.append(f"{hours}h")
    if minutes or hours or days:
        parts.append(f"{minutes}m")
    parts.append(f"{secs}s")
    return " ".join(parts)


def relative_timestamp(value: str) -> str:
    if not value or value == "never":
        return "Never"
    try:
        timestamp = datetime.fromisoformat(value.replace("Z", "+00:00"))
        age_seconds = max(
            0,
            int((datetime.now(timezone.utc) - timestamp).total_seconds()),
        )
    except (TypeError, ValueError):
        return "Unknown"
    if age_seconds < 60:
        return f"{age_seconds}s ago"
    if age_seconds < 3600:
        return f"{age_seconds // 60}m ago"
    if age_seconds < 86400:
        return f"{age_seconds // 3600}h ago"
    return f"{age_seconds // 86400}d ago"


@dataclass
class DiagnosticsManager:
    """Maintain bridge diagnostics, metrics and MQTT diagnostic entities."""

    diagnostic_base: str
    app_version: str
    publish_fn: PublishFn
    started_monotonic: float = field(default_factory=time.monotonic)
    poll_count: int = 0
    poll_error_count: int = 0
    command_count: int = 0
    command_failure_count: int = 0
    command_deferred_count: int = 0
    command_not_applicable_count: int = 0
    mqtt_reconnect_count: int = 0
    recovery_count: int = 0
    recovery_failure_count: int = 0
    successful_timed_commands: int = 0
    command_duration_total_ms: float = 0.0
    fastest_command_time_ms: int = 0
    slowest_command_time_ms: int = 0
    timed_polls: int = 0
    poll_duration_total_ms: float = 0.0
    last_poll_time_ms: int = 0
    average_poll_time_ms: int = 0
    fastest_poll_time_ms: int = 0
    slowest_poll_time_ms: int = 0
    last_error: str = "none"
    bridge_status: str = "starting"
    mqtt_status: str = "connecting"
    transport_type: str = "tablet_relay"
    last_recovery: str = "never"
    recovery_reason: str = "none"
    last_recovery_duration_ms: int = 0
    average_recovery_time_ms: int = 0
    longest_recovery_time_ms: int = 0
    health_score: int = 0
    health_status: str = "starting"
    health_reason: str = "Bridge is starting"
    stability_score: float = 100.0
    stability_status: str = "excellent"
    stability_trend: str = "stable"
    bridge_summary: str = "Bridge is starting"
    health_advisor: str = "Waiting for initial status"
    last_event: str = "INFO • Bridge starting"
    event_level: str = "INFO"
    event_message: str = "Bridge starting"
    protocol_name: str = "TFIAC 20014"
    discovery_status: str = "connected"
    uptime_text: str = "0s"
    last_recovery_age: str = "Never"
    stability_window_size: int = DEFAULT_STABILITY_WINDOW
    _stability_events: deque[bool] = field(
        default_factory=lambda: deque(maxlen=DEFAULT_STABILITY_WINDOW),
        repr=False,
    )

    def __post_init__(self) -> None:
        self._stability_events = deque(
            maxlen=max(MIN_STABILITY_WINDOW, int(self.stability_window_size))
        )

    @property
    def uptime_seconds(self) -> int:
        """Return bridge uptime using the monotonic clock."""
        return int(time.monotonic() - self.started_monotonic)

    def publish(self, key: str, value: Any, retain: bool = True) -> bool:
        return self.publish_fn(f"{self.diagnostic_base}/{key}", value, retain)

    def initialize(self) -> None:
        """Publish initial diagnostics and the first complete metric snapshot."""
        defaults = {
            "last_command": "No command sent yet",
            "last_command_result": "idle",
            "last_command_duration": "0",
            "last_transaction_id": "0",
            "relay_status": "starting",
            "transport_status": "starting",
            "last_state_change_timestamp": utc_now(),
            "bridge_version": self.app_version,
        }
        for key, value in defaults.items():
            self.publish(key, value)
        self.publish_metrics()

    @property
    def average_command_time_ms(self) -> int:
        if self.successful_timed_commands == 0:
            return 0
        return round(
            self.command_duration_total_ms / self.successful_timed_commands
        )

    @property
    def command_success_rate(self) -> float:
        applicable = (
            self.command_count
            - self.command_deferred_count
            - self.command_not_applicable_count
        )
        if applicable <= 0:
            return 100.0
        successful = max(0, applicable - self.command_failure_count)
        return round((successful / applicable) * 100, 1)

    @property
    def poll_success_rate(self) -> float:
        attempts = self.poll_count + self.poll_error_count
        return (
            100.0
            if attempts == 0
            else round((self.poll_count / attempts) * 100, 1)
        )

    @property
    def recovery_success_rate(self) -> float:
        attempts = self.recovery_count + self.recovery_failure_count
        return (
            100.0
            if attempts == 0
            else round((self.recovery_count / attempts) * 100, 1)
        )

    @staticmethod
    def _stability_status(score: float) -> str:
        if score >= STABILITY_EXCELLENT:
            return "excellent"
        if score >= STABILITY_GOOD:
            return "good"
        if score >= STABILITY_WARNING:
            return "warning"
        return "poor"

    @staticmethod
    def _stability_trend(previous: float, current: float) -> str:
        delta = current - previous
        if delta >= TREND_THRESHOLD:
            return "improving"
        if delta <= -TREND_THRESHOLD:
            return "declining"
        return "stable"

    def record_stability_event(self, success: bool) -> None:
        """Record an outcome and refresh rolling stability measurements."""
        previous = self.stability_score
        self._stability_events.append(bool(success))
        self.stability_score = round(
            (sum(self._stability_events) / len(self._stability_events)) * 100,
            1,
        )
        self.stability_status = self._stability_status(self.stability_score)
        self.stability_trend = self._stability_trend(
            previous,
            self.stability_score,
        )

    def record_command_duration(self, duration_ms: Any) -> None:
        """Record a valid successful-command duration in milliseconds."""
        try:
            duration = int(round(float(duration_ms)))
        except (TypeError, ValueError):
            return
        if duration < 0:
            return
        self.command_duration_total_ms += duration
        self.successful_timed_commands += 1
        self.fastest_command_time_ms = (
            duration
            if self.fastest_command_time_ms == 0
            else min(self.fastest_command_time_ms, duration)
        )
        self.slowest_command_time_ms = max(
            self.slowest_command_time_ms,
            duration,
        )

    def record_poll_duration(self, duration_ms: float) -> None:
        """Record a poll duration and update poll timing statistics."""
        duration = max(0, int(round(duration_ms)))
        self.last_poll_time_ms = duration
        self.poll_duration_total_ms += duration
        self.timed_polls += 1
        self.average_poll_time_ms = round(
            self.poll_duration_total_ms / self.timed_polls
        )
        self.fastest_poll_time_ms = (
            duration
            if self.fastest_poll_time_ms == 0
            else min(self.fastest_poll_time_ms, duration)
        )
        self.slowest_poll_time_ms = max(
            self.slowest_poll_time_ms,
            duration,
        )

    def update_narrative(self) -> None:
        self.uptime_text = format_duration(self.uptime_seconds)
        self.last_recovery_age = relative_timestamp(self.last_recovery)

        transport_ok = self.bridge_status == "ready"
        mqtt_ok = self.mqtt_status == "connected"
        transport_label = (
            "Relay"
            if self.transport_type in {"relay", "tablet_relay"}
            else "Transport"
        )
        if self.health_status == "excellent" and mqtt_ok and transport_ok:
            self.bridge_summary = (
                f"Healthy • MQTT ✓ • {transport_label} ✓ • "
                f"{self.last_poll_time_ms} ms"
            )
        elif self.health_status in {"critical", "warning"}:
            self.bridge_summary = (
                f"{self.health_status.title()} • {self.health_reason}"
            )
        else:
            self.bridge_summary = (
                f"{self.health_status.title()} • MQTT {self.mqtt_status} "
                f"• {transport_label} {self.bridge_status}"
            )

        if self.health_status in {"critical", "warning"}:
            self.health_advisor = self.health_reason
        elif self.stability_trend == "declining":
            subject = (
                "tablet relay"
                if transport_label == "Relay"
                else "active transport"
            )
            self.health_advisor = (
                f"Stability is declining. Monitor the {subject} and "
                "Wi-Fi connection."
            )
        elif self.recovery_count > 0 and self.stability_score < STABILITY_EXCELLENT:
            self.health_advisor = (
                f"Recovered automatically. Stability is {self.stability_trend}."
            )
        elif self.average_poll_time_ms >= SLOW_POLL_WARNING_MS:
            subject = "relay" if transport_label == "Relay" else "transport"
            self.health_advisor = (
                "Communication is available, but "
                f"{subject} response time is elevated."
            )
        elif self.recovery_count > 0:
            self.health_advisor = (
                "Operating normally. Last recovery: "
                f"{self.last_recovery_age.lower()}."
            )
        else:
            self.health_advisor = (
                f"Operating normally. Stability is {self.stability_trend}."
            )

    def record_event(self, level: str, message: str) -> None:
        """Store the latest normalized diagnostic event."""
        level = str(level).upper().strip() or "INFO"
        message = str(message).strip() or "No event details"
        self.event_level = level
        self.event_message = message
        self.last_event = f"{level} • {message}"

    def publish_metrics(self) -> None:
        """Publish the current diagnostics snapshot to MQTT."""
        self.update_narrative()
        metrics = {
            "bridge_version": self.app_version,
            "bridge_uptime": self.uptime_seconds,
            "bridge_uptime_text": self.uptime_text,
            "bridge_status": self.bridge_status,
            "mqtt_status": self.mqtt_status,
            "transport_type": self.transport_type,
            "health_score": self.health_score,
            "health_status": self.health_status,
            "health_reason": self.health_reason,
            "bridge_summary": self.bridge_summary,
            "health_advisor": self.health_advisor,
            "stability_score": self.stability_score,
            "stability_status": self.stability_status,
            "stability_trend": self.stability_trend,
            "poll_count": self.poll_count,
            "poll_errors": self.poll_error_count,
            "poll_success_rate": self.poll_success_rate,
            "last_poll_time": self.last_poll_time_ms,
            "average_poll_time": self.average_poll_time_ms,
            "fastest_poll_time": self.fastest_poll_time_ms,
            "slowest_poll_time": self.slowest_poll_time_ms,
            "command_count": self.command_count,
            "command_failures": self.command_failure_count,
            "command_deferred": self.command_deferred_count,
            "command_not_applicable": self.command_not_applicable_count,
            "command_success_rate": self.command_success_rate,
            "average_command_time": self.average_command_time_ms,
            "fastest_command_time": self.fastest_command_time_ms,
            "slowest_command_time": self.slowest_command_time_ms,
            "mqtt_reconnects": self.mqtt_reconnect_count,
            "recovery_count": self.recovery_count,
            "recovery_failures": self.recovery_failure_count,
            "recovery_success_rate": self.recovery_success_rate,
            "last_recovery": self.last_recovery,
            "last_recovery_age": self.last_recovery_age,
            "recovery_reason": self.recovery_reason,
            "last_recovery_duration": self.last_recovery_duration_ms,
            "average_recovery_time": self.average_recovery_time_ms,
            "longest_recovery_time": self.longest_recovery_time_ms,
            "last_event": self.last_event,
            "event_level": self.event_level,
            "event_message": self.event_message,
            "protocol_name": self.protocol_name,
            "discovery_status": self.discovery_status,
            "last_error": self.last_error,
        }
        for key, value in metrics.items():
            self.publish(key, value)

    def publish_command(
        self,
        *,
        command_json: str,
        result: str,
        transaction: dict[str, Any] | None = None,
    ) -> None:
        """Publish command diagnostics and record successful timing data."""
        self.publish("last_command", command_json)
        self.publish("last_command_result", result)
        level = (
            "INFO"
            if result in {"running", "success", "deferred", "not_applicable"}
            else "ERROR"
        )
        self.record_event(level, f"Command {result}: {command_json}")
        if transaction:
            self.publish(
                "last_transaction_id",
                transaction.get("transaction_id", ""),
            )
            duration = transaction.get("duration_ms", "")
            self.publish("last_command_duration", duration)
            if result == "success":
                self.record_command_duration(duration)
        elif result in {"deferred", "not_applicable"}:
            self.publish("last_transaction_id", "0")
            self.publish("last_command_duration", "0")
