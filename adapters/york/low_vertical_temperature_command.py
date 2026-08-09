"""Parameterised York Heat/Low/Vertical temperature commands."""
from __future__ import annotations

from adapters.york.errors import YorkProtocolError

MIN_LOW_VERTICAL_TEMPERATURE = 16
MAX_LOW_VERTICAL_TEMPERATURE = 31
CAPTURED_LOW_VERTICAL_TEMPERATURES = tuple(
    range(MIN_LOW_VERTICAL_TEMPERATURE, MAX_LOW_VERTICAL_TEMPERATURE + 1)
)
QUALIFIED_LOW_VERTICAL_TEMPERATURES = tuple(
    value / 2
    for value in range(
        MIN_LOW_VERTICAL_TEMPERATURE * 2,
        MAX_LOW_VERTICAL_TEMPERATURE * 2 + 1,
    )
)


def build_captured_heat_low_vertical_temperature_command(
    target_temperature: float,
) -> bytes:
    """Build a 0.5 °C Low/Vertical command in the qualified range.

    Alpha.42 proved the exact 24 and 25 °C frames and constant state byte
    ``0x3A``. Alpha.44 extended the already proven ``31 - temperature``
    encoding across the York whole-degree 16–31 °C range and physically
    qualified the comfortable 25 → 26 → 25 °C sequence. Alpha.45 enables this
    parameterised generator through normal guarded Home Assistant routing.
    Alpha.46 adds the independently captured byte-11 ``0x02`` half-degree flag
    without changing the qualified ``0x3A`` operating-state byte.
    """

    try:
        temperature = float(target_temperature)
    except (TypeError, ValueError) as error:
        raise YorkProtocolError("York target temperature must be numeric") from error
    half_steps = round(temperature * 2)
    normalised = half_steps / 2
    if abs(temperature - normalised) > 1e-9:
        raise YorkProtocolError(
            "Heat/Low/Vertical qualification supports 0.5 °C increments only"
        )
    if not MIN_LOW_VERTICAL_TEMPERATURE <= normalised <= MAX_LOW_VERTICAL_TEMPERATURE:
        raise YorkProtocolError(
            "Heat/Low/Vertical qualification temperature must be between "
            "16 and 31 °C"
        )
    whole = int(normalised)
    half_degree = normalised != whole

    frame = bytearray(31)
    frame[:9] = bytes.fromhex("BB0001031901004401")
    frame[9] = 31 - whole
    frame[10] = 0x3A
    frame[11] = 0x02 if half_degree else 0x00
    checksum = 0
    for value in frame[:-1]:
        checksum ^= value
    frame[-1] = checksum
    return bytes(frame)


def validate_captured_heat_low_vertical_temperature_command(
    frame: bytes,
) -> float:
    """Require a canonical Low/Vertical frame inside the qualified range."""

    if len(frame) != 31:
        raise YorkProtocolError(
            "York Low/Vertical temperature command must contain exactly 31 bytes"
        )
    if frame[11] not in {0x00, 0x02}:
        raise YorkProtocolError(
            "York Low/Vertical temperature command has an invalid half-degree byte"
        )
    temperature = float(31 - frame[9]) + (0.5 if frame[11] == 0x02 else 0.0)
    expected = build_captured_heat_low_vertical_temperature_command(temperature)
    if frame != expected:
        raise YorkProtocolError(
            "Safety interlock rejected a non-canonical parameterised "
            "Heat/Low/Vertical temperature command"
        )
    return temperature
