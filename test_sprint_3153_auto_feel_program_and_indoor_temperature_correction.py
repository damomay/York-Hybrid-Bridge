from adapters.york.official_sdk_mode_transitions import OFFICIAL_SDK_MODE_TRANSITIONS


def test_auto_feel_program_keeps_dynamic_target_temperature():
    transitions = [
        item for item in OFFICIAL_SDK_MODE_TRANSITIONS if item.requested_mode == "auto"
    ]
    assert transitions
    assert all(item.dynamic_target_temperature for item in transitions)
    assert all("temperature" not in item.target_fields for item in transitions)
