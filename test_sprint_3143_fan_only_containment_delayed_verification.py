from adapters.york.official_sdk_mode_transitions import (
    OFFICIAL_SDK_FAN_ONLY_SOURCE,
    OFFICIAL_SDK_FAN_ONLY_TARGET,
)


def test_fan_only_transition_is_exactly_contained():
    assert OFFICIAL_SDK_FAN_ONLY_SOURCE["mode"] == "dry"
    assert OFFICIAL_SDK_FAN_ONLY_TARGET["mode"] == "fan_only"
    assert "temperature" not in OFFICIAL_SDK_FAN_ONLY_TARGET
    assert OFFICIAL_SDK_FAN_ONLY_TARGET["power"] is True
