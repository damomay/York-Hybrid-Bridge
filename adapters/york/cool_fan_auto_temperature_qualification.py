"""Guarded Cool temperature encoder across qualified fan states."""
from __future__ import annotations

import math
from typing import Any, Mapping

from adapters.york.errors import YorkProtocolError

COOL_23_TO_21_FAN_AUTO_COMMAND = bytes.fromhex(
    "BB00010319010044030A0000000000000000000000000000000000000000EC"
)

COOL_20_TO_20_5_FAN_AUTO_COMMAND = bytes.fromhex(
    "BB00010319010044030B0002000000000000000000000000000000000000EF"
)

COOL_20_5_TO_20_FAN_AUTO_COMMAND = bytes.fromhex(
    "BB00010319010044030B0000000000000000000000000000000000000000ED"
)

COOL_20_TO_22_FAN_AUTO_COMMAND = bytes.fromhex(
    "BB0001031901004403090000000000000000000000000000000000000000EF"
)

COOL_22_TO_20_FAN_AUTO_COMMAND = bytes.fromhex(
    "BB00010319010044030B0000000000000000000000000000000000000000ED"
)

COOL_20_TO_22_5_FAN_AUTO_COMMAND = bytes.fromhex(
    "BB0001031901004403090002000000000000000000000000000000000000ED"
)

COOL_22_5_TO_24_FAN_AUTO_COMMAND = bytes.fromhex(
    "BB0001031901004403070000000000000000000000000000000000000000E1"
)

COOL_24_TO_24_5_FAN_AUTO_COMMAND = bytes.fromhex(
    "BB0001031901004403070002000000000000000000000000000000000000E3"
)

COOL_24_5_TO_20_5_FAN_AUTO_COMMAND = COOL_20_TO_20_5_FAN_AUTO_COMMAND

COOL_20_5_TO_22_FAN_AUTO_COMMAND = COOL_20_TO_22_FAN_AUTO_COMMAND

COOL_23_FAN_AUTO_SOURCE: dict[str, Any] = {
    "power": True,
    "mode": "cool",
    "temperature": 23.0,
    "fan": "auto",
    "swing": "off",
    "turbo": False,
    "eco": False,
    "health": False,
    "display": True,
}

COOL_21_FAN_AUTO_TARGET: dict[str, Any] = {
    **COOL_23_FAN_AUTO_SOURCE,
    "temperature": 21.0,
}

COOL_20_FAN_AUTO_SOURCE: dict[str, Any] = {
    **COOL_23_FAN_AUTO_SOURCE,
    "temperature": 20.0,
}

COOL_20_5_FAN_AUTO_TARGET: dict[str, Any] = {
    **COOL_20_FAN_AUTO_SOURCE,
    "temperature": 20.5,
}

COOL_20_5_FAN_AUTO_SOURCE: dict[str, Any] = dict(COOL_20_5_FAN_AUTO_TARGET)

COOL_20_FAN_AUTO_TARGET: dict[str, Any] = dict(COOL_20_FAN_AUTO_SOURCE)

COOL_22_FAN_AUTO_TARGET: dict[str, Any] = {
    **COOL_20_FAN_AUTO_SOURCE,
    "temperature": 22.0,
}

COOL_22_FAN_AUTO_SOURCE: dict[str, Any] = dict(COOL_22_FAN_AUTO_TARGET)

COOL_22_5_FAN_AUTO_SOURCE: dict[str, Any] = {
    **COOL_20_FAN_AUTO_SOURCE,
    "temperature": 22.5,
}

COOL_24_FAN_AUTO_SOURCE: dict[str, Any] = {
    **COOL_20_FAN_AUTO_SOURCE,
    "temperature": 24.0,
}

COOL_24_5_FAN_AUTO_SOURCE: dict[str, Any] = {
    **COOL_20_FAN_AUTO_SOURCE,
    "temperature": 24.5,
}

GENERAL_COOL_FAN_AUTO_MIN_TEMPERATURE = 16.0
GENERAL_COOL_FAN_AUTO_MAX_TEMPERATURE = 31.0
GENERAL_COOL_FAN_AUTO_STEP = 0.5

