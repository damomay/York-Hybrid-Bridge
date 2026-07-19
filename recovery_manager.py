from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import re
import time


def friendly_reason(reason: str) -> str:
    text = str(reason or "").strip()
    lower = text.lower()
    if not text or lower == "none": return "none"
    if "mqtt disconnected" in lower: return "MQTT connection was interrupted"
    if "500 server error" in lower or "http 500" in lower: return "Tablet relay returned HTTP 500 while polling AC state"
    if "connection refused" in lower: return "Tablet relay connection was refused"
    if "connect timeout" in lower or "timed out" in lower: return "Tablet relay did not respond before the timeout"
    if lower.startswith("poll:"):
        detail = re.sub(r"https?://\S+", "tablet relay", text.split(":", 2)[-1].strip())
        return f"Temporary tablet relay polling failure: {detail}"
    return text


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class RecoveryManager:
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
        return 0 if self.recovery_count == 0 else round(self.total_duration_ms / self.recovery_count)

    def begin(self, reason: str) -> None:
        if not self.active:
            self.started_monotonic = time.monotonic()
        self.active = True
        self.state = "recovering"
        self.last_reason = friendly_reason(reason)

    def complete(self) -> bool:
        if not self.active:
            self.state = "ready"
            return False
        duration = 0 if self.started_monotonic is None else int(round((time.monotonic() - self.started_monotonic) * 1000))
        self.active = False
        self.started_monotonic = None
        self.state = "ready"
        self.recovery_count += 1
        self.last_duration_ms = duration
        self.total_duration_ms += duration
        self.longest_duration_ms = max(self.longest_duration_ms, duration)
        self.last_recovery = utc_now()
        return True

    def fail(self, reason: str) -> None:
        self.active = True
        self.state = "error"
        self.failure_count += 1
        self.last_reason = friendly_reason(reason)
