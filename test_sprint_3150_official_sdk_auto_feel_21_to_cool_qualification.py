from adapters.york.official_sdk_mode_transitions import (
    OFFICIAL_SDK_AUTO_COOL_SOURCE,
    OFFICIAL_SDK_AUTO_FEEL_21_AUTO_OFF_TO_COOL_21,
    QUALIFIED_AUTO_COOL_QUALIFICATION_COMMANDS,
    build_official_sdk_auto_cool_qualification,
)


def test_auto_feel_21_to_cool_21_is_exactly_allowlisted():
    frame = build_official_sdk_auto_cool_qualification(OFFICIAL_SDK_AUTO_COOL_SOURCE)
    assert frame == OFFICIAL_SDK_AUTO_FEEL_21_AUTO_OFF_TO_COOL_21
    assert QUALIFIED_AUTO_COOL_QUALIFICATION_COMMANDS == frozenset({frame})
