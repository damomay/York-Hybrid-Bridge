import pytest

from adapters.york.errors import YorkProtocolError
from adapters.york.official_sdk_mode_transitions import (
    OFFICIAL_SDK_HEAT_23_AUTO_OFF_TO_AUTO_FEEL,
    OFFICIAL_SDK_HEAT_AUTO_SOURCE,
    QUALIFIED_HEAT_AUTO_QUALIFICATION_COMMANDS,
    build_official_sdk_heat_auto_qualification,
)


def test_heat_to_auto_feel_frame_is_exactly_allowlisted():
    frame = build_official_sdk_heat_auto_qualification(OFFICIAL_SDK_HEAT_AUTO_SOURCE)
    assert frame == OFFICIAL_SDK_HEAT_23_AUTO_OFF_TO_AUTO_FEEL
    assert QUALIFIED_HEAT_AUTO_QUALIFICATION_COMMANDS == frozenset({frame})


def test_heat_to_auto_feel_rejects_wrong_source_temperature():
    with pytest.raises(YorkProtocolError):
        build_official_sdk_heat_auto_qualification(
            {**OFFICIAL_SDK_HEAT_AUTO_SOURCE, "temperature": 22.0}
        )