GENERAL_COOL_QUALIFIED_FAN_VALUES = {
    "auto": 0x00,
    "low": 0x02,
    "high": 0x05,
}


def _normalise_half_degree_temperature(value: Any, *, label: str) -> float:
    if isinstance(value, bool):
        raise YorkProtocolError(f"{label} requires a numeric temperature")
    try:
        temperature = float(value)
    except (TypeError, ValueError) as exc:
        raise YorkProtocolError(f"{label} requires a numeric temperature") from exc
    if not math.isfinite(temperature):
        raise YorkProtocolError(f"{label} requires a finite temperature")
    if not (
        GENERAL_COOL_FAN_AUTO_MIN_TEMPERATURE
        <= temperature
        <= GENERAL_COOL_FAN_AUTO_MAX_TEMPERATURE
    ):
        raise YorkProtocolError(
            f"{label} requires {GENERAL_COOL_FAN_AUTO_MIN_TEMPERATURE:g} to "
            f"{GENERAL_COOL_FAN_AUTO_MAX_TEMPERATURE:g} C"
        )
    doubled = temperature * 2.0
    if not doubled.is_integer():
        raise YorkProtocolError(f"{label} requires 0.5 C increments")
    return temperature


def encode_general_cool_qualified_fan_temperature(
    target_temperature: Any,
    fan: Any,
) -> bytes:
    """Encode one canonical Cool/Swing Off target preserving a qualified fan."""

    temperature = _normalise_half_degree_temperature(
        target_temperature,
        label="General Cool qualified-fan encoder",
    )
    fan_name = str(fan).strip().lower()
    try:
        fan_byte = GENERAL_COOL_QUALIFIED_FAN_VALUES[fan_name]
    except KeyError as exc:
        raise YorkProtocolError(
            "General Cool qualified-fan encoder requires Auto, Low, or High"
        ) from exc
    whole = int(temperature)
    frame = bytearray(31)
    frame[0:7] = bytes.fromhex("BB000103190100")
    frame[7] = 0x44  # Power On + Display On; Eco Off.
    frame[8] = 0x03  # Cool; Turbo/Health Off.
    frame[9] = 31 - whole
    frame[10] = fan_byte
    frame[11] = 0x02 if temperature != whole else 0x00
    checksum = 0
    for byte in frame[:-1]:
        checksum ^= byte
    frame[-1] = checksum
    return bytes(frame)


def encode_general_cool_fan_auto_temperature(target_temperature: Any) -> bytes:
    """Compatibility wrapper for Alpha.91's Fan Auto encoder."""

    return encode_general_cool_qualified_fan_temperature(
        target_temperature,
        "auto",
    )


GENERAL_COOL_QUALIFIED_FAN_TEMPERATURE_COMMANDS = frozenset(
    encode_general_cool_qualified_fan_temperature(step / 2.0, fan)
    for fan in GENERAL_COOL_QUALIFIED_FAN_VALUES
    for step in range(
        int(GENERAL_COOL_FAN_AUTO_MIN_TEMPERATURE * 2),
        int(GENERAL_COOL_FAN_AUTO_MAX_TEMPERATURE * 2) + 1,
    )
)


GENERAL_COOL_FAN_AUTO_TEMPERATURE_COMMANDS = frozenset(
    encode_general_cool_fan_auto_temperature(step / 2.0)
    for step in range(
        int(GENERAL_COOL_FAN_AUTO_MIN_TEMPERATURE * 2),
        int(GENERAL_COOL_FAN_AUTO_MAX_TEMPERATURE * 2) + 1,
    )
)

LEGACY_QUALIFIED_COOL_FAN_AUTO_TEMPERATURE_COMMANDS = frozenset(
    {
        COOL_23_TO_21_FAN_AUTO_COMMAND,
        COOL_20_TO_20_5_FAN_AUTO_COMMAND,
        COOL_20_5_TO_20_FAN_AUTO_COMMAND,
        COOL_20_TO_22_FAN_AUTO_COMMAND,
        COOL_22_TO_20_FAN_AUTO_COMMAND,
        COOL_20_TO_22_5_FAN_AUTO_COMMAND,
        COOL_22_5_TO_24_FAN_AUTO_COMMAND,
        COOL_24_TO_24_5_FAN_AUTO_COMMAND,
    }
)

