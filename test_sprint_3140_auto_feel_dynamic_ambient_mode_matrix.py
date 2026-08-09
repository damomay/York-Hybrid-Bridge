from adapters.york.official_sdk_mode_transitions import (
    OFFICIAL_SDK_HEAT_AUTO_SOURCE,
    OFFICIAL_SDK_MODE_TRANSITIONS,
)


def test_auto_feel_transition_preserves_dynamic_temperature_semantics():
    transition = next(
        item
        for item in OFFICIAL_SDK_MODE_TRANSITIONS
        if item.key == "mode-heat-23-to-auto-feel"
    )
    assert transition.dynamic_target_temperature is True
    assert transition.source == OFFICIAL_SDK_HEAT_AUTO_SOURCE
    assert "temperature" not in transition.target_fields
