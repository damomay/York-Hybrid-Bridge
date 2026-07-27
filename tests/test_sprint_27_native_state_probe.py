import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def _load_probe():
    spec = importlib.util.spec_from_file_location(
        "native_state_probe",
        ROOT / "york_capture_probe.py",
    )
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_native_comparison_matches_supported_fields():
    probe = _load_probe()
    result = probe._compare(
        {"power": True, "mode": "heat", "fan": "high"},
        {"power": True, "mode": "heat", "fan": "high"},
    )
    assert result["result"] == "MATCH"
    assert result["matches"] == 3


def test_native_comparison_records_mismatch():
    probe = _load_probe()
    result = probe._compare({"mode": "cool"}, {"mode": "heat"})
    assert result["result"] == "MISMATCH"
    assert result["mismatches"] == 1


def test_aggregate_confidence(tmp_path):
    probe = _load_probe()
    path = tmp_path / "native-qualification.json"
    first = probe._update_aggregate(path, {"result": "MATCH"})
    second = probe._update_aggregate(path, {"result": "MISMATCH"})
    assert first["confidence_percent"] == 100.0
    assert second["confidence_percent"] == 50.0
    assert json.loads(path.read_text(encoding="utf-8"))["probes"] == 2


def test_qualification_report_v2_is_packaged():
    text = (ROOT / "qualification_suite.py").read_text(encoding="utf-8")
    assert 'SUITE_VERSION = "2.1.0"' in text
    assert "Native Qualification" in text
    assert "Project Milestones" in text
