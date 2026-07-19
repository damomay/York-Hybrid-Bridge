from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import re
import time


def friendly_reason(reason: str) -> str:
    """Convert a technical recovery reason into user-friendly text."""
    text = str(reason or "").strip()
    lower = text.lower()

    if not text or lower == "none":
        return "none"

    if "mqtt disconnected" in lower:
        return "MQTT connection was interrupted"

    if "500 server error" in lower or "http 500" in lower:
        return "Tablet relay returned HTTP 500 while polling AC state"

    if "connection refused" in lower:
        return "Tablet relay connection was refused"

    if "connect timeout" in lower or "timed out" in lower:
        return "Tablet relay did not respond before the timeout"

    if lower.startswith("poll:"):
        detail = text.split(":", 2)[-1].strip()
        detail = re.sub(r"https?://\S+", "tablet relay", detail)
        return f"Temporary tablet relay polling failure: {detail}"

    return text


def utc_now() -> str:
    """Return the current UTC timestamp in ISO 8601 format."""
    return datetime.now(timezone.utc).isoformat()


@dataclass
class RecoveryManager:
    """Track bridge recovery state, outcomes and timing metrics."""

    state: str = "starting"
    recovery_count: int = 0
    failure_count: int = 0
    last_recovery: str = "never"
    last_reason: str = "none"
    active: bool = False
    started_monotonic: float | None = None
    last_duration_ms: int = 0
    total_duration_ms: int = 0
    longest_duration_ms: int = 0

    @property
    def average_duration_ms(self) -> int:
        """Return the average duration of successful recoveries."""
        if self.recovery_count == 0:
            return 0

        return round(self.total_duration_ms / self.recovery_count)

    def begin(self, reason: str) -> None:
        """Begin or update an active recovery attempt."""
        if not self.active:
            self.started_monotonic = time.monotonic()

        self.active = True
        self.state = "recovering"
        self.last_reason = friendly_reason(reason)

    def complete(self) -> bool:
        """Complete the active recovery and record its timing metrics."""
        if not self.active:
            self.state = "ready"
            return False

        duration = self._active_duration_ms()

        self.active = False
        self.started_monotonic = None
        self.state = "ready"
        self.recovery_count += 1
        self.last_duration_ms = duration
        self.total_duration_ms += duration
        self.longest_duration_ms = max(
            self.longest_duration_ms,
            duration,
        )
        self.last_recovery = utc_now()

        return True

    def fail(self, reason: str) -> None:
        """Record a failed recovery attempt while retaining recovery context."""
        self.active = True
        self.state = "error"
        self.failure_count += 1
        self.last_reason = friendly_reason(reason)

    def _active_duration_ms(self) -> int:
        """Return the elapsed duration of the active recovery attempt."""
        if self.started_monotonic is None:
            return 0

        elapsed_seconds = time.monotonic() - self.started_monotonic
        return int(round(elapsed_seconds * 1000))