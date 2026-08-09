from __future__ import annotations

from pathlib import Path

import pytest

from adapters.york.decoder import YorkPacketDecoder
from configuration import load_config
from direct_read_manager import DirectReadManager


def _status_frame(
    *,
    temperature: int,
    half_degree: bool = False,
    fan_nibble: int = 0,
) -> bytes:
    frame = bytearray.fromhex(
        "BB0100030F01003408200000000000000073000000"
    )
    frame[8] = ((fan_nibble & 0x0F) << 4) | ((temperature - 16) & 0x0F)
    frame[9] = 0x22 if half_degree else 0x20
    checksum = 0
    for value in frame[:-1]:
        checksum ^= value
    frame[-1] = checksum
    return bytes(frame)


@pytest.mark.parametrize(
    ("temperature", "half_degree", "expected"),
    [
        (20, False, 20.0),
        (20, True, 20.5),
        (24, False, 24.0),
        (25, False, 25.0),
    ],
)
def test_target_temperature_decodes_from_verified_status_fields(
    temperature: int,
    half_degree: bool,
    expected: float,
) -> None:
    state = YorkPacketDecoder().decode_state(
        _status_frame(temperature=temperature, half_degree=half_degree)
    )
    assert state.temperature == expected


@pytest.mark.parametrize(
    ("fan_nibble", "expected_fan"),
    [(0, "auto"), (1, "low"), (2, "medium"), (3, "high")],
)
def test_temperature_low_nibble_does_not_change_fan_mapping(
    fan_nibble: int,
    expected_fan: str,
) -> None:
    state = YorkPacketDecoder().decode_state(
        _status_frame(temperature=24, fan_nibble=fan_nibble)
    )
    assert state.temperature == 24.0
    assert state.fan == expected_fan


class _TemperatureTransport:
    last_response_length = 21
    last_send_count = 2
    last_raw_frame_hex = _status_frame(temperature=24).hex().upper()
    last_fan_status_byte = 0x08
    last_fan_status_nibble = 0

    def __init__(self, _config) -> None:
        pass

    def get_state(self) -> dict:
        return {
            "power": True,
            "mode": "heat",
            "temperature": 24.0,
            "fan": "auto",
        }

    def close(self) -> None:
        pass


def test_shadow_comparison_includes_target_temperature() -> None:
    config = load_config(Path("config.example.yml"))
    manager = DirectReadManager(
        config,
        transport_factory=_TemperatureTransport,
    )
    result = manager.observe(
        {
            "power": True,
            "mode": "heat",
            "temperature": 24.0,
            "fan": "auto",
        },
        now=100,
    )
    assert result is not None
    assert result.comparison == "match (4/4)"
    assert result.compared_fields == 4


def test_shadow_comparison_reports_temperature_mismatch() -> None:
    config = load_config(Path("config.example.yml"))
    manager = DirectReadManager(
        config,
        transport_factory=_TemperatureTransport,
    )
    result = manager.observe(
        {
            "power": True,
            "mode": "heat",
            "temperature": 25.0,
            "fan": "auto",
        },
        now=100,
    )
    assert result is not None
    assert result.comparison == "mismatch: temperature"


def test_misindented_direct_read_is_rejected(tmp_path: Path) -> None:
    source = Path("config.example.yml").read_text(encoding="utf-8")
    path = tmp_path / "config.yml"
    path.write_text(
        source.replace(
            "logging:\n  level: INFO",
            "logging:\n  level: INFO\n  direct_read:\n    enabled: true",
        ),
        encoding="utf-8",
    )
    with pytest.raises(ValueError, match="nested under logging"):
        load_config(path)
