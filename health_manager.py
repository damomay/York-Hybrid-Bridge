from __future__ import annotations

from dataclasses import dataclass


MQTT_DISCONNECTED_SCORE = 20
RELAY_UNAVAILABLE_SCORE = 25

POLL_FAILURE_PENALTY = 15
MAX_POLL_FAILURE_PENALTY = 45

RECOVERING_PENALTY = 15
ERROR_PENALTY = 35

SLOW_COMMAND_WARNING_MS = 4_000
SLOW_COMMAND_CRITICAL_MS = 6_000
SLOW_COMMAND_WARNING_PENALTY = 5
SLOW_COMMAND_CRITICAL_PENALTY = 15

EXCELLENT_SCORE = 90
GOOD_SCORE = 75
WARNING_SCORE = 50


@dataclass(frozen=True)
class HealthSnapshot:
    """Current operational health assessment."""

    score: int
    status: str
    reason: str


class HealthManager:
    """Evaluate current operational health independently of reliability history."""

    def evaluate(
        self,
        *,
        mqtt_connected: bool,
        consecutive_poll_failures: int,
        relay_offline_after_failures: int,
        average_command_time_ms: int,
        bridge_status: str,
    ) -> HealthSnapshot:
        """Return a health snapshot for the bridge's current operating state."""
        score = 100
        reasons: list[str] = []

        if not mqtt_connected:
            return HealthSnapshot(
                MQTT_DISCONNECTED_SCORE,
                "critical",
                "MQTT is disconnected",
            )

        if consecutive_poll_failures >= relay_offline_after_failures:
            return HealthSnapshot(
                RELAY_UNAVAILABLE_SCORE,
                "critical",
                "Tablet relay is unavailable",
            )

        if consecutive_poll_failures > 0:
            penalty = min(
                MAX_POLL_FAILURE_PENALTY,
                consecutive_poll_failures * POLL_FAILURE_PENALTY,
            )
            score -= penalty

            failure_label = (
                "failure"
                if consecutive_poll_failures == 1
                else "failures"
            )
            reasons.append(
                "Tablet relay poll is retrying "
                f"({consecutive_poll_failures} consecutive {failure_label})"
            )

        if bridge_status == "recovering" and not reasons:
            score -= RECOVERING_PENALTY
            reasons.append("Bridge recovery is in progress")
        elif bridge_status == "error" and not reasons:
            score -= ERROR_PENALTY
            reasons.append("Bridge reported an active error")

        if average_command_time_ms >= SLOW_COMMAND_CRITICAL_MS:
            score -= SLOW_COMMAND_CRITICAL_PENALTY
            reasons.append("Command response is currently slow")
        elif average_command_time_ms >= SLOW_COMMAND_WARNING_MS:
            score -= SLOW_COMMAND_WARNING_PENALTY
            reasons.append("Command response is slower than normal")

        score = max(0, min(100, score))

        if score >= EXCELLENT_SCORE:
            status = "excellent"
        elif score >= GOOD_SCORE:
            status = "good"
        elif score >= WARNING_SCORE:
            status = "warning"
        else:
            status = "critical"

        reason = (
            "; ".join(reasons)
            if reasons
            else "All monitored systems are operating normally"
        )

        return HealthSnapshot(
            score=score,
            status=status,
            reason=reason,
        )