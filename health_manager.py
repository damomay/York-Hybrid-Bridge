from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class HealthSnapshot:
    score: int
    status: str
    reason: str


class HealthManager:
    """Evaluate current operational health separately from historical reliability."""

    def evaluate(
        self,
        *,
        mqtt_connected: bool,
        consecutive_poll_failures: int,
        relay_offline_after_failures: int,
        average_command_time_ms: int,
        bridge_status: str,
        state_source_label: str = "Active transport",
    ) -> HealthSnapshot:
        score = 100
        reasons: list[str] = []

        if not mqtt_connected:
            return HealthSnapshot(20, "critical", "MQTT is disconnected")

        if consecutive_poll_failures >= relay_offline_after_failures:
            return HealthSnapshot(25, "critical", f"{state_source_label} is unavailable")

        if consecutive_poll_failures > 0:
            score -= min(45, consecutive_poll_failures * 15)
            reasons.append(
                f"{state_source_label} poll is retrying ({consecutive_poll_failures} consecutive failure"
                + ("s" if consecutive_poll_failures != 1 else "")
                + ")"
            )

        if bridge_status == "recovering" and not reasons:
            score -= 15
            reasons.append("Bridge recovery is in progress")
        elif bridge_status == "error" and not reasons:
            score -= 35
            reasons.append("Bridge reported an active error")

        if average_command_time_ms >= 6000:
            score -= 15
            reasons.append("Command response is currently slow")
        elif average_command_time_ms >= 4000:
            score -= 5
            reasons.append("Command response is slower than normal")

        score = max(0, min(100, score))
        if score >= 90:
            status = "excellent"
        elif score >= 75:
            status = "good"
        elif score >= 50:
            status = "warning"
        else:
            status = "critical"

        reason = "; ".join(reasons) if reasons else "All monitored systems are operating normally"
        return HealthSnapshot(score=score, status=status, reason=reason)
