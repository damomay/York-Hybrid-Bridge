import json
from pathlib import Path

from york_request_hunter import hunt


def test_hunter_excludes_known_response_and_creates_no_candidate(tmp_path: Path):
    packets = tmp_path / "observed"
    packets.mkdir()
    (packets / "response.json").write_text(json.dumps({
        "id": "response",
        "kind": "unknown",
        "direction": "unknown",
        "frame_hex": "BB 01 00 03 0F 01 00 35 07 20 00 00 00 00 00 00 00 5F 00 00 FA",
        "verification": {"status": "observed"},
    }), encoding="utf-8")
    fixtures = Path(__file__).parent / "protocols/york/qualification/decoder_fixtures.json"
    candidate_dir = tmp_path / "candidates"
    report = hunt(packets, fixtures, tmp_path / "reports", candidate_dir=candidate_dir)
    assert report["summary"]["eligible_candidates"] == 0
    assert report["summary"]["excluded_known_responses"] == 1
    assert report["safety"]["records_verified"] == 0
    assert not candidate_dir.exists() or not list(candidate_dir.glob("*.json"))


def test_hunter_candidate_output_stays_non_executable(tmp_path: Path):
    packets = tmp_path / "observed"
    packets.mkdir()
    (packets / "candidate.json").write_text(json.dumps({
        "id": "candidate",
        "kind": "state_request",
        "direction": "controller_to_device",
        "frame_hex": "BB 00 00 01",
        "verification": {"status": "observed"},
    }), encoding="utf-8")
    fixtures_file = tmp_path / "fixtures.json"
    fixtures_file.write_text(json.dumps({"fixtures": []}), encoding="utf-8")
    candidate_dir = tmp_path / "candidates"
    report = hunt(packets, fixtures_file, tmp_path / "reports", candidate_dir=candidate_dir, minimum_score=60)
    # A four-byte observation has insufficient evidence to become a candidate.
    assert report["summary"]["eligible_candidates"] == 0
    assert not candidate_dir.exists() or not list(candidate_dir.glob("*.json"))
