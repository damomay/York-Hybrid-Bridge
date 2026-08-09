from pathlib import Path

from adapters.york.official_sdk_mode_transitions import (
    OFFICIAL_SDK_MODE_TRANSITIONS,
)


def test_legacy_remaining_mode_matrix_is_removed_after_consolidation():
    assert not Path("adapters/york/remaining_mode_matrix.py").exists()
    assert not Path("adapters/york/remaining_mode_matrix.pyc").exists()


def test_auto_and_cool_dry_edges_are_owned_by_the_consolidated_registry():
    keys = {item.key for item in OFFICIAL_SDK_MODE_TRANSITIONS}
    assert "mode-heat-23-to-auto-feel" in keys
    assert "mode-auto-feel-21-to-cool-21" in keys
    assert "mode-cool-21-to-dry" in keys
