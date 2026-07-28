import hashlib
import json
from pathlib import Path

import pytest

from adapters.york.errors import YorkFrameError
from protocols.york.native_capture import (
    import_native_capture,
    import_relay_transactions,
)
from protocols.york.packet_library import load_packet_record


def _capture() -> dict:
    return {
        "schema_version": 1,
        "evidence_type": "native_york_controller_request",
        "timestamp_utc": "2026-07-28T08:00:00Z",
        "direction": "controller_to_device",
        "endpoint": {"transport": "udp", "host": "192.0.2.30", "port": 12345},
        "action": {
            "marker": "power-on cool 22",
            "purpose": "command_request",
            "requested_state": {"power": True, "mode": "cool", "temperature": 22},
        },
        "frame_hex": "BB 01 02 B8",
        "source": {
            "artifact": "York TFIAC Relay V2 debug build",
            "artifact_sha256": "a" * 64,
            "tool": "in-app pre-send capture",
            "hook_point": "native request bytes before socket send",
        },
    }


def test_import_preserves_provenance_and_forces_non_executable(tmp_path: Path):
    capture_path = tmp_path / "capture.json"
    capture_path.write_text(json.dumps(_capture()), encoding="utf-8")

    report = import_native_capture(capture_path, tmp_path / "evidence")
    record_path = Path(report["record_file"])
    raw = json.loads(record_path.read_text(encoding="utf-8"))
    loaded = load_packet_record(record_path)

    assert report["status"] == "IMPORTED_OBSERVED_NON_EXECUTABLE"
    assert report["packets_transmitted"] == 0
    assert report["network_sockets_opened"] == 0
    assert raw["direction"] == "controller_to_device"
    assert raw["observations"]["action_marker"] == "power-on cool 22"
    assert raw["observations"]["endpoint"] == {
        "transport": "udp",
        "host": "192.0.2.30",
        "port": 12345,
    }
    assert raw["observations"]["checksum_analysis"]["matches"] is True
    assert raw["source"]["capture_sha256"] == hashlib.sha256(
        capture_path.read_bytes()
    ).hexdigest()
    assert raw["verification"]["status"] == "observed"
    assert raw["verification"]["safe_to_transmit"] is False
    assert loaded.executable is False


def test_import_rejects_response_direction(tmp_path: Path):
    capture = _capture()
    capture["direction"] = "device_to_controller"
    path = tmp_path / "response.json"
    path.write_text(json.dumps(capture), encoding="utf-8")

    with pytest.raises(ValueError, match="controller_to_device"):
        import_native_capture(path, tmp_path / "evidence")


def test_import_rejects_missing_source_provenance(tmp_path: Path):
    capture = _capture()
    del capture["source"]["hook_point"]
    path = tmp_path / "missing-provenance.json"
    path.write_text(json.dumps(capture), encoding="utf-8")

    with pytest.raises(ValueError, match="hook_point"):
        import_native_capture(path, tmp_path / "evidence")


def test_import_rejects_non_york_frame(tmp_path: Path):
    capture = _capture()
    capture["frame_hex"] = "AA 01 02 B9"
    path = tmp_path / "not-york.json"
    path.write_text(json.dumps(capture), encoding="utf-8")

    with pytest.raises(YorkFrameError, match="0xBB"):
        import_native_capture(path, tmp_path / "evidence")


def _relay_export() -> dict:
    return {
        "count": 1,
        "transactions": [
            {
                "transaction_id": 1,
                "started_at": "2026-07-28 10:40:31.393",
                "requested": {"power": True, "mode": "cool"},
                "before": {"power": False},
                "target": {"power": True, "mode": "cool"},
                "after": {"power": True, "mode": "cool"},
                "generated_packet": (
                    "BB 00 01 03 19 01 00 44 03 09 02 00 00 00 00 00 "
                    "00 00 00 00 00 00 00 00 00 00 00 00 00 00 ED"
                ),
                "sdk_response": {"code": 0, "msg": "uart data send success"},
                "verification": {"success": True},
                "success": True,
            }
        ],
    }


def test_relay_export_import_preserves_sdk_boundary_and_verification(
    tmp_path: Path,
):
    export_path = tmp_path / "transactions.json"
    export_path.write_text(json.dumps(_relay_export()), encoding="utf-8")
    synthetic_mac = ":".join(["00", "11", "22", "33", "44", "55"])

    report = import_relay_transactions(
        export_path,
        tmp_path / "evidence",
        artifact="recovered-relay-source.zip",
        artifact_sha256="b" * 64,
        target_mac=synthetic_mac,
        source_timezone="Australia/Melbourne",
    )
    assert report["transaction_count"] == 1
    assert report["packets_transmitted"] == 0
    record_path = next(
        (tmp_path / "evidence" / "packet_library" / "observed").glob("*.json")
    )
    record = json.loads(record_path.read_text(encoding="utf-8"))
    assert record["frame_length"] == 31
    assert record["observations"]["timestamp_utc"].startswith(
        "2026-07-28T00:40:31.393"
    )
    assert record["observations"]["endpoint"] == {
        "transport": "broadlink_sdk_passthrough",
        "target_mac": synthetic_mac.replace(":", ""),
    }
    assert record["observations"]["checksum_analysis"]["matches"] is True
    relay = record["source"]["relay_transaction"]
    assert relay["transaction_id"] == 1
    assert relay["before"]["power"] is False
    assert relay["after"]["power"] is True
    assert relay["sdk_response"]["code"] == 0
    assert relay["verification"]["success"] is True
    assert record["verification"]["safe_to_transmit"] is False


def test_relay_export_rejects_unverified_transaction(tmp_path: Path):
    export = _relay_export()
    export["transactions"][0]["verification"]["success"] = False
    export_path = tmp_path / "transactions.json"
    export_path.write_text(json.dumps(export), encoding="utf-8")
    synthetic_mac = ":".join(["00", "11", "22", "33", "44", "55"])

    with pytest.raises(ValueError, match="not successfully verified"):
        import_relay_transactions(
            export_path,
            tmp_path / "evidence",
            artifact="recovered-relay-source.zip",
            artifact_sha256="b" * 64,
            target_mac=synthetic_mac,
            source_timezone="Australia/Melbourne",
        )


def test_phase1_preserves_relay_and_no_send_boundary():
    roadmap = Path("docs/roadmaps/tablet-removal.md").read_text(encoding="utf-8")
    phase = Path(
        "docs/tablet-removal/phase-1-native-command-discovery.md"
    ).read_text(encoding="utf-8")
    source = Path("protocols/york/native_capture.py").read_text(encoding="utf-8")

    assert "Android relay remains the default" in roadmap
    assert "No live native transmission is authorized" in phase
    assert "safe_to_transmit" in source
    assert "False" in source
    assert "socket.socket" not in source
