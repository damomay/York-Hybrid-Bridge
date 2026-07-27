from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REFERENCE = ROOT / "protocols" / "york"


def test_york_protocol_reference_structure_exists() -> None:
    required = [
        REFERENCE / "README.md",
        REFERENCE / "captures" / "README.md",
        REFERENCE / "packet_library" / "README.md",
        REFERENCE / "packet_library" / "template.json",
        REFERENCE / "schemas" / "packet-record.schema.json",
        REFERENCE / "documentation" / "observations.md",
        REFERENCE / "documentation" / "packet_format.md",
        REFERENCE / "documentation" / "state_mapping.md",
        REFERENCE / "documentation" / "checksum.md",
    ]
    assert all(path.is_file() for path in required)


def test_packet_template_is_non_executable_until_verified() -> None:
    record = json.loads((REFERENCE / "packet_library" / "template.json").read_text())
    assert record["frame_hex"] == ""
    assert record["verification"]["status"] == "unverified"
    assert record["verification"]["safe_to_transmit"] is False


def test_no_unverified_library_entry_contains_executable_frame() -> None:
    for path in (REFERENCE / "packet_library").glob("*.json"):
        if path.name == "template.json":
            continue
        record = json.loads(path.read_text())
        if record["frame_hex"]:
            assert record["verification"]["status"] == "verified"
            assert record["source"]["capture_file"]
