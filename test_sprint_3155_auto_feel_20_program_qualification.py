from adapters.york.official_sdk_mode_transitions import OFFICIAL_SDK_MODE_TRANSITIONS


def test_auto_feel_20_program_is_registered():
    transition = next(
        item
        for item in OFFICIAL_SDK_MODE_TRANSITIONS
        if item.key == "mode-auto-feel-20-to-cool-20"
    )
    assert transition.source["mode"] == "auto"
    assert transition.source["temperature"] == 20.0
