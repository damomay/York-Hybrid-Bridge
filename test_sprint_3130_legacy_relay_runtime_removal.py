from dataclasses import replace
from pathlib import Path

import pytest

from configuration import load_config
from transport.factory import create_transport
from transport.native_command_boundary import NativeCommandBoundaryTransport


REMOVED_RUNTIME_FILES = (
    "relay_manager.py",
    "transport/relay_transport.py",
    "transport/relay_extraction_logger.py",
    "york_relay_extraction_report.py",
)


def test_relay_runtime_files_are_absent():
    for relative in REMOVED_RUNTIME_FILES:
        assert not Path(relative).exists(), relative


def test_production_dependencies_contain_no_http_client():
    requirements = Path("requirements.txt").read_text(encoding="utf-8")
    assert "requests" not in requirements


def test_new_configuration_contains_no_relay_endpoint_or_fallback():
    example = Path("config.example.yml").read_text(encoding="utf-8")
    config = load_config(Path("config.example.yml"))

    assert "base_url:" not in example
    assert "fallback_to_relay:" not in example
    assert not hasattr(config, "transport_url")
    assert not hasattr(config, "direct_control_fallback_to_relay")


@pytest.mark.parametrize("legacy_type", ["relay", "tablet_relay"])
def test_legacy_transport_alias_maps_to_native_boundary(legacy_type):
    config = replace(
        load_config(Path("config.example.yml")),
        transport_type=legacy_type,
        direct_read_enabled=True,
    )
    assert isinstance(create_transport(config), NativeCommandBoundaryTransport)


def test_native_boundary_has_no_fallback_execution_surface():
    config = replace(
        load_config(Path("config.example.yml")),
        direct_read_enabled=True,
    )
    transport = create_transport(config)

    assert transport.command_fallback_enabled is False
    assert not hasattr(transport, "session")
    with pytest.raises(RuntimeError, match="qualified native allowlist"):
        transport.command(eco=True)


def test_docker_does_not_copy_removed_relay_executables():
    dockerfile = Path("Dockerfile").read_text(encoding="utf-8")
    assert "relay_manager.py" not in dockerfile
    assert "york_relay_extraction_report.py" not in dockerfile
