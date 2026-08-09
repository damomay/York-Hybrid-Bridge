from importlib import import_module
import json
from pathlib import Path
import socket
import sys

from adapters.york.decoder import YorkPacketDecoder
from protocols.york.capture_importer import import_captures
from york_packet_classifier import classify


RESEARCH_MODULES = (
    "protocols.york.capture_importer",
    "protocols.york.lab_dashboard",
    "protocols.york.packet_library",
    "protocols.york.xml_broadcast",
    "qualification_suite",
    "york_capture_importer",
    "york_decoder_qualification",
    "york_packet_classifier",
    "york_protocol_lab",
)


def test_importing_research_modules_has_no_io_side_effects(monkeypatch):
    def reject_network(*args, **kwargs):
        raise AssertionError("research-module import attempted network access")

    def reject_write(*args, **kwargs):
        raise AssertionError("research-module import attempted a file write")

    monkeypatch.setattr(socket, "create_connection", reject_network)
    monkeypatch.setattr(Path, "write_text", reject_write)
    for name in RESEARCH_MODULES:
        sys.modules.pop(name, None)
        import_module(name)


def test_approved_fixture_is_deterministic_across_repeat_runs(tmp_path: Path):
    capture = tmp_path / "approved-fixture.log"
    capture.write_text(
        "MARK: observed cool state\n"
        "RX BB 01 00 03 0F 01 00 31 06 00 00 00 00 00 00 00 00 5F 00 00 DF\n",
        encoding="utf-8",
    )
    first_root = tmp_path / "first" / "protocols" / "york"
    second_root = tmp_path / "second" / "protocols" / "york"
    first = import_captures([capture], first_root)
    second = import_captures([capture], second_root)

    first_record = json.loads(
        next((first_root / "packet_library" / "observed").glob("*.json"))
        .read_text(encoding="utf-8")
    )
    second_record = json.loads(
        next((second_root / "packet_library" / "observed").glob("*.json"))
        .read_text(encoding="utf-8")
    )
    assert first["unique_frame_count"] == second["unique_frame_count"] == 1
    assert first_record["id"] == second_record["id"]
    assert first_record["frame_hex"] == second_record["frame_hex"]
    assert first_record["verification"] == second_record["verification"]

    fixtures = (
        Path(__file__).parents[1]
        / "protocols/york/qualification/decoder_fixtures.json"
    )
    first_classification = classify(
        first_root / "packet_library" / "observed",
        fixtures,
        tmp_path / "first-reports",
        tmp_path / "first-classified",
    )
    second_classification = classify(
        second_root / "packet_library" / "observed",
        fixtures,
        tmp_path / "second-reports",
        tmp_path / "second-classified",
    )
    assert first_classification["summary"] == second_classification["summary"]

    frame = bytes.fromhex(first_record["frame_hex"])
    assert YorkPacketDecoder().decode_state(frame).to_dict() == (
        YorkPacketDecoder().decode_state(frame).to_dict()
    )


def test_normal_bridge_startup_does_not_import_research_tools():
    source = (Path(__file__).parents[1] / "bridge.py").read_text(encoding="utf-8")
    for name in RESEARCH_MODULES:
        assert name not in source
