from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from bridge import ClimateBridge, YorkBridge
from configuration import ConfigError, load_config
from transport import YorkDirectTransport, create_transport
from transport.native_command_boundary import NativeCommandBoundaryTransport


BASE = """
mqtt:
  host: 192.0.2.10
device:
  name: Test York
  unique_id: test_york
"""


def load(tmp_path: Path, transport: str):
    path = tmp_path / "config.yml"
    path.write_text(transport + BASE, encoding="utf-8")
    return load_config(path)


def test_legacy_relay_name_routes_to_native_only_when_native_is_enabled(tmp_path):
    config = load(tmp_path, "transport:\n  type: relay\ndirect_read:\n  enabled: true\n  host: 192.0.2.30\n  mac: 02:00:00:00:00:01\n")
    assert isinstance(create_transport(config), NativeCommandBoundaryTransport)


def test_native_transport_is_fail_closed_when_direct_read_is_disabled(tmp_path):
    config = load(tmp_path, "transport:\n  type: native\n")
    with pytest.raises(ValueError, match="direct_read.enabled"):
        create_transport(config)


def test_direct_transport_construction_does_not_open_socket(tmp_path):
    config = load(tmp_path, "transport:\n  type: york_direct\ndirect_read:\n  enabled: true\n  host: 192.0.2.30\n  mac: 02:00:00:00:00:01\n")
    transport = create_transport(config)
    assert isinstance(transport, YorkDirectTransport)
    assert transport.connected is False
    transport.close()


def test_invalid_configuration_keeps_clear_error(tmp_path):
    path = tmp_path / "config.yml"
    path.write_text("mqtt: []\ndevice: {}\n", encoding="utf-8")
    with pytest.raises(ConfigError):
        load_config(path)


def test_bridge_keeps_public_class_and_transport_metadata(tmp_path):
    config = load(tmp_path, "transport:\n  type: native\ndirect_read:\n  enabled: true\n  host: 192.0.2.30\n  mac: 02:00:00:00:00:01\n")
    fake_transport = Mock(spec=["name", "display_name", "command", "get_state", "close"])
    fake_transport.name = "york_native"
    fake_transport.display_name = "York Native"
    with patch("bridge.create_transport", return_value=fake_transport), patch("bridge.MqttManager"):
        bridge = ClimateBridge(config)
    assert YorkBridge is ClimateBridge
    assert bridge.transport is fake_transport
    assert bridge.diagnostics.transport_type == "york_native"
    assert not hasattr(bridge, "relay")
