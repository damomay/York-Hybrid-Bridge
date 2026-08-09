"""Alpha.63 qualification frames for Heat / 22.5 °C / Swing Off fan control."""
from __future__ import annotations

from adapters.york.errors import YorkProtocolError

QUALIFICATION_TEMPERATURE = 22.5
QUALIFIED_FAN_OFF_MODES = ("low", "high")

YORK_QUALIFICATION_HEAT_LOW_OFF_22_5 = bytes.fromhex(
    "BB0001031901004401090202000000000000000000000000000000000000ED"
)
YORK_CANDIDATE_HEAT_HIGH_OFF_22_5 = bytes.fromhex(
    "BB0001031901004401090502000000000000000000000000000000000000EA"
)


def build_heat_22_5_fan_off_qualification_command(target_fan: str) -> bytes:
    """Return only the exact Alpha.63 Low/Off or candidate High/Off frame."""

    fan = str(target_fan).strip().lower()
    if fan == "low":
        return YORK_QUALIFICATION_HEAT_LOW_OFF_22_5
    if fan == "high":
        return YORK_CANDIDATE_HEAT_HIGH_OFF_22_5
    raise YorkProtocolError(
        "Alpha.63 Fan Off qualification supports only Low and High"
    )


def validate_heat_22_5_fan_off_qualification_command(
    frame: bytes,
    target_fan: str,
) -> None:
    """Require byte identity with the case-specific Alpha.63 frame."""

    expected = build_heat_22_5_fan_off_qualification_command(target_fan)
    if frame != expected:
        raise YorkProtocolError(
            "Safety interlock rejected a non-canonical Alpha.63 Fan Off frame"
        )
