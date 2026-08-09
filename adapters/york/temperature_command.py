"""Evidence-backed York temperature-command generation for qualification."""
from __future__ import annotations

from adapters.york.errors import YorkProtocolError

MIN_TEMPERATURE = 16.0
MAX_TEMPERATURE = 30.0
_MODE_BYTES = {"heat": 0x01, "cool": 0x03}
_BYTE_MODES = {value: key for key, value in _MODE_BYTES.items()}


def _normalise_temperature(value: float) -> float:
    try:
        temperature = float(value)
    except (TypeError, ValueError) as error:
        raise YorkProtocolError("York target temperature must be numeric") from error
    half_steps = round(temperature * 2)
    normalised = half_steps / 2
    if abs(temperature - normalised) > 1e-9:
        raise YorkProtocolError(
            "York target temperature must use 0.5 °C increments"
        )
    if not MIN_TEMPERATURE <= normalised <= MAX_TEMPERATURE:
        raise YorkProtocolError(
            f"York target temperature must be between "
            f"{MIN_TEMPERATURE:g} and {MAX_TEMPERATURE:g} °C"
        )
    return normalised


def build_qualified_temperature_command(mode: str, target_temperature: float) -> bytes:
    """Build the captured 31-byte command shape for a temperature-only change.

    This generator is deliberately limited to the qualified On / Low fan /
    Swing Off / Display On command shape observed in Relay v2 transactions.
    Alpha.29 may use it through a separate guarded, disabled-by-default manager.
    """

    mode_name = str(mode).strip().lower()
    if mode_name not in _MODE_BYTES:
        raise YorkProtocolError(
            "Dynamic temperature qualification supports only heat and cool"
        )
    temperature = _normalise_temperature(target_temperature)
    whole = int(temperature)
    half_degree = temperature != whole

    frame = bytearray(31)
    frame[:8] = bytes.fromhex("BB00010319010044")
    frame[8] = _MODE_BYTES[mode_name]
    frame[9] = 31 - whole
    frame[10] = 0x02
    frame[11] = 0x02 if half_degree else 0x00
    checksum = 0
    for value in frame[:-1]:
        checksum ^= value
    frame[-1] = checksum
    return bytes(frame)


def validate_qualified_temperature_command(frame: bytes) -> tuple[str, float]:
    """Require a byte-canonical frame and return its mode and target."""

    if len(frame) != 31:
        raise YorkProtocolError(
            "York dynamic temperature command must contain exactly 31 bytes"
        )
    mode = _BYTE_MODES.get(frame[8])
    if mode is None:
        raise YorkProtocolError(
            "York dynamic temperature command has an unsupported mode byte"
        )
    if frame[11] not in {0x00, 0x02}:
        raise YorkProtocolError(
            "York dynamic temperature command has an invalid half-degree byte"
        )
    temperature = float(31 - frame[9]) + (0.5 if frame[11] == 0x02 else 0.0)
    expected = build_qualified_temperature_command(mode, temperature)
    if frame != expected:
        raise YorkProtocolError(
            "Safety interlock rejected a non-canonical York temperature command"
        )
    return mode, temperature
