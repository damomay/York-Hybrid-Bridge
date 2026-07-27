"""Load York protocol evidence without modifying it."""
from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class YorkAnalysisData:
    records: list[dict[str, Any]]
    fixtures: list[dict[str, Any]]
    timeline_events: list[dict[str, Any]]
    classifier_results: dict[str, dict[str, Any]]
    source_paths: dict[str, str]


def _load_json(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"Unable to load JSON evidence {path}: {exc}") from exc


def _latest_json(directory: Path, prefix: str) -> Path | None:
    if not directory.exists():
        return None
    matches = sorted(directory.glob(f"{prefix}*.json"), key=lambda p: p.stat().st_mtime)
    return matches[-1] if matches else None


def load_analysis_data(
    packet_library: Path,
    fixtures_path: Path,
    timeline_path: Path | None = None,
    classifier_report: Path | None = None,
) -> YorkAnalysisData:
    records: list[dict[str, Any]] = []
    if packet_library.exists():
        for path in sorted(packet_library.rglob("*.json")):
            if path.name == "template.json":
                continue
            raw = _load_json(path, {})
            if isinstance(raw, dict):
                raw = dict(raw)
                raw["_source_path"] = str(path)
                records.append(raw)

    fixtures_raw = _load_json(fixtures_path, {})
    fixtures = fixtures_raw.get("fixtures", []) if isinstance(fixtures_raw, dict) else []

    if timeline_path is None:
        timeline_path = _latest_json(packet_library.parent.parent / "timelines", "import-")
    timeline_raw = _load_json(timeline_path, []) if timeline_path else []
    timeline_events = timeline_raw if isinstance(timeline_raw, list) else []

    if classifier_report is None:
        classifier_report = _latest_json(Path("/reports/classification"), "york-packet-classification-")
    classifier_raw = _load_json(classifier_report, {}) if classifier_report else {}
    classifier_results: dict[str, dict[str, Any]] = {}
    if isinstance(classifier_raw, dict):
        for item in classifier_raw.get("results", []):
            if isinstance(item, dict) and item.get("record_id"):
                classifier_results[str(item["record_id"])] = item

    return YorkAnalysisData(
        records=records,
        fixtures=[item for item in fixtures if isinstance(item, dict)],
        timeline_events=[item for item in timeline_events if isinstance(item, dict)],
        classifier_results=classifier_results,
        source_paths={
            "packet_library": str(packet_library),
            "fixtures": str(fixtures_path),
            "timeline": str(timeline_path) if timeline_path else "",
            "classifier_report": str(classifier_report) if classifier_report else "",
        },
    )
