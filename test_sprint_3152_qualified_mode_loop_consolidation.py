from adapters.york.official_sdk_mode_transitions import (
    OFFICIAL_SDK_MODE_TRANSITIONS,
    QUALIFIED_OFFICIAL_SDK_MODE_COMMANDS,
)


def test_mode_loop_registry_is_unique_and_complete():
    assert len({item.key for item in OFFICIAL_SDK_MODE_TRANSITIONS}) == len(
        OFFICIAL_SDK_MODE_TRANSITIONS
    )
    assert QUALIFIED_OFFICIAL_SDK_MODE_COMMANDS == frozenset(
        item.frame for item in OFFICIAL_SDK_MODE_TRANSITIONS
    )
