from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from bridge import ClimateBridge, YorkBridge
from configuration import ConfigError, load_config
from transport import RelayTransport, YorkDirectTransport, create_transport


BASE = """
mqtt:
  host: 192.0.2.10
  port: 1883
device:
  name: Test York
  unique_id: test_york
"""


def load(tmp_path: Path, transport: str):
    path = tmp_path / "config.yml"
    path.write_text(transport + BASE, encoding="utf-8")
    return load_config(path)


def test_legacy_relay_configuration_remains_default(tmp_path: Path):
    config = load(
        tmp_path,
        "relay:\n  base_url: http://192.0.2.20:8765\n",
    )
    transport = create_transport(config)
    assert isinstance(transport, RelayTransport)
    assert config.relay_url == config.transport_url
    assert config.relay_timeout == config.transport_timeout
    transport.close()


def test_transport_configuration_selects_relay_without_network_io(tmp_path: Path):
    config = load(
        tmp_path,
        "transport:\n  type: relay\n  base_url: http://192.0.2.20:8765\n",
    )
    transport = create_transport(config)
    assert isinstance(transport, RelayTransport)
    assert transport.name == "tablet_relay"
    transport.close()


def test_direct_transport_is_disabled_by_default(tmp_path: Path):
    config = load(
        tmp_path,
        """
transport:
  type: york_direct
direct_device:
  host: 192.0.2.30
  mac: 02:00:00:00:00:01
  state_request_hex: BB 00 00 00
""",
    )
    with pytest.raises(ValueError, match="disabled"):
        create_transport(config)


def test_direct_transport_construction_does_not_open_socket(tmp_path: Path):
    config = load(
        tmp_path,
        """
transport:
  type: york_direct
direct_device:
  enabled: true
  host: 192.0.2.30
  mac: 02:00:00:00:00:01
  state_request_hex: BB 00 00 00
""",
    )
    transport = create_transport(config)
    assert isinstance(transport, YorkDirectTransport)
    assert transport.connected is False
    transport.close()


def test_invalid_configuration_keeps_clear_error(tmp_path: Path):
    path = tmp_path / "config.yml"
    path.write_text("mqtt: []\ndevice: {}\n", encoding="utf-8")
    with pytest.raises(ConfigError, match="transport"):
        load_config(path)


def test_bridge_keeps_legacy_public_class_and_transport_metadata(tmp_path: Path):
    config = load(
        tmp_path,
        "transport:\n  type: relay\n  base_url: http://192.0.2.20:8765\n",
    )
    fake_transport = Mock(
        name="transport",
        spec=["name", "display_name", "command", "get_state", "close"],
    )
    fake_transport.name = "tablet_relay"
    fake_transport.display_name = "Relay (Legacy)"
    with (
        patch("bridge.create_transport", return_value=fake_transport),
        patch("bridge.MqttManager"),
    ):
        bridge = ClimateBridge(config)
    assert YorkBridge is ClimateBridge
    assert bridge.transport is fake_transport
    assert bridge.relay is fake_transport
    assert bridge.diagnostics.transport_type == "tablet_relay"
