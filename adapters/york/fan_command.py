"""Guarded York Heat/Vertical Low and High fan commands."""
from __future__ import annotations

from adapters.york.captured_temperature_command import (
    build_captured_heat_high_vertical_temperature_command,
    validate_captured_heat_high_vertical_temperature_command,
)
from adapters.york.errors import YorkProtocolError
from adapters.york.low_vertical_temperature_command import (
    build_captured_heat_low_vertical_temperature_command,
    validate_captured_heat_low_vertical_temperature_command,
)

QUALIFIED_FAN_MODES = ("low", "high")


def build_qualified_heat_vertical_fan_command(
    target_fan: str,
    target_temperature: float,
) -> bytes:
    """Build the canonical target state for a Low/High fan-only change."""

    fan = str(target_fan).strip().lower()
    if fan == "low":
        return build_captured_heat_low_vertical_temperature_command(
            target_temperature
        )
    if fan == "high":
        return build_captured_heat_high_vertical_temperature_command(
            target_temperature
        )
    raise YorkProtocolError(
        "Guarded native fan control supports only Low and High"
    )


def validate_qualified_heat_vertical_fan_command(
    frame: bytes,
    target_fan: str,
) -> float:
    """Require a canonical Low/High target frame and return its setpoint."""

    fan = str(target_fan).strip().lower()
    if fan == "low":
        return validate_captured_heat_low_vertical_temperature_command(frame)
    if fan == "high":
        return validate_captured_heat_high_vertical_temperature_command(frame)
    raise YorkProtocolError(
        "Guarded native fan control supports only Low and High"
    )
