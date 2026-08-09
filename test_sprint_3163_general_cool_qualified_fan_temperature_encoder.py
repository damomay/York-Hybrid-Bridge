import pytest

from adapters.york.cool_fan_auto_temperature_qualification import (
    GENERAL_COOL_QUALIFIED_FAN_VALUES,
    encode_general_cool_qualified_fan_temperature,
)
from adapters.york.errors import YorkProtocolError


def test_general_encoder_is_distinct_for_each_qualified_fan():
    frames = {
        fan: encode_general_cool_qualified_fan_temperature(22.5, fan)
        for fan in GENERAL_COOL_QUALIFIED_FAN_VALUES
    }
    assert set(frames) == {"auto", "low", "high"}
    assert len(set(frames.values())) == 3
    with pytest.raises(YorkProtocolError):
        encode_general_cool_qualified_fan_temperature(22.5, "medium")
