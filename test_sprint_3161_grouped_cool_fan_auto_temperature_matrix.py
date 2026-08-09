from adapters.york.cool_fan_auto_temperature_qualification import (
    GROUPED_COOL_FAN_AUTO_TEMPERATURE_MATRIX,
    build_grouped_cool_fan_auto_temperature_command,
)


def test_every_grouped_edge_builds_its_exact_allowlisted_frame():
    for (source, target), frame in GROUPED_COOL_FAN_AUTO_TEMPERATURE_MATRIX.items():
        state = {
            "power": True,
            "mode": "cool",
            "temperature": source,
            "fan": "auto",
            "swing": "off",
            "turbo": False,
            "eco": False,
            "health": False,
            "display": True,
        }
        assert build_grouped_cool_fan_auto_temperature_command(state, target) == frame
