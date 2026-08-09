from adapters.york.cool_fan_auto_temperature_qualification import (
    COOL_20_FAN_AUTO_SOURCE,
    COOL_20_TO_20_5_FAN_AUTO_COMMAND,
    build_cool_20_to_20_5_fan_auto_command,
)


def test_cool_20_to_20_5_fan_auto_command_is_exact():
    assert build_cool_20_to_20_5_fan_auto_command(
        COOL_20_FAN_AUTO_SOURCE, 20.5
    ) == COOL_20_TO_20_5_FAN_AUTO_COMMAND
