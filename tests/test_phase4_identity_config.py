from pathlib import Path
from unittest.mock import Mock, patch

import pytest
import yaml

from configuration import ConfigError, load_config
from mqtt_manager import MqttManager
from validate_config import validate
from version import APP_NAME, APP_VERSION, __version__


ROOT = Path(__file__).resolve().parents[1]


def _write_config(tmp_path: Path, text: str) -> Path:
    path = tmp_path / "config.yml"
    path.write_text(text, encoding="utf-8")
    return path


def test_version_file_is_the_single_canonical_version_source():
    assert (ROOT / "VERSION").read_text(encoding="utf-8").strip() == "1.0.0-alpha.20"
    assert APP_NAME == "Climate Bridge"
    assert APP_VERSION == "1.0.0-alpha.20"
    assert __version__ == APP_VERSION


def test_runtime_and_container_use_canonical_identity_without_stale_versions():
    current_files = [
        ROOT / "bridge.py",
        ROOT / "configuration.py",
        ROOT / "discovery_manager.py",
        ROOT / "Dockerfile",
        ROOT / "docker-compose.yml",
        ROOT / "config.example.yml",
        ROOT / "york_replay_engine.py",
        ROOT / "york_relay_extraction_report.py",
    ]
    combined = "\n".join(path.read_text(encoding="utf-8") for path in current_files)
    assert "York Hybrid Bridge" not in combined
    assert "3.0.0-dev" not in combined
    assert "1.0.0-alpha.18" not in combined
    assert 'org.opencontainers.image.title="Climate Bridge"' in combined
    assert "COPY VERSION version.py" in combined


def test_committed_example_is_safe_valid_and_uses_optional_credentials():
    raw = yaml.safe_load((ROOT / "config.example.yml").read_text(encoding="utf-8"))
    assert raw["transport"]["type"] == "relay"
    assert raw["direct_device"]["enabled"] is False
    assert raw["direct_device"]["host"] == ""
    assert raw["direct_device"]["mac"] == ""
    assert raw["mqtt"]["username"] == ""
    assert raw["mqtt"]["password"] == ""
    assert raw["device"]["bridge_name"] == APP_NAME

    config = load_config(ROOT / "config.example.yml")
    assert config.transport_type == "relay"
    assert config.direct_enabled is False
    assert config.mqtt_username == ""
    assert config.mqtt_password == ""
    assert validate(ROOT / "config.example.yml") == "relay"


def test_empty_password_is_passed_when_username_auth_is_configured(tmp_path: Path):
    path = _write_config(
        tmp_path,
        """
transport:
  type: relay
  base_url: http://192.0.2.20:8765
mqtt:
  host: 192.0.2.10
  username: bridge-user
  password: ""
device:
  name: Test York
  unique_id: test_york
""",
    )
    config = load_config(path)
    client = Mock()
    with patch("mqtt_manager.mqtt.Client", return_value=client):
        MqttManager(
            config,
            on_message=Mock(),
            on_connected=Mock(),
            on_disconnected=Mock(),
        )
    client.username_pw_set.assert_called_once_with("bridge-user", "")


@pytest.mark.parametrize(
    ("replacement", "message"),
    [
        ("type: unsupported", "Unsupported transport type"),
        ("type: relay\n  base_url: 192.0.2.20:8765", "must start with"),
        ("type: relay\n  base_url: http://192.0.2.20:8765\n  timeout_seconds: invalid", "Invalid configuration value"),
    ],
)
def test_invalid_configuration_fails_clearly(
    tmp_path: Path,
    replacement: str,
    message: str,
):
    path = _write_config(
        tmp_path,
        f"""
transport:
  {replacement}
mqtt:
  host: 192.0.2.10
device:
  name: Test York
  unique_id: test_york
""",
    )
    with pytest.raises(ConfigError, match=message):
        load_config(path)


def test_disabled_direct_mode_is_rejected_by_startup_validator(tmp_path: Path):
    path = _write_config(
        tmp_path,
        """
transport:
  type: york_direct
direct_device:
  enabled: false
  host: 192.0.2.30
  mac: 02:00:00:00:00:01
  state_request_hex: BB000000
mqtt:
  host: 192.0.2.10
device:
  name: Test York
  unique_id: test_york
""",
    )
    with pytest.raises(ConfigError, match="direct_device.enabled"):
        validate(path)
