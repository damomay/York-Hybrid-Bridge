"""Alpha.64 qualification frames for Cool / 22.5 °C / Swing Off fan control."""
from __future__ import annotations

from adapters.york.errors import YorkProtocolError

QUALIFICATION_TEMPERATURE = 22.5
QUALIFIED_COOL_FAN_OFF_MODES = ("low", "high")

YORK_QUALIFICATION_COOL_LOW_OFF_22_5 = bytes.fromhex(
    "BB0001031901004403090202000000000000000000000000000000000000EF"
)
YORK_CANDIDATE_COOL_HIGH_OFF_22_5 = bytes.fromhex(
    "BB0001031901004403090502000000000000000000000000000000000000E8"
)


def build_cool_22_5_fan_off_qualification_command(target_fan: str) -> bytes:
    """Return only the exact Alpha.64 Cool Low/Off or High/Off frame."""

    fan = str(target_fan).strip().lower()
    if fan == "low":
        return YORK_QUALIFICATION_COOL_LOW_OFF_22_5
    if fan == "high":
        return YORK_CANDIDATE_COOL_HIGH_OFF_22_5
    raise YorkProtocolError(
        "Alpha.64 Cool Fan Off qualification supports only Low and High"
    )


def validate_cool_22_5_fan_off_qualification_command(
    frame: bytes,
    target_fan: str,
) -> None:
    """Require byte identity with the case-specific Alpha.64 Cool frame."""

    expected = build_cool_22_5_fan_off_qualification_command(target_fan)
    if frame != expected:
        raise YorkProtocolError(
            "Safety interlock rejected a non-canonical Alpha.64 Cool Fan Off frame"
        )
