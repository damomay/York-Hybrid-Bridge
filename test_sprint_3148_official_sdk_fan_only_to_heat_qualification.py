import pytest

from adapters.york.errors import YorkProtocolError
from adapters.york.official_sdk_mode_transitions import (
    OFFICIAL_SDK_FAN_ONLY_AUTO_OFF_TO_HEAT_23,
    OFFICIAL_SDK_FAN_ONLY_HEAT_SOURCE,
    QUALIFIED_FAN_ONLY_HEAT_QUALIFICATION_COMMANDS,
    build_official_sdk_fan_only_heat_qualification,
)


def test_fan_only_to_heat_frame_is_exactly_allowlisted():
    frame = build_official_sdk_fan_only_heat_qualification(
        OFFICIAL_SDK_FAN_ONLY_HEAT_SOURCE
    )
    assert frame == OFFICIAL_SDK_FAN_ONLY_AUTO_OFF_TO_HEAT_23
    assert QUALIFIED_FAN_ONLY_HEAT_QUALIFICATION_COMMANDS == frozenset({frame})


def test_fan_only_to_heat_rejects_wrong_source_mode():
    with pytest.raises(YorkProtocolError):
        build_official_sdk_fan_only_heat_qualification(
            {**OFFICIAL_SDK_FAN_ONLY_HEAT_SOURCE, "mode": "dry"}
        )
