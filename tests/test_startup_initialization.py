from pathlib import Path
from unittest.mock import patch

from bridge import ClimateBridge
from configuration import load_config


def test_bridge_initializes_diagnostics_before_transport_metadata(tmp_path):
    config_path = tmp_path / "config.yml"
    config_path.write_text(
        """
transport:
  type: relay
  base_url: http://192.0.2.20:8765
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
    assert bridge.diagnostics.transport_type == "tablet_relay"
