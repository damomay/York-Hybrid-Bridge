"""Consolidated official-SDK mode-transition allowlist through Alpha.85.

Every entry is a physically qualified, byte-exact edge.  This module does not
infer frames, combine fields, or open additional source/target combinations.
"""
from __future__ import annotations

from dataclasses import dataclass
from types import MappingProxyType
from typing import Any, Mapping

from adapters.york.errors import YorkProtocolError


MODE_FIELDS = (
    "power",
    "mode",
    "temperature",
    "fan",
    "swing",
    "turbo",
    "eco",
    "health",
    "display",
)
NON_SETPOINT_MODE_FIELDS = tuple(
    field for field in MODE_FIELDS if field != "temperature"
)


@dataclass(frozen=True)
class OfficialSdkModeTransition:
    """One immutable, physically qualified mode edge."""

    key: str
    requested_mode: str
    frame: bytes
    source: Mapping[str, Any]
    target: Mapping[str, Any]
    source_fields: tuple[str, ...]
    target_fields: tuple[str, ...]
    dynamic_target_temperature: bool = False


def _state(**values: Any) -> Mapping[str, Any]:
    return MappingProxyType(values)


_COMMON = {
    "power": True,
    "fan": "auto",
    "swing": "off",
    "turbo": False,
    "eco": False,
    "health": False,
    "display": True,
}


# Generated offline by York Write Packet Lab v1 through the official
# TCL/Broadlink setSplitAirconInfo() parser, then physically qualified in
# Alpha.75 and Alpha.77-80. Capture 7 adds the exact Auto/FEEL 23 C to Cool
# 23 C edge needed by Alpha.82. Capture 9 adds only the exact Auto/FEEL 20 C
# to Cool 20 C edge needed by Alpha.85. No retired Alpha.67-72 candidate is
# retained here.
OFFICIAL_SDK_MODE_TRANSITIONS = (
    OfficialSdkModeTransition(
        key="mode-dry-to-fan-only",
        requested_mode="fan_only",
        frame=bytes.fromhex(
            "BB00010319010044070E0000000000000000000000000000000000000000EC"
        ),
        source=_state(**_COMMON, mode="dry"),
        target=_state(**_COMMON, mode="fan_only"),
        source_fields=NON_SETPOINT_MODE_FIELDS,
        target_fields=NON_SETPOINT_MODE_FIELDS,
    ),
    OfficialSdkModeTransition(
        key="mode-fan-only-to-heat-23",
        requested_mode="heat",
        frame=bytes.fromhex(
            "BB0001031901004401080000000000000000000000000000000000000000EC"
        ),
        source=_state(**_COMMON, mode="fan_only"),
        target=_state(**_COMMON, mode="heat", temperature=23.0),
        source_fields=NON_SETPOINT_MODE_FIELDS,
        target_fields=MODE_FIELDS,
    ),
    OfficialSdkModeTransition(
        key="mode-heat-23-to-auto-feel",
        requested_mode="auto",
        frame=bytes.fromhex(
            "BB0001031901004408080000000000000000000000000000000000000000E5"
        ),
        source=_state(**_COMMON, mode="heat", temperature=23.0),
        target=_state(**_COMMON, mode="auto", temperature=23.0),
        source_fields=MODE_FIELDS,
        target_fields=NON_SETPOINT_MODE_FIELDS,
        dynamic_target_temperature=True,
    ),
    OfficialSdkModeTransition(
        key="mode-auto-feel-21-to-cool-21",
        requested_mode="cool",
        frame=bytes.fromhex(
            "BB00010319010044030A0000000000000000000000000000000000000000EC"
        ),
        source=_state(**_COMMON, mode="auto", temperature=21.0),
        target=_state(**_COMMON, mode="cool", temperature=21.0),
        source_fields=MODE_FIELDS,
        target_fields=MODE_FIELDS,
    ),
    OfficialSdkModeTransition(
        key="mode-auto-feel-23-to-cool-23",
        requested_mode="cool",
        frame=bytes.fromhex(
            "BB0001031901004403080000000000000000000000000000000000000000EE"
        ),
        source=_state(**_COMMON, mode="auto", temperature=23.0),
        target=_state(**_COMMON, mode="cool", temperature=23.0),
        source_fields=MODE_FIELDS,
        target_fields=MODE_FIELDS,
    ),
    OfficialSdkModeTransition(
        key="mode-auto-feel-20-to-cool-20",
        requested_mode="cool",
        frame=bytes.fromhex(
            "BB00010319010044030B0000000000000000000000000000000000000000ED"
        ),
        source=_state(**_COMMON, mode="auto", temperature=20.0),
        target=_state(**_COMMON, mode="cool", temperature=20.0),
        source_fields=MODE_FIELDS,
        target_fields=MODE_FIELDS,
    ),
    OfficialSdkModeTransition(
        key="mode-cool-21-to-dry",
        requested_mode="dry",
        frame=bytes.fromhex(
            "BB00010319010044020A0000000000000000000000000000000000000000ED"
        ),
        source=_state(**_COMMON, mode="cool", temperature=21.0),
        target=_state(**_COMMON, mode="dry"),
        source_fields=MODE_FIELDS,
        target_fields=NON_SETPOINT_MODE_FIELDS,
    ),
)

