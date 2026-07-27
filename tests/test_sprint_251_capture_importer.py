import json
from pathlib import Path

from protocols.york.capture_importer import import_captures, parse_capture


def test_extracts_marks_directions_and_deduplicates(tmp_path: Path):
    source = tmp_path / "explorer.log"
    source.write_text(
        "2026-01-01 10:00:00 MARK: power on\n"
        "2026-01-01 10:00:01 TX BB 00 01 04 02 01 00 BD\n"
        "2026-01-01 10:00:02 TX BB 00 01 04 02 01 00 BD\n"
        "2026-01-01 10:00:03 RX BB 01 00 03 10 20 30\n",
        encoding="utf-8",
    )
    frames, quarantine, timeline = parse_capture(source)
    assert len(frames) == 2
    assert not quarantine
    request = next(frame for frame in frames if frame.frame[1] == 0)
    assert len(request.occurrences) == 2
    assert request.occurrences[0].mark == "power on"
    assert request.occurrences[0].direction == "controller_to_device"
    assert any(event["event"] == "mark" for event in timeline)


def test_import_writes_observed_non_executable_records(tmp_path: Path):
    source = tmp_path / "capture.txt"
    source.write_text("RX BB 01 00 03 10 20 30\n", encoding="utf-8")
    root = tmp_path / "protocols" / "york"
    report = import_captures([source], root)
    records = list((root / "packet_library" / "observed").glob("*.json"))
    assert report["unique_frame_count"] == 1
    assert len(records) == 1
    data = json.loads(records[0].read_text(encoding="utf-8"))
    assert data["verification"]["status"] == "observed"
    assert data["direction"] == "device_to_controller"
    assert data["kind"] == "unknown"


def test_short_bb_candidate_is_quarantined(tmp_path: Path):
    source = tmp_path / "bad.log"
    source.write_text("RX BB 01\n", encoding="utf-8")
    frames, quarantine, _ = parse_capture(source)
    assert not frames
    assert quarantine[0]["reason"].startswith("frame too short")
