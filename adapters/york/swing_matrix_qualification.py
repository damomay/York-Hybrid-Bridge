"""Alpha.65 case-specific Heat / 22.5 °C / Fan Low swing matrix."""
from __future__ import annotations

from adapters.york.errors import YorkProtocolError

QUALIFICATION_TEMPERATURE = 22.5
QUALIFIED_SWING_MATRIX_MODES = ("off", "vertical", "both", "horizontal")

YORK_QUALIFICATION_HEAT_LOW_OFF_22_5 = bytes.fromhex(
    "BB0001031901004401090202000000000000000000000000000000000000ED"
)
YORK_QUALIFICATION_HEAT_LOW_VERTICAL_22_5 = bytes.fromhex(
    "BB0001031901004401093A02000000000000000000000000000000000000D5"
)
YORK_CANDIDATE_HEAT_LOW_BOTH_22_5 = bytes.fromhex(
    "BB0001031901004401093A0A000000000000000000000000000000000000DD"
)
YORK_CANDIDATE_HEAT_LOW_HORIZONTAL_22_5 = bytes.fromhex(
    "BB000103190100440109020A000000000000000000000000000000000000E5"
)

_COMMANDS = {
    "off": YORK_QUALIFICATION_HEAT_LOW_OFF_22_5,
    "vertical": YORK_QUALIFICATION_HEAT_LOW_VERTICAL_22_5,
    "both": YORK_CANDIDATE_HEAT_LOW_BOTH_22_5,
    "horizontal": YORK_CANDIDATE_HEAT_LOW_HORIZONTAL_22_5,
}


def build_heat_22_5_low_swing_matrix_command(target_swing: str) -> bytes:
    """Return only the exact case-specific Alpha.65 target frame."""

    swing = str(target_swing).strip().lower()
    try:
        return _COMMANDS[swing]
    except KeyError as error:
        raise YorkProtocolError(
            "Alpha.65 swing matrix supports only Off, Vertical, Both and Horizontal"
        ) from error


def validate_heat_22_5_low_swing_matrix_command(
    frame: bytes,
    target_swing: str,
) -> None:
    """Require byte identity with the case-specific Alpha.65 target."""

    if frame != build_heat_22_5_low_swing_matrix_command(target_swing):
        raise YorkProtocolError(
            "Safety interlock rejected a non-canonical Alpha.65 swing frame"
        )
