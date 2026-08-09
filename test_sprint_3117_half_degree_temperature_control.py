from __future__ import annotations

import pytest

from adapters.york.captured_temperature_command import (
    QUALIFIED_TEMPERATURES,
    build_captured_heat_high_vertical_temperature_command,
    validate_captured_heat_high_vertical_temperature_command,
)
from adapters.york.errors import YorkProtocolError
from adapters.york.low_vertical_temperature_command import (
    QUALIFIED_LOW_VERTICAL_TEMPERATURES,
    build_captured_heat_low_vertical_temperature_command,
    validate_captured_heat_low_vertical_temperature_command,
)
from test_sprint_3112_guarded_temperature_control import (
    _manager as high_vertical_manager,
    _state as high_vertical_state,
)
from test_sprint_3116_parameterised_low_vertical_control import (
    _manager as low_vertical_manager,
    _state as low_vertical_state,
)


@pytest.mark.parametrize(
    ("builder", "validator", "state_byte", "expected_25_5_hex"),
    [
        (
            build_captured_heat_high_vertical_temperature_command,
            validate_captured_heat_high_vertical_temperature_command,
            0x3D,
            "BB0001031901004401063D02000000000000000000000000000000000000DD",
        ),
        (
            build_captured_heat_low_vertical_temperature_command,
            validate_captured_heat_low_vertical_temperature_command,
            0x3A,
            "BB0001031901004401063A02000000000000000000000000000000000000DA",
        ),
    ],
)
def test_half_degree_frame_is_canonical_and_exact(
    builder,
    validator,
    state_byte,
    expected_25_5_hex,
):
    frame = builder(25.5)

    assert frame.hex().upper() == expected_25_5_hex
    assert frame[9] == 31 - 25
    assert frame[10] == state_byte
    assert frame[11] == 0x02
    assert validator(frame) == 25.5
    assert len(frame) == 31
    assert not any(frame[12:30])
    assert _xor(frame) == 0


def _xor(frame: bytes) -> int:
    value = 0
    for byte in frame:
        value ^= byte
    return value


@pytest.mark.parametrize(
    ("builder", "validator"),
    [
        (
            build_captured_heat_high_vertical_temperature_command,
            validate_captured_heat_high_vertical_temperature_command,
        ),
        (
            build_captured_heat_low_vertical_temperature_command,
            validate_captured_heat_low_vertical_temperature_command,
        ),
    ],
)
def test_complete_half_degree_range_is_canonical(builder, validator):
    expected = tuple(value / 2 for value in range(32, 63))

    for target in expected:
        frame = builder(target)
        assert validator(frame) == target
        assert frame[11] == (0x02 if target % 1 else 0x00)
        assert _xor(frame) == 0

    assert QUALIFIED_TEMPERATURES == expected
    assert QUALIFIED_LOW_VERTICAL_TEMPERATURES == expected


@pytest.mark.parametrize(
    "target",
    (15.5, 16.25, 25.25, 30.75, 31.5),
)
@pytest.mark.parametrize(
    "builder",
    [
        build_captured_heat_high_vertical_temperature_command,
        build_captured_heat_low_vertical_temperature_command,
    ],
)
def test_invalid_target_stops_at_generator(target, builder):
    with pytest.raises(YorkProtocolError):
        builder(target)


@pytest.mark.parametrize(
    ("manager_factory", "state_factory", "source", "path"),
    [
        (
            high_vertical_manager,
            high_vertical_state,
            "york_direct_temperature_captured",
            "captured_heat_high_vertical",
        ),
        (
            low_vertical_manager,
            low_vertical_state,
            "york_direct_temperature_low_vertical",
            "parameterised_heat_low_vertical",
        ),
    ],
)
@pytest.mark.parametrize(
    ("before", "target"),
    [
        (25.0, 25.5),
        (25.5, 25.0),
        (16.0, 16.5),
        (30.0, 30.5),
        (30.5, 31.0),
    ],
)
def test_normal_control_uses_native_half_degree_path(
    manager_factory,
    state_factory,
    source,
    path,
    before,
    target,
):
    manager, sock = manager_factory(before, target)

    response = manager.command(target, state_factory(before))

    assert response["temperature"] == target
    assert response["_transaction"]["source"] == source
    assert response["_transaction"]["qualified_path"] == path
    assert response["_transaction"]["verification"] == {
        "success": True,
        "matched_fields": 9,
        "compared_fields": 9,
    }
    assert response["_transaction"]["udp_sends"] == 4
    assert response["_transaction"]["automatic_retries"] == 0
    assert response["_transaction"]["fallback_used"] is False
    assert manager.last_udp_sends == 4
    assert len(sock.sent) == 4


def test_low_vertical_half_degree_preserves_fan_and_swing():
    manager, _sock = low_vertical_manager(25.0, 25.5)

    response = manager.command(25.5, low_vertical_state(25.0))

    assert response["fan"] == "low"
    assert response["swing"] == "vertical"
