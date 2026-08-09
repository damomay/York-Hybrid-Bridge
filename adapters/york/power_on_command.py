"""Parameterised York power-on commands backed by qualified target shapes."""
from __future__ import annotations

from adapters.york.captured_temperature_command import (
    QUALIFIED_TEMPERATURES,
    build_captured_heat_high_vertical_temperature_command,
)
from adapters.york.errors import YorkProtocolError
from adapters.york.low_vertical_temperature_command import (
    QUALIFIED_LOW_VERTICAL_TEMPERATURES,
    build_captured_heat_low_vertical_temperature_command,
)
from adapters.york.temperature_command import (
    MAX_TEMPERATURE,
    MIN_TEMPERATURE,
    build_qualified_temperature_command,
)


def build_parameterised_power_on_command(
    mode: str,
    temperature: float,
    fan: str,
    swing: str,
) -> bytes:
    """Build only complete power-on target states already qualified natively."""

    mode_name = str(mode).strip().lower()
    fan_name = str(fan).strip().lower()
    swing_name = str(swing).strip().lower()

    if fan_name == "low" and swing_name == "off":
        return build_qualified_temperature_command(mode_name, temperature)
    if mode_name == "heat" and fan_name == "low" and swing_name == "vertical":
        return build_captured_heat_low_vertical_temperature_command(temperature)
    if mode_name == "heat" and fan_name == "high" and swing_name == "vertical":
        return build_captured_heat_high_vertical_temperature_command(temperature)
    raise YorkProtocolError(
        "Parameterised power-on supports only Heat/Cool Low/Off, "
        "Heat Low/Vertical, or Heat High/Vertical"
    )


def validate_parameterised_power_on_command(
    frame: bytes,
    mode: str,
    temperature: float,
    fan: str,
    swing: str,
) -> None:
    """Require the exact canonical frame for the requested target state."""

    expected = build_parameterised_power_on_command(
        mode,
        temperature,
        fan,
        swing,
    )
    if frame != expected:
        raise YorkProtocolError(
            "Safety interlock rejected a non-canonical parameterised "
            "power-on command"
        )


_LOW_OFF_TEMPERATURES = tuple(
    value / 2
    for value in range(int(MIN_TEMPERATURE * 2), int(MAX_TEMPERATURE * 2) + 1)
)

QUALIFIED_PARAMETERISED_POWER_ON_COMMANDS = frozenset(
    {
        *(
            build_parameterised_power_on_command(mode, temperature, "low", "off")
            for mode in ("heat", "cool")
            for temperature in _LOW_OFF_TEMPERATURES
        ),
        *(
            build_parameterised_power_on_command(
                "heat", temperature, "low", "vertical"
            )
            for temperature in QUALIFIED_LOW_VERTICAL_TEMPERATURES
        ),
        *(
            build_parameterised_power_on_command(
                "heat", temperature, "high", "vertical"
            )
            for temperature in QUALIFIED_TEMPERATURES
        ),
    }
)
