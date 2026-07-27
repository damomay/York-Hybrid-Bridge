from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class TransportBase(ABC):
    """Common interface used by Climate Bridge transport implementations."""

    name: str = "unknown"
    display_name: str = "Unknown"

    @abstractmethod
    def get_state(self) -> dict[str, Any]:
        """Return the current normalized HVAC state."""

    @abstractmethod
    def command(self, **changes: Any) -> dict[str, Any]:
        """Apply requested state changes and return the confirmed state."""

    def close(self) -> None:
        """Release transport resources when required."""
