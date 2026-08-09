from __future__ import annotations

from pathlib import Path

import pytest

from adapters.york.broadlink import YORK_QUALIFICATION_POWER_OFF_HEAT
from configuration import load_config
from direct_power_manager import (
    DIRECT_POWER_CASES,
    DirectPowerManager,
    DirectPowerSafeStop,
)


def _off_heat_case():
    return next(case for case in DIRECT_POWER_CASES if case.name == "off-heat")


def test_off_heat_is_a_locked_normal_control_case():
    case = _off_heat_case()

    assert case.requested == {"power": False}
    assert case.before["power"] is True
    assert case.before["mode"] == "heat"
    assert case.after["power"] is False
    assert case.after["mode"] == "heat"
    assert case.command == YORK_QUALIFICATION_POWER_OFF_HEAT
    assert len(case.command) == 31


def test_power_off_selects_heat_fixture_from_relay_state():
    case = _off_heat_case()

    selected = DirectPowerManager._select_case_for_state(
        {"power": False},
        dict(case.before),
    )

    assert selected.name == "off-heat"
    assert selected.command == YORK_QUALIFICATION_POWER_OFF_HEAT


def test_power_off_outside_all_qualified_states_creates_no_client():
    case = _off_heat_case()
    config = load_config(Path("config.example.yml"))

    def forbidden_client(*_args, **_kwargs):
        raise AssertionError("client created for an unqualified Power Off state")

    manager = DirectPowerManager(config, client_factory=forbidden_client)
    state = {**case.before, "fan": "auto"}

    with pytest.raises(DirectPowerSafeStop, match="qualified power shape"):
        manager.command({"power": False}, state)
