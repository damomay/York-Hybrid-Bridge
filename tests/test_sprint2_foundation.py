from pathlib import Path
from unittest.mock import Mock, patch

from bridge import log_startup_banner
from configuration import load_config
from transport.york_direct_transport import YorkDirectTransport


def _write_config(
    tmp_path: Path,
    *,
    transport_type: str = "relay",
    password: str = "",
) -> Path:
    path = tmp_path / "config.yml"
    path.write_text(
        f"""
transport:
  type: {transport_type}
  base_url: http://192.0.2.20:8765
direct_device:
  enabled: true
  host: 192.0.2.30
  mac: 02:00:00:00:00:01
  state_request_hex: ""
mqtt:
  host: 192.0.2.10
  password: "{password}"
device:
  name: Test York
  unique_id: test_york
""",
        encoding="utf-8",
    )
    return path


def test_direct_transport_endpoint_is_validated_without_connecting(tmp_path):
    config = load_config(_write_config(tmp_path, transport_type="york_direct"))
    transport = YorkDirectTransport(config)
    assert not transport.connected

    assert transport.host == "192.0.2.30"
    assert transport.port == 80
    transport.close()
    assert not transport.connected


def test_startup_banner_does_not_include_password(tmp_path, monkeypatch):
    secret = "do-not-log-this-password"
    config = load_config(_write_config(tmp_path, password=secret))
    messages = []
    monkeypatch.setattr(
        "bridge.LOG.info",
        lambda message, *args: messages.append(message % args if args else message),
    )
    log_startup_banner(config, "relay")
    banner = "\n".join(messages)
    assert "Climate Bridge" in banner
    assert "York TFIAC" in banner
    assert secret not in banner