# Compatibility name retained for earlier qualification imports. Alpha.91
# derives this target-frame boundary from the encoder rather than source edges.
QUALIFIED_COOL_FAN_AUTO_TEMPERATURE_COMMANDS = (
    GENERAL_COOL_FAN_AUTO_TEMPERATURE_COMMANDS
)

GROUPED_COOL_FAN_AUTO_TEMPERATURE_MATRIX = {
    (20.0, 22.5): COOL_20_TO_22_5_FAN_AUTO_COMMAND,
    (22.5, 24.0): COOL_22_5_TO_24_FAN_AUTO_COMMAND,
    (24.0, 24.5): COOL_24_TO_24_5_FAN_AUTO_COMMAND,
    (24.5, 20.5): COOL_24_5_TO_20_5_FAN_AUTO_COMMAND,
    (20.5, 22.0): COOL_20_5_TO_22_FAN_AUTO_COMMAND,
    (22.0, 20.0): COOL_22_TO_20_FAN_AUTO_COMMAND,
}


def build_grouped_cool_fan_auto_temperature_command(
    source: Mapping[str, Any],
    target_temperature: float,
) -> bytes:
    """Return one immutable Alpha.90 matrix command for an exact source edge."""

    if isinstance(target_temperature, bool):
        raise YorkProtocolError(
            "Grouped Cool Fan Auto matrix requires a numeric target"
        )
    source_temperature = source.get("temperature")
    if isinstance(source_temperature, bool) or source_temperature is None:
        raise YorkProtocolError(
            "Grouped Cool Fan Auto matrix requires a numeric source temperature"
        )
    source_temperature = float(source_temperature)
    expected_source = {
        **COOL_20_FAN_AUTO_SOURCE,
        "temperature": source_temperature,
    }
    mismatches = [
        field
        for field, expected in expected_source.items()
        if source.get(field) != expected
    ]
    if mismatches:
        raise YorkProtocolError(
            "Grouped Cool Fan Auto matrix source mismatch: "
            + ", ".join(mismatches)
        )
    edge = (source_temperature, float(target_temperature))
    try:
        return GROUPED_COOL_FAN_AUTO_TEMPERATURE_MATRIX[edge]
    except KeyError as exc:
        raise YorkProtocolError(
            "Grouped Cool Fan Auto matrix rejected uncaptured edge "
            f"{edge[0]:g} to {edge[1]:g} C"
        ) from exc


def build_general_cool_fan_auto_temperature_command(
    source: Mapping[str, Any],
    target_temperature: Any,
) -> bytes:
    """Build any canonical 16–31 C half-degree target from an exact source."""

    source_temperature = _normalise_half_degree_temperature(
        source.get("temperature"),
        label="General Cool Fan Auto source",
    )
    expected_source = {
        **COOL_20_FAN_AUTO_SOURCE,
        "temperature": source_temperature,
    }
    mismatches = [
        field
        for field, expected in expected_source.items()
        if source.get(field) != expected
    ]
    if mismatches:
        raise YorkProtocolError(
            "General Cool Fan Auto source mismatch: " + ", ".join(mismatches)
        )
    target = _normalise_half_degree_temperature(
        target_temperature,
        label="General Cool Fan Auto target",
    )
    if target == source_temperature:
        raise YorkProtocolError(
            "General Cool Fan Auto encoder rejected an unchanged target"
        )
    return encode_general_cool_fan_auto_temperature(target)


