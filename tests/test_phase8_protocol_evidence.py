from __future__ import annotations

import json
from pathlib import Path

from protocols.york.capture_importer import import_captures
from york_decoder_qualification import DEFAULT_FIXTURES, run_qualification
from york_packet_classifier import classify
from york_request_hunter import hunt


ROOT = Path(__file__).resolve().parents[1]
APPROVED_EXCERPT = (
    ROOT / "protocols/york/qualification/approved_modes_excerpt.txt"
)


def test_approved_fixture_pipeline_is_traceable_and_deterministic(tmp_path: Path):
    first_root = tmp_path / "first"
    second_root = tmp_path / "second"

    first = import_captures([APPROVED_EXCERPT], first_root)
    second = import_captures([APPROVED_EXCERPT], second_root)

    assert first["unique_frame_count"] == second["unique_frame_count"] == 3
    assert first["source_evidence"] == second["source_evidence"]
    first_records = sorted(
        (
            json.loads(path.read_text())
            for path in (first_root / "packet_library/observed").glob("*.json")
        ),
        key=lambda record: record["id"],
    )
    second_records = sorted(
        (
            json.loads(path.read_text())
            for path in (second_root / "packet_library/observed").glob("*.json")
        ),
        key=lambda record: record["id"],
    )
    assert first_records == second_records
    assert all(record["verification"]["status"] == "observed" for record in first_records)
    assert all(record["source"]["evidence_files"] for record in first_records)
    assert all(
        location["timestamp"]
        for record in first_records
        for location in record["observations"]["locations"]
    )


def test_approved_fixture_conclusions_remain_response_only_and_no_send(tmp_path: Path):
    protocol_root = tmp_path / "protocol"
    import_captures([APPROVED_EXCERPT], protocol_root)
    observed = protocol_root / "packet_library/observed"

    classification = classify(
        observed,
        DEFAULT_FIXTURES,
        tmp_path / "classification",
        tmp_path / "classified",
    )
    hunter = hunt(
        observed,
        DEFAULT_FIXTURES,
        tmp_path / "hunter",
        classifier_report=Path(classification["report_paths"]["json"]),
    )
    qualification = run_qualification(DEFAULT_FIXTURES)

    assert qualification["summary"]["result"] == "PASS"
    assert classification["summary"]["state_responses"] == 3
    assert classification["summary"]["state_requests"] == 0
    assert classification["safety"]["records_made_executable"] == 0
    assert hunter["summary"]["eligible_candidates"] == 0
    assert hunter["summary"]["excluded_known_responses"] == 3
    assert hunter["safety"]["packets_transmitted"] == 0
    assert "tablet removal is not achieved" in hunter["conclusion"]
