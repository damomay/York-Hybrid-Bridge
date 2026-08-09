"""Guarded York Heat/Low Swing Off and Vertical commands."""
from __future__ import annotations

from adapters.york.errors import YorkProtocolError
from adapters.york.low_vertical_temperature_command import (
    build_captured_heat_low_vertical_temperature_command,
    validate_captured_heat_low_vertical_temperature_command,
)
from adapters.york.temperature_command import (
    build_qualified_temperature_command,
    validate_qualified_temperature_command,
)

QUALIFIED_SWING_MODES = ("off", "vertical")


def build_qualified_heat_low_swing_command(
    target_swing: str,
    target_temperature: float,
) -> bytes:
    """Build the canonical target state for an Off/Vertical swing change."""

    swing = str(target_swing).strip().lower()
    if swing == "off":
        return build_qualified_temperature_command("heat", target_temperature)
    if swing == "vertical":
        return build_captured_heat_low_vertical_temperature_command(
            target_temperature
        )
    raise YorkProtocolError(
        "Guarded native swing control supports only Off and Vertical"
    )


def validate_qualified_heat_low_swing_command(
    frame: bytes,
    target_swing: str,
) -> float:
    """Require a canonical Off/Vertical target frame and return its setpoint."""

    swing = str(target_swing).strip().lower()
    if swing == "off":
        mode, temperature = validate_qualified_temperature_command(frame)
        if mode != "heat":
            raise YorkProtocolError(
                "Guarded native swing control requires Heat mode"
            )
        return temperature
    if swing == "vertical":
        return validate_captured_heat_low_vertical_temperature_command(frame)
    raise YorkProtocolError(
        "Guarded native swing control supports only Off and Vertical"
    )
