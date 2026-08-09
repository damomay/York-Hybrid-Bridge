from __future__ import annotations

import pytest

from adapters.york.decoder import YorkPacketDecoder
from adapters.york.errors import YorkFrameError


def frame(value: str) -> bytes:
    return bytes.fromhex(value)


def test_decodes_cooling_state() -> None:
    state = YorkPacketDecoder().decode_state(
        frame("BB 01 00 03 0F 01 00 31 06 00 00 00 00 00 00 00 00 5F 00 00 DF")
    )
    assert state.power is True
    assert state.mode == "cool"
    assert state.fan == "auto"
    assert state.swing == "off"
    assert state.turbo is False
    assert state.eco is False


def test_decodes_fan_swing_and_options() -> None:
    decoder = YorkPacketDecoder()

    medium = decoder.decode_state(
        frame("BB 01 00 03 0F 01 00 34 29 20 00 00 00 00 00 00 00 61 08 00 E3")
    )
    assert medium.mode == "heat"
    assert medium.fan == "medium"

    horizontal = decoder.decode_state(
        frame("BB 01 00 03 0F 01 00 34 09 20 20 00 00 00 00 00 00 61 08 00 E3")
    )
    assert horizontal.swing == "horizontal"

    vertical = decoder.decode_state(
        frame("BB 01 00 03 0F 01 00 34 09 20 40 00 00 00 00 00 00 64 00 00 8E")
    )
    assert vertical.swing == "vertical"

    turbo = decoder.decode_state(
        frame("BB 01 00 03 0F 01 00 B4 0F 20 00 00 00 00 00 00 00 64 00 00 48")
    )
    assert turbo.turbo is True

    eco = decoder.decode_state(
        frame("BB 01 00 03 0F 01 00 74 09 20 00 00 00 00 00 00 00 66 08 00 84")
    )
    assert eco.eco is True

    health = decoder.decode_state(
        frame("BB 01 00 03 0F 01 00 34 09 24 00 00 00 00 00 00 00 66 08 00 C0")
    )
    assert health.health is True


def test_display_flag_observation() -> None:
    decoder = YorkPacketDecoder()
    display_on = decoder.decode_state(
        frame("BB 01 00 03 0F 01 00 34 07 20 00 00 00 00 00 00 00 6B 08 00 C7")
    )
    display_off = decoder.decode_state(
        frame("BB 01 00 03 0F 01 00 14 07 20 00 00 00 00 00 00 00 6B 08 00 E7")
    )
    assert display_on.display is True
    assert display_off.display is False
    assert display_on.power is True
    assert display_off.power is True


def test_rejects_checksum_error() -> None:
    corrupted = frame(
        "BB 01 00 03 0F 01 00 34 09 20 00 00 00 00 00 00 00 61 08 00 00"
    )
    with pytest.raises(YorkFrameError, match="checksum mismatch"):
        YorkPacketDecoder().decode_state(corrupted)
