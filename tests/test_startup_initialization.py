from pathlib import Path
from unittest.mock import patch

from bridge import ClimateBridge
from configuration import load_config


def test_bridge_initializes_diagnostics_before_transport_metadata(tmp_path):
    config_path = tmp_path / "config.yml"
    config_path.write_text(
        """
transport:
  type: native
direct_read:
  enabled: true
  host: 192.0.2.30
  mac: 02:00:00:00:00:01
mqtt:
  host: 192.0.2.10
device:
  name: Test York
""",
        encoding="utf-8",
    )
    config = load_config(config_path)
    with patch("bridge.MqttManager"):
        bridge = ClimateBridge(config)
    assert bridge.diagnostics.transport_type == "york_native_boundary"
