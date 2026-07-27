from pathlib import Path

from configuration import load_config


def test_debug_defaults_disabled(tmp_path):
    config = tmp_path / "config.yml"
    config.write_text(
        """transport:
  type: relay
  base_url: http://192.0.2.20:8765
mqtt:
  host: 192.0.2.10
device:
  name: York
  unique_id: york
""",
        encoding="utf-8",
    )
    loaded = load_config(config)
    assert loaded.debug_enabled is False
    assert loaded.debug_native_compare is False
    assert loaded.debug_probe_on_startup is False
