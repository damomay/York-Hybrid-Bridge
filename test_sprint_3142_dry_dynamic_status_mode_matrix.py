from adapters.york.official_sdk_mode_transitions import (
    OFFICIAL_SDK_COOL_DRY_SOURCE,
    OFFICIAL_SDK_COOL_DRY_TARGET,
)


def test_dry_transition_uses_non_setpoint_target_semantics():
    assert OFFICIAL_SDK_COOL_DRY_SOURCE["mode"] == "cool"
    assert OFFICIAL_SDK_COOL_DRY_TARGET["mode"] == "dry"
    assert "temperature" not in OFFICIAL_SDK_COOL_DRY_TARGET
