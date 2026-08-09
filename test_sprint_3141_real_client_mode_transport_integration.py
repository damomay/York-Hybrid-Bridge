from adapters.york.official_sdk_mode_transitions import (
    OFFICIAL_SDK_MODE_TRANSITIONS,
    QUALIFIED_OFFICIAL_SDK_MODE_COMMANDS,
)


def test_consolidated_mode_commands_are_exact_and_separately_allowlisted():
    commands = {item.frame for item in OFFICIAL_SDK_MODE_TRANSITIONS}
    assert len(commands) == len(OFFICIAL_SDK_MODE_TRANSITIONS)
    assert commands == QUALIFIED_OFFICIAL_SDK_MODE_COMMANDS
    assert all(frame.startswith(bytes.fromhex("BB00010319")) for frame in commands)