QUALIFIED_OFFICIAL_SDK_MODE_COMMANDS = frozenset(
    transition.frame for transition in OFFICIAL_SDK_MODE_TRANSITIONS
)


def state_mismatches(
    expected: Mapping[str, Any],
    observed: Mapping[str, Any],
    fields: tuple[str, ...],
) -> list[str]:
    """Return exact field mismatches for one transition boundary."""

    return [field for field in fields if observed.get(field) != expected.get(field)]


def select_official_sdk_mode_transition(
    requested_mode: str,
    authoritative_state: Mapping[str, Any],
) -> OfficialSdkModeTransition:
    """Select exactly one qualified edge from its exact live source shape."""

    mode = str(requested_mode).strip().lower()
    matches = [
        transition
        for transition in OFFICIAL_SDK_MODE_TRANSITIONS
        if transition.requested_mode == mode
        and not state_mismatches(
            transition.source,
            authoritative_state,
            transition.source_fields,
        )
    ]
    if len(matches) != 1:
        raise YorkProtocolError(
            "authoritative direct state is outside the qualified official-SDK "
            "mode loop"
        )
    return matches[0]


def validate_official_sdk_mode_command(frame: bytes) -> None:
    """Reject every mode frame outside the qualified SDK edges."""

    if frame not in QUALIFIED_OFFICIAL_SDK_MODE_COMMANDS:
        raise YorkProtocolError(
            "Safety interlock rejected a non-canonical official-SDK mode command"
        )


def _by_key(key: str) -> OfficialSdkModeTransition:
    return next(item for item in OFFICIAL_SDK_MODE_TRANSITIONS if item.key == key)


def _build_exact(
    transition: OfficialSdkModeTransition,
    authoritative_state: Mapping[str, Any],
) -> bytes:
    mismatches = state_mismatches(
        transition.source,
        authoritative_state,
        transition.source_fields,
    )
    if mismatches:
        raise YorkProtocolError(
            f"{transition.key} requires its exact official-SDK source state: "
            + ", ".join(mismatches)
        )
    return transition.frame


# Named evidence views preserve the Alpha.75-80 test/report vocabulary while
# keeping every byte and state definition owned by the single registry above.
_DRY_FAN = _by_key("mode-dry-to-fan-only")
_FAN_HEAT = _by_key("mode-fan-only-to-heat-23")
_HEAT_AUTO = _by_key("mode-heat-23-to-auto-feel")
_AUTO_COOL = _by_key("mode-auto-feel-21-to-cool-21")
_AUTO_23_COOL = _by_key("mode-auto-feel-23-to-cool-23")
_AUTO_20_COOL = _by_key("mode-auto-feel-20-to-cool-20")
_COOL_DRY = _by_key("mode-cool-21-to-dry")

OFFICIAL_SDK_DRY_17_AUTO_OFF_TO_FAN_ONLY = _DRY_FAN.frame
OFFICIAL_SDK_FAN_ONLY_SOURCE = _DRY_FAN.source
OFFICIAL_SDK_FAN_ONLY_TARGET = _DRY_FAN.target
QUALIFIED_FAN_ONLY_QUALIFICATION_COMMANDS = frozenset({_DRY_FAN.frame})

OFFICIAL_SDK_FAN_ONLY_AUTO_OFF_TO_HEAT_23 = _FAN_HEAT.frame
OFFICIAL_SDK_FAN_ONLY_HEAT_SOURCE = _FAN_HEAT.source
OFFICIAL_SDK_FAN_ONLY_HEAT_TARGET = _FAN_HEAT.target
QUALIFIED_FAN_ONLY_HEAT_QUALIFICATION_COMMANDS = frozenset({_FAN_HEAT.frame})

