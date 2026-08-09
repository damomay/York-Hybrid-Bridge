from adapters.york.cool_fan_auto_temperature_qualification import (
    COOL_23_FAN_AUTO_SOURCE,
    COOL_23_TO_21_FAN_AUTO_COMMAND,
    build_cool_23_to_21_fan_auto_command,
)


def test_cool_23_to_21_fan_auto_command_is_exact():
    assert build_cool_23_to_21_fan_auto_command(
        COOL_23_FAN_AUTO_SOURCE, 21.0
    ) == COOL_23_TO_21_FAN_AUTO_COMMAND
