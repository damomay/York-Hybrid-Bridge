from pathlib import Path

import pytest

from configuration import load_config
from transport import YorkDirectTransport, create_transport
from transport.native_command_boundary import NativeCommandBoundaryTransport


BASE = "\nmqtt:\n  host: 192.0.2.10\ndevice:\n  name: Test AC\n  unique_id: test_ac\n"


def load(tmp_path: Path, body: str):
    path = tmp_path / "config.yml"
    path.write_text(body + BASE, encoding="utf-8")
    return load_config(path)


def test_native_transport_is_default_and_fail_closed(tmp_path):
    cfg = load(tmp_path, "")
    with pytest.raises(ValueError, match="direct_read.enabled"):
        create_transport(cfg)


def test_native_transport_is_selectable(tmp_path):
    cfg = load(tmp_path, "transport:\n  type: native\ndirect_read:\n  enabled: true\n  host: 192.0.2.30\n  mac: 02:00:00:00:00:01\n")
    assert isinstance(create_transport(cfg), NativeCommandBoundaryTransport)


def test_york_direct_is_selectable_without_connecting(tmp_path):
    cfg = load(tmp_path, "transport:\n  type: york_direct\ndirect_read:\n  enabled: true\n  host: 192.0.2.30\n  mac: 02:00:00:00:00:01\n")
    transport = create_transport(cfg)
    assert isinstance(transport, YorkDirectTransport)
    assert transport.connected is False