def build_general_cool_qualified_fan_temperature_command(
    source: Mapping[str, Any],
    target_temperature: Any,
) -> bytes:
    """Build any canonical Cool target while preserving Auto, Low, or High."""

    source_temperature = _normalise_half_degree_temperature(
        source.get("temperature"),
        label="General Cool qualified-fan source",
    )
    fan = str(source.get("fan", "")).strip().lower()
    if fan not in GENERAL_COOL_QUALIFIED_FAN_VALUES:
        raise YorkProtocolError(
            "General Cool qualified-fan source requires Auto, Low, or High"
        )
    expected_source = {
        **COOL_20_FAN_AUTO_SOURCE,
        "temperature": source_temperature,
        "fan": fan,
    }
    mismatches = [
        field
        for field, expected in expected_source.items()
        if source.get(field) != expected
    ]
    if mismatches:
        raise YorkProtocolError(
            "General Cool qualified-fan source mismatch: "
            + ", ".join(mismatches)
        )
    target = _normalise_half_degree_temperature(
        target_temperature,
        label="General Cool qualified-fan target",
    )
    if target == source_temperature:
        raise YorkProtocolError(
            "General Cool qualified-fan encoder rejected an unchanged target"
        )
    return encode_general_cool_qualified_fan_temperature(target, fan)


def validate_general_cool_qualified_fan_temperature_command(
    frame: bytes,
) -> None:
    """Reject frames outside the 31 temperatures by three-fan canonical set."""

    if frame not in GENERAL_COOL_QUALIFIED_FAN_TEMPERATURE_COMMANDS:
        raise YorkProtocolError(
            "Safety interlock rejected a non-canonical general Cool "
            "qualified-fan command"
        )


def validate_general_cool_fan_auto_temperature_command(frame: bytes) -> None:
    """Reject any frame outside the formula-derived canonical target set."""

    if frame not in GENERAL_COOL_FAN_AUTO_TEMPERATURE_COMMANDS:
        raise YorkProtocolError(
            "Safety interlock rejected a non-canonical general Cool Fan Auto command"
        )


def validate_grouped_cool_fan_auto_temperature_command(frame: bytes) -> None:
    """Reject any frame outside Alpha.90's immutable grouped matrix."""

    if frame not in frozenset(GROUPED_COOL_FAN_AUTO_TEMPERATURE_MATRIX.values()):
        raise YorkProtocolError(
            "Safety interlock rejected a non-canonical grouped Cool Fan Auto command"
        )


def build_cool_23_to_21_fan_auto_command(
    source: Mapping[str, Any],
    target_temperature: float,
) -> bytes:
    """Return Capture 8's immutable command only for its exact source edge."""

    mismatches = [
        field
        for field, expected in COOL_23_FAN_AUTO_SOURCE.items()
        if source.get(field) != expected
    ]
    if mismatches:
        raise YorkProtocolError(
            "Cool Fan Auto qualification source mismatch: "
            + ", ".join(mismatches)
        )
    if isinstance(target_temperature, bool) or float(target_temperature) != 21.0:
        raise YorkProtocolError(
            "Cool Fan Auto qualification permits only the captured 23 to 21 C edge"
        )
    return COOL_23_TO_21_FAN_AUTO_COMMAND


def validate_cool_23_to_21_fan_auto_command(frame: bytes) -> None:
    """Reject frames outside the two immutable Cool/Fan Auto captures."""

    if frame not in LEGACY_QUALIFIED_COOL_FAN_AUTO_TEMPERATURE_COMMANDS:
        raise YorkProtocolError(
            "Safety interlock rejected a non-canonical Cool Fan Auto command"
        )


def build_cool_20_to_20_5_fan_auto_command(
    source: Mapping[str, Any],
    target_temperature: float,
) -> bytes:
    """Return Capture 10's immutable command only for its exact source edge."""

    mismatches = [
        field
        for field, expected in COOL_20_FAN_AUTO_SOURCE.items()
        if source.get(field) != expected
    ]
    if mismatches:
        raise YorkProtocolError(
            "Cool 20 Fan Auto qualification source mismatch: "
            + ", ".join(mismatches)
        )
    if (
        isinstance(target_temperature, bool)
        or float(target_temperature) != 20.5
    ):
        raise YorkProtocolError(
            "Cool 20 Fan Auto qualification permits only the captured "
            "20 to 20.5 C edge"
        )
    return COOL_20_TO_20_5_FAN_AUTO_COMMAND


