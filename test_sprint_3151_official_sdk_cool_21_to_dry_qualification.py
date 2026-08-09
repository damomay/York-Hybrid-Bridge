from adapters.york.official_sdk_mode_transitions import (
    OFFICIAL_SDK_COOL_21_AUTO_OFF_TO_DRY,
    OFFICIAL_SDK_COOL_DRY_SOURCE,
    QUALIFIED_COOL_DRY_QUALIFICATION_COMMANDS,
    build_official_sdk_cool_dry_qualification,
)


def test_cool_21_to_dry_is_exactly_allowlisted():
    frame = build_official_sdk_cool_dry_qualification(OFFICIAL_SDK_COOL_DRY_SOURCE)
    assert frame == OFFICIAL_SDK_COOL_21_AUTO_OFF_TO_DRY
    assert QUALIFIED_COOL_DRY_QUALIFICATION_COMMANDS == frozenset({frame})
