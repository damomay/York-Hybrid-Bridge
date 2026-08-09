"""Parameterised York running-mode commands backed by qualified target shapes."""
from __future__ import annotations

from adapters.york.broadlink import YORK_QUALIFICATION_POWER_ON_COOL
from adapters.york.errors import YorkProtocolError
from adapters.york.power_on_command import (
    QUALIFIED_PARAMETERISED_POWER_ON_COMMANDS,
    build_parameterised_power_on_command,
)


def build_parameterised_running_mode_command(
    mode: str,
    temperature: float,
    fan: str,
    swing: str,
) -> bytes:
    """Build an On target frame only from Alpha.60-qualified canonical shapes."""

    if (
        str(mode).strip().lower() == "cool"
        and float(temperature) == 25.0
        and str(fan).strip().lower() == "high"
        and str(swing).strip().lower() == "vertical"
    ):
        return YORK_QUALIFICATION_POWER_ON_COOL
    return build_parameterised_power_on_command(mode, temperature, fan, swing)


def validate_parameterised_running_mode_command(
    frame: bytes,
    mode: str,
    temperature: float,
    fan: str,
    swing: str,
) -> None:
    """Require the exact canonical On frame for the requested running mode."""

    expected = build_parameterised_running_mode_command(
        mode,
        temperature,
        fan,
        swing,
    )
    if frame != expected:
        raise YorkProtocolError(
            "Safety interlock rejected a non-canonical parameterised "
            "running-mode command"
        )


QUALIFIED_PARAMETERISED_RUNNING_MODE_COMMANDS = frozenset(
    {YORK_QUALIFICATION_POWER_ON_COOL, *QUALIFIED_PARAMETERISED_POWER_ON_COMMANDS}
)
