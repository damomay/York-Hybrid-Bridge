import json
from pathlib import Path

import pytest

from adapters.york.errors import YorkProtocolNotReady
from protocols.york.packet_library import find_verified_state_request, load_packet_record


def write_record(path: Path, **changes):
    data = {
        "id": "state-request-01",
        "protocol": "york_tfiac_20014",
        "kind": "state_request",
        "direction": "controller_to_device",
        "frame_hex": "BB 00 00 00",
        "source": {"capture_file": "test.txt", "tool": "test"},
        "verification": {"status": "verified", "safe_to_transmit": True, "replay_count": 1, "successful_responses": 1},
    }
    data.update(changes)
    path.write_text(json.dumps(data), encoding="utf-8")


def test_verified_state_request_is_executable(tmp_path):
    path = tmp_path / "state-request-01.json"
    write_record(path)
    record = find_verified_state_request(tmp_path)
    assert record.executable
    assert record.frame == bytes.fromhex("BB000000")


@pytest.mark.parametrize("changes", [
    {"verification": {"status": "observed", "replay_count": 0, "successful_responses": 0}},
    {"direction": "device_to_controller"},
    {"kind": "power_on"},
])
def test_non_verified_or_wrong_purpose_is_not_executable(tmp_path, changes):
    write_record(tmp_path / "record.json", **changes)
    with pytest.raises(YorkProtocolNotReady):
        find_verified_state_request(tmp_path)


def test_template_is_ignored(tmp_path):
    write_record(tmp_path / "template.json")
    with pytest.raises(YorkProtocolNotReady):
        find_verified_state_request(tmp_path)


def test_record_requires_bb_header(tmp_path):
    path = tmp_path / "bad.json"
    write_record(path, frame_hex="AA 00 00 00")
    with pytest.raises(Exception, match="0xBB"):
        load_packet_record(path)
