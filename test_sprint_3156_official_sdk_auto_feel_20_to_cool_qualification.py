from adapters.york.official_sdk_mode_transitions import (
    OFFICIAL_SDK_AUTO_20_COOL_SOURCE,
    OFFICIAL_SDK_AUTO_FEEL_20_AUTO_OFF_TO_COOL_20,
    QUALIFIED_AUTO_20_COOL_QUALIFICATION_COMMANDS,
    build_official_sdk_auto_20_cool_qualification,
)


def test_auto_feel_20_to_cool_20_is_exactly_allowlisted():
    frame = build_official_sdk_auto_20_cool_qualification(
        OFFICIAL_SDK_AUTO_20_COOL_SOURCE
    )
    assert frame == OFFICIAL_SDK_AUTO_FEEL_20_AUTO_OFF_TO_COOL_20
    assert QUALIFIED_AUTO_20_COOL_QUALIFICATION_COMMANDS == frozenset({frame})
