import json
from pathlib import Path

from york_packet_classifier import classify


def test_classifier_identifies_status_frames_without_verifying(tmp_path: Path):
    packet_dir = tmp_path / "observed"
    packet_dir.mkdir()
    packet = {
        "id": "sample",
        "kind": "unknown",
        "direction": "unknown",
        "frame_hex": "BB 01 00 03 0F 01 00 35 07 20 00 00 00 00 00 00 00 5F 00 00 FA",
        "verification": {"status": "observed"},
    }
    (packet_dir / "sample.json").write_text(json.dumps(packet), encoding="utf-8")
    fixtures = (
        Path(__file__).parents[1]
        / "protocols/york/qualification/decoder_fixtures.json"
    )
    report = classify(packet_dir, fixtures, tmp_path / "reports", tmp_path / "classified")
    assert report["summary"]["state_responses"] == 1
    assert report["summary"]["state_requests"] == 0
    output = json.loads((tmp_path / "classified/sample.json").read_text())
    assert output["kind"] == "state_response"
    assert output["direction"] == "device_to_controller"
    assert output["verification"]["status"] == "observed"
    assert output["verification"]["safe_to_transmit"] is False
