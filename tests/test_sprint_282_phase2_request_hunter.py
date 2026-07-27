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
    fixtures = (
        Path(__file__).parents[1]
        / "protocols/york/qualification/decoder_fixtures.json"
    )
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
        "source": {"capture_file": "approved-full-duplex.log"},
        "observations": {
            "locations": [
                {
                    "capture_file": "approved-full-duplex.log",
                    "line_number": 42,
                    "timestamp": "2026-07-13 20:00:00.000",
                    "direction": "controller_to_device",
                }
            ]
        },
        "verification": {"status": "observed"},
    }), encoding="utf-8")
    fixtures_file = tmp_path / "fixtures.json"
    fixtures_file.write_text(json.dumps({"fixtures": []}), encoding="utf-8")
    candidate_dir = tmp_path / "candidates"
    report = hunt(packets, fixtures_file, tmp_path / "reports", candidate_dir=candidate_dir, minimum_score=60)
    assert report["summary"]["eligible_candidates"] == 1
    output = json.loads((candidate_dir / "candidate-candidate.json").read_text(encoding="utf-8"))
    assert output["verification"]["status"] == "observed"
    assert output["verification"]["safe_to_transmit"] is False


def test_hunter_rejects_label_only_candidate_without_capture_provenance(tmp_path: Path):
    packets = tmp_path / "observed"
    packets.mkdir()
    (packets / "ambiguous.json").write_text(json.dumps({
        "id": "ambiguous",
        "kind": "state_request",
        "direction": "controller_to_device",
        "frame_hex": "BB 00 00 01",
        "verification": {"status": "observed"},
    }), encoding="utf-8")
    fixtures_file = tmp_path / "fixtures.json"
    fixtures_file.write_text(json.dumps({"fixtures": []}), encoding="utf-8")

    report = hunt(packets, fixtures_file, tmp_path / "reports", minimum_score=60)

    assert report["summary"]["eligible_candidates"] == 0
    assert report["summary"]["excluded_incomplete_or_ambiguous"] == 1
    assert report["safety"]["packets_transmitted"] == 0
