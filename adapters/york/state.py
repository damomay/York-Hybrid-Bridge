from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any


@dataclass(frozen=True)
class YorkState:
    """Normalized York state returned to Climate Bridge core."""

    power: bool | None = None
    mode: str | None = None
    temperature: float | None = None
    current_temperature: float | None = None
    fan: str | None = None
    swing: str | None = None
    turbo: bool | None = None
    eco: bool | None = None
    health: bool | None = None
    display: bool | None = None
    sleep: bool | None = None

    def to_dict(self) -> dict[str, Any]:
        return {key: value for key, value in asdict(self).items() if value is not None}
