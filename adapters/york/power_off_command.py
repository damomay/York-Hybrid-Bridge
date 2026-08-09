"""Parameterised York power-off commands backed by qualified target shapes."""
from __future__ import annotations

from adapters.york.errors import YorkProtocolError
from adapters.york.power_on_command import (
    QUALIFIED_PARAMETERISED_POWER_ON_COMMANDS,
    build_parameterised_power_on_command,
)


def _york_xor(data: bytes | bytearray) -> int:
    value = 0
    for item in data:
        value ^= item
    return value


def _power_off_from_canonical_on(frame: bytes) -> bytes:
    """Clear only the qualified York power bit and refresh the frame XOR."""

    if len(frame) != 31 or frame[7] != 0x44:
        raise YorkProtocolError(
            "Parameterised power-off requires a canonical power-on frame"
        )
    command = bytearray(frame)
    command[7] = 0x40
    command[-1] = _york_xor(command[:-1])
    return bytes(command)


def build_parameterised_power_off_command(
    mode: str,
    temperature: float,
    fan: str,
    swing: str,
) -> bytes:
    """Build Off only for complete target states already qualified natively."""

    return _power_off_from_canonical_on(
        build_parameterised_power_on_command(mode, temperature, fan, swing)
    )


def validate_parameterised_power_off_command(
    frame: bytes,
    mode: str,
    temperature: float,
    fan: str,
    swing: str,
) -> None:
    """Require the exact canonical Off frame for the retained target state."""

    expected = build_parameterised_power_off_command(
        mode,
        temperature,
        fan,
        swing,
    )
    if frame != expected:
        raise YorkProtocolError(
            "Safety interlock rejected a non-canonical parameterised "
            "power-off command"
        )


QUALIFIED_PARAMETERISED_POWER_OFF_COMMANDS = frozenset(
    _power_off_from_canonical_on(frame)
    for frame in QUALIFIED_PARAMETERISED_POWER_ON_COMMANDS
)
