from pathlib import Path

import pytest

from adapters.york.connection import YorkConnection
from adapters.york.decoder import YorkPacketDecoder
from adapters.york.errors import YorkFrameError
from adapters.york.session import YorkProtocolSession
from configuration import load_config
from transport.york_direct_transport import YorkDirectTransport


def _direct_config(tmp_path: Path):
    path = tmp_path / "direct-config.yml"
    path.write_text("""
transport:
  type: york_direct
direct_read:
  enabled: true
  host: 192.0.2.30
  mac: 02:00:00:00:00:01
mqtt:
  host: 192.0.2.10
device:
  name: Test York
  unique_id: test_york
""", encoding="utf-8")
    return load_config(path)


def test_york_components_are_split_by_responsibility(tmp_path):
    transport = YorkDirectTransport(_direct_config(tmp_path))
    assert isinstance(transport.client, object)
    assert isinstance(transport.decoder, YorkPacketDecoder)


def test_captured_bb_frame_can_be_staged_without_state_guessing(tmp_path):
    transport = YorkDirectTransport(_direct_config(tmp_path))
    captured = bytes.fromhex("BB 01 00 03 0F 01 00 31 06 00 00 00 00 00 00 00 00 5F 00 00 DF")
    frame = transport.inspect_captured_frame(captured)
    assert frame.header == 0xBB
    assert frame.hex == captured.hex(" ").upper()


def test_non_bb_frame_is_rejected():
    with pytest.raises(YorkFrameError):
        YorkPacketDecoder().parse_frame(bytes.fromhex("AA 00 00 00"))