def validate_cool_20_to_20_5_fan_auto_command(frame: bytes) -> None:
    """Reject any mutation of Capture 10's exact official-parser frame."""

    if frame != COOL_20_TO_20_5_FAN_AUTO_COMMAND:
        raise YorkProtocolError(
            "Safety interlock rejected a non-canonical Cool 20 Fan Auto command"
        )


def build_cool_20_5_to_20_fan_auto_command(
    source: Mapping[str, Any],
    target_temperature: float,
) -> bytes:
    """Return Capture 11's immutable command only for its exact source edge."""

    mismatches = [
        field
        for field, expected in COOL_20_5_FAN_AUTO_SOURCE.items()
        if source.get(field) != expected
    ]
    if mismatches:
        raise YorkProtocolError(
            "Cool 20.5 Fan Auto qualification source mismatch: "
            + ", ".join(mismatches)
        )
    if isinstance(target_temperature, bool) or float(target_temperature) != 20.0:
        raise YorkProtocolError(
            "Cool 20.5 Fan Auto qualification permits only the captured "
            "20.5 to 20 C edge"
        )
    return COOL_20_5_TO_20_FAN_AUTO_COMMAND


def validate_cool_20_5_to_20_fan_auto_command(frame: bytes) -> None:
    """Reject any mutation of Capture 11's exact official-parser frame."""

    if frame != COOL_20_5_TO_20_FAN_AUTO_COMMAND:
        raise YorkProtocolError(
            "Safety interlock rejected a non-canonical Cool 20.5 Fan Auto command"
        )


def build_cool_20_to_22_fan_auto_command(
    source: Mapping[str, Any],
    target_temperature: float,
) -> bytes:
    """Return Capture 10's immutable 20 to 22 command for its exact edge."""

    mismatches = [
        field
        for field, expected in COOL_20_FAN_AUTO_SOURCE.items()
        if source.get(field) != expected
    ]
    if mismatches:
        raise YorkProtocolError(
            "Cool 20 to 22 Fan Auto qualification source mismatch: "
            + ", ".join(mismatches)
        )
    if isinstance(target_temperature, bool) or float(target_temperature) != 22.0:
        raise YorkProtocolError(
            "Cool 20 Fan Auto qualification permits only the captured "
            "20 to 22 C edge"
        )
    return COOL_20_TO_22_FAN_AUTO_COMMAND


def validate_cool_20_to_22_fan_auto_command(frame: bytes) -> None:
    """Reject any mutation of Capture 10's exact 20 to 22 parser frame."""

    if frame != COOL_20_TO_22_FAN_AUTO_COMMAND:
        raise YorkProtocolError(
            "Safety interlock rejected a non-canonical Cool 20 to 22 Fan Auto command"
        )


def build_cool_22_to_20_fan_auto_command(
    source: Mapping[str, Any],
    target_temperature: float,
) -> bytes:
    """Return Capture 12's immutable 22 to 20 command for its exact edge."""

    mismatches = [
        field
        for field, expected in COOL_22_FAN_AUTO_SOURCE.items()
        if source.get(field) != expected
    ]
    if mismatches:
        raise YorkProtocolError(
            "Cool 22 to 20 Fan Auto qualification source mismatch: "
            + ", ".join(mismatches)
        )
    if isinstance(target_temperature, bool) or float(target_temperature) != 20.0:
        raise YorkProtocolError(
            "Cool 22 Fan Auto qualification permits only the captured "
            "22 to 20 C edge"
        )
    return COOL_22_TO_20_FAN_AUTO_COMMAND


def validate_cool_22_to_20_fan_auto_command(frame: bytes) -> None:
    """Reject any mutation of Capture 12's exact 22 to 20 parser frame."""

    if frame != COOL_22_TO_20_FAN_AUTO_COMMAND:
        raise YorkProtocolError(
            "Safety interlock rejected a non-canonical Cool 22 to 20 Fan Auto command"
        )
