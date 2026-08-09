from __future__ import annotations

from pathlib import Path

import pytest

from adapters.york.broadlink import (
    YORK_QUALIFICATION_POWER_ON_COOL,
    YORK_QUALIFICATION_POWER_ON_HEAT,
)
from configuration import load_config
from direct_power_manager import (
    DIRECT_POWER_CASES,
    DirectPowerManager,
    DirectPowerSafeStop,
)


def _case(name: str):
    return next(case for case in DIRECT_POWER_CASES if case.name == name)


@pytest.mark.parametrize(
    ("name", "before_mode", "after_mode", "command"),
    [
        (
            "heat-to-cool",
            "heat",
            "cool",
            YORK_QUALIFICATION_POWER_ON_COOL,
        ),
        (
            "cool-to-heat",
            "cool",
            "heat",
            YORK_QUALIFICATION_POWER_ON_HEAT,
        ),
    ],
)
def test_running_mode_case_is_locked_for_normal_control(
    name: str,
    before_mode: str,
    after_mode: str,
    command: bytes,
):
    case = _case(name)

    assert case.requested == {"power": True, "mode": after_mode}
    assert case.before["power"] is True
    assert case.before["mode"] == before_mode
    assert case.after["power"] is True
    assert case.after["mode"] == after_mode
    assert case.command == command
    assert len(case.command) == 31


@pytest.mark.parametrize(
    ("name", "requested"),
    [
        ("heat-to-cool", {"power": True, "mode": "cool"}),
        ("cool-to-heat", {"power": True, "mode": "heat"}),
    ],
)
def test_running_mode_request_selects_fixture_from_exact_relay_state(
    name: str,
    requested: dict,
):
    case = _case(name)

    selected = DirectPowerManager._select_case_for_state(
        requested,
        dict(case.before),
    )

    assert selected.name == name
    assert selected.command == case.command


@pytest.mark.parametrize("name", ["heat-to-cool", "cool-to-heat"])
def test_running_mode_outside_qualified_state_creates_no_client(name: str):
    case = _case(name)
    config = load_config(Path("config.example.yml"))

    def forbidden_client(*_args, **_kwargs):
        raise AssertionError("client created for an unqualified mode state")

    manager = DirectPowerManager(config, client_factory=forbidden_client)
    state = {**case.before, "temperature": 24.0}

    with pytest.raises(DirectPowerSafeStop, match="qualified power shape"):
        manager.command(dict(case.requested), state)


def test_power_on_cases_remain_distinct_from_running_mode_cases():
    on_heat = _case("on-heat")
    on_cool = _case("on-cool")
    cool_to_heat = _case("cool-to-heat")
    heat_to_cool = _case("heat-to-cool")

    assert on_heat.requested == cool_to_heat.requested
    assert on_heat.before["power"] is False
    assert cool_to_heat.before["power"] is True
    assert on_cool.requested == heat_to_cool.requested
    assert on_cool.before["power"] is False
    assert heat_to_cool.before["power"] is True


def test_alpha38_exposes_six_guarded_power_and_mode_cases():
    assert tuple(case.name for case in DIRECT_POWER_CASES) == (
        "off",
        "off-heat",
        "on-heat",
        "on-cool",
        "heat-to-cool",
        "cool-to-heat",
    )
