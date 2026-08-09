import pytest

from adapters.york.errors import YorkProtocolError
from adapters.york.official_sdk_mode_transitions import (
    OFFICIAL_SDK_DRY_17_AUTO_OFF_TO_FAN_ONLY,
    OFFICIAL_SDK_FAN_ONLY_SOURCE,
    QUALIFIED_FAN_ONLY_QUALIFICATION_COMMANDS,
    build_official_sdk_fan_only_qualification,
)


def test_official_sdk_fan_only_frame_is_exactly_allowlisted():
    frame = build_official_sdk_fan_only_qualification(OFFICIAL_SDK_FAN_ONLY_SOURCE)
    assert frame == OFFICIAL_SDK_DRY_17_AUTO_OFF_TO_FAN_ONLY
    assert QUALIFIED_FAN_ONLY_QUALIFICATION_COMMANDS == frozenset({frame})


def test_fan_only_builder_rejects_a_mismatched_source():
    with pytest.raises(YorkProtocolError):
        build_official_sdk_fan_only_qualification(
            {**OFFICIAL_SDK_FAN_ONLY_SOURCE, "mode": "cool"}
        )
