import pytest

from adapters.york.cool_fan_auto_temperature_qualification import (
    encode_general_cool_fan_auto_temperature,
)
from adapters.york.errors import YorkProtocolError


def test_general_fan_auto_encoder_covers_half_degree_range_and_rejects_bounds():
    frames = {encode_general_cool_fan_auto_temperature(step / 2) for step in range(32, 63)}
    assert len(frames) == 31
    with pytest.raises(YorkProtocolError):
        encode_general_cool_fan_auto_temperature(15.5)
    with pytest.raises(YorkProtocolError):
        encode_general_cool_fan_auto_temperature(31.5)