OFFICIAL_SDK_HEAT_23_AUTO_OFF_TO_AUTO_FEEL = _HEAT_AUTO.frame
OFFICIAL_SDK_HEAT_AUTO_SOURCE = _HEAT_AUTO.source
OFFICIAL_SDK_HEAT_AUTO_TARGET = _HEAT_AUTO.target
QUALIFIED_HEAT_AUTO_QUALIFICATION_COMMANDS = frozenset({_HEAT_AUTO.frame})

OFFICIAL_SDK_AUTO_FEEL_21_AUTO_OFF_TO_COOL_21 = _AUTO_COOL.frame
OFFICIAL_SDK_AUTO_COOL_SOURCE = _AUTO_COOL.source
OFFICIAL_SDK_AUTO_COOL_TARGET = _AUTO_COOL.target
QUALIFIED_AUTO_COOL_QUALIFICATION_COMMANDS = frozenset({_AUTO_COOL.frame})

OFFICIAL_SDK_AUTO_FEEL_23_AUTO_OFF_TO_COOL_23 = _AUTO_23_COOL.frame
OFFICIAL_SDK_AUTO_23_COOL_SOURCE = _AUTO_23_COOL.source
OFFICIAL_SDK_AUTO_23_COOL_TARGET = _AUTO_23_COOL.target
QUALIFIED_AUTO_23_COOL_QUALIFICATION_COMMANDS = frozenset(
    {_AUTO_23_COOL.frame}
)

OFFICIAL_SDK_AUTO_FEEL_20_AUTO_OFF_TO_COOL_20 = _AUTO_20_COOL.frame
OFFICIAL_SDK_AUTO_20_COOL_SOURCE = _AUTO_20_COOL.source
OFFICIAL_SDK_AUTO_20_COOL_TARGET = _AUTO_20_COOL.target
QUALIFIED_AUTO_20_COOL_QUALIFICATION_COMMANDS = frozenset(
    {_AUTO_20_COOL.frame}
)

OFFICIAL_SDK_COOL_21_AUTO_OFF_TO_DRY = _COOL_DRY.frame
OFFICIAL_SDK_COOL_DRY_SOURCE = _COOL_DRY.source
OFFICIAL_SDK_COOL_DRY_TARGET = _COOL_DRY.target
QUALIFIED_COOL_DRY_QUALIFICATION_COMMANDS = frozenset({_COOL_DRY.frame})


def build_official_sdk_fan_only_qualification(state: Mapping[str, Any]) -> bytes:
    return _build_exact(_DRY_FAN, state)


def validate_official_sdk_fan_only_qualification(frame: bytes) -> None:
    if frame != _DRY_FAN.frame:
        validate_official_sdk_mode_command(b"")


def build_official_sdk_fan_only_heat_qualification(state: Mapping[str, Any]) -> bytes:
    return _build_exact(_FAN_HEAT, state)


def validate_official_sdk_fan_only_heat_qualification(frame: bytes) -> None:
    if frame != _FAN_HEAT.frame:
        validate_official_sdk_mode_command(b"")


def build_official_sdk_heat_auto_qualification(state: Mapping[str, Any]) -> bytes:
    return _build_exact(_HEAT_AUTO, state)


def validate_official_sdk_heat_auto_qualification(frame: bytes) -> None:
    if frame != _HEAT_AUTO.frame:
        validate_official_sdk_mode_command(b"")


def build_official_sdk_auto_cool_qualification(state: Mapping[str, Any]) -> bytes:
    return _build_exact(_AUTO_COOL, state)


def validate_official_sdk_auto_cool_qualification(frame: bytes) -> None:
    if frame != _AUTO_COOL.frame:
        validate_official_sdk_mode_command(b"")


def build_official_sdk_auto_23_cool_qualification(
    state: Mapping[str, Any],
) -> bytes:
    return _build_exact(_AUTO_23_COOL, state)


def validate_official_sdk_auto_23_cool_qualification(frame: bytes) -> None:
    if frame != _AUTO_23_COOL.frame:
        validate_official_sdk_mode_command(b"")


def build_official_sdk_auto_20_cool_qualification(
    state: Mapping[str, Any],
) -> bytes:
    return _build_exact(_AUTO_20_COOL, state)


def validate_official_sdk_auto_20_cool_qualification(frame: bytes) -> None:
    if frame != _AUTO_20_COOL.frame:
        validate_official_sdk_mode_command(b"")


def build_official_sdk_cool_dry_qualification(state: Mapping[str, Any]) -> bytes:
    return _build_exact(_COOL_DRY, state)


def validate_official_sdk_cool_dry_qualification(frame: bytes) -> None:
    if frame != _COOL_DRY.frame:
        validate_official_sdk_mode_command(b"")
