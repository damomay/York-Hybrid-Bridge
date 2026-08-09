"""Boundary-qualified York Heat/High/Vertical temperature command generation."""
from __future__ import annotations

from adapters.york.errors import YorkProtocolError

MIN_QUALIFIED_TEMPERATURE = 16
MAX_QUALIFIED_TEMPERATURE = 31
CAPTURED_TEMPERATURES = tuple(
    range(MIN_QUALIFIED_TEMPERATURE, MAX_QUALIFIED_TEMPERATURE + 1)
)
QUALIFIED_TEMPERATURES = tuple(
    value / 2
    for value in range(
        MIN_QUALIFIED_TEMPERATURE * 2,
        MAX_QUALIFIED_TEMPERATURE * 2 + 1,
    )
)


def build_captured_heat_high_vertical_temperature_command(
    target_temperature: float,
) -> bytes:
    """Build a 0.5 °C command inside the qualified range.

    Sprint 3.1.10 established the encoding from 24, 25 and 26 °C. Sprint 3.1.11
    then captured both endpoints and their adjacent values: 16, 17, 30 and
    31 °C. Sprint 3.1.17 promotes the independently captured half-degree
    encoding: byte 9 is ``31 - whole temperature`` and byte 11 is ``0x02``
    for a half degree, for On / Heat / Fan High / Swing Vertical / Display On.
    """

    try:
        temperature = float(target_temperature)
    except (TypeError, ValueError) as error:
        raise YorkProtocolError("York target temperature must be numeric") from error
    half_steps = round(temperature * 2)
    normalised = half_steps / 2
    if abs(temperature - normalised) > 1e-9:
        raise YorkProtocolError(
            "Captured Heat/High/Vertical qualification supports 0.5 °C "
            "increments only"
        )
    if not MIN_QUALIFIED_TEMPERATURE <= normalised <= MAX_QUALIFIED_TEMPERATURE:
        raise YorkProtocolError(
            "Boundary-qualified Heat/High/Vertical temperature must be "
            "between 16 and 31 °C"
        )
    whole = int(normalised)
    half_degree = normalised != whole

    frame = bytearray(31)
    frame[:9] = bytes.fromhex("BB0001031901004401")
    frame[9] = 31 - whole
    frame[10] = 0x3D
    frame[11] = 0x02 if half_degree else 0x00
    checksum = 0
    for value in frame[:-1]:
        checksum ^= value
    frame[-1] = checksum
    return bytes(frame)


def validate_captured_heat_high_vertical_temperature_command(
    frame: bytes,
) -> float:
    """Require a canonical frame inside the boundary-qualified range."""

    if len(frame) != 31:
        raise YorkProtocolError(
            "York captured temperature command must contain exactly 31 bytes"
        )
    if frame[11] not in {0x00, 0x02}:
        raise YorkProtocolError(
            "York captured temperature command has an invalid half-degree byte"
        )
    temperature = float(31 - frame[9]) + (0.5 if frame[11] == 0x02 else 0.0)
    expected = build_captured_heat_high_vertical_temperature_command(temperature)
    if frame != expected:
        raise YorkProtocolError(
            "Safety interlock rejected a non-canonical captured "
            "Heat/High/Vertical temperature command"
        )
    return temperature
