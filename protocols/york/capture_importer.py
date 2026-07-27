"""Evidence-preserving importer for York Protocol Explorer text captures."""
from __future__ import annotations

import hashlib
import json
import re
import shutil
import zipfile
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

from .lab_dashboard import generate_dashboard

HEX_TOKEN = re.compile(r"(?i)\b[0-9a-f]{2}\b")
BB_START = re.compile(r"(?i)\bbb\b")
TIMESTAMP_PATTERNS = (
    re.compile(r"(?P<ts>\d{4}-\d{2}-\d{2}[ T]\d{2}:\d{2}:\d{2}(?:[.,]\d{1,6})?(?:Z|[+-]\d{2}:?\d{2})?)"),
    re.compile(r"(?P<ts>\d{2}/\d{2}/\d{4}[ T]\d{2}:\d{2}:\d{2}(?:[.,]\d{1,6})?)"),
    re.compile(r"(?P<ts>\d{2}:\d{2}:\d{2}(?:[.,]\d{1,6})?)"),
)
MARK_RE = re.compile(r"(?i)\bMARK\s*[:=-]\s*(?P<mark>.+)$")


@dataclass
class Occurrence:
    source_file: str
    line_number: int
    raw_line: str
    timestamp: str = ""
    mark: str = ""
    direction: str = "unknown"


@dataclass
class ImportedFrame:
    frame: bytes
    occurrences: list[Occurrence] = field(default_factory=list)

    @property
    def digest(self) -> str:
        return hashlib.sha256(self.frame).hexdigest()

    @property
    def record_id(self) -> str:
        return f"yrk-observed-{self.digest[:12]}"

    @property
    def frame_hex(self) -> str:
        return self.frame.hex(" ").upper()


def _timestamp(line: str) -> str:
    for pattern in TIMESTAMP_PATTERNS:
        match = pattern.search(line)
        if match:
            return match.group("ts").replace(",", ".")
    return ""


def _direction(line: str) -> str:
    value = line.lower()
    controller_tokens = ("controller_to_device", "controller -> device", "tx", "send", "request", "outbound", "c2d")
    device_tokens = ("device_to_controller", "device -> controller", "rx", "recv", "receive", "response", "inbound", "d2c")
    if any(re.search(rf"(?<![a-z0-9_]){re.escape(token)}(?![a-z0-9_])", value) for token in controller_tokens):
        return "controller_to_device"
    if any(re.search(rf"(?<![a-z0-9_]){re.escape(token)}(?![a-z0-9_])", value) for token in device_tokens):
        return "device_to_controller"
    return "unknown"


def _extract_frame(line: str) -> tuple[bytes | None, str | None]:
    start = BB_START.search(line)
    if not start:
        return None, None
    tail = line[start.start():]
    tokens = HEX_TOKEN.findall(tail)
    if not tokens or tokens[0].upper() != "BB":
        return None, "candidate did not begin with BB"
    try:
        frame = bytes.fromhex("".join(tokens))
    except ValueError as exc:
        return None, f"invalid hex: {exc}"
    if len(frame) < 4:
        return None, f"frame too short ({len(frame)} bytes)"
    return frame, None



def _read_capture_text(path: Path) -> str:
    """Read plain text captures and Word .docx files without external dependencies."""
    if path.suffix.lower() != ".docx":
        return path.read_text(encoding="utf-8", errors="replace")
    try:
        with zipfile.ZipFile(path) as archive:
            document = archive.read("word/document.xml")
    except (OSError, KeyError, zipfile.BadZipFile) as exc:
        raise ValueError(f"Unable to read DOCX capture {path.name}: {exc}") from exc
    root = ET.fromstring(document)
    namespace = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
    lines: list[str] = []
    for paragraph in root.iter(namespace + "p"):
        parts = [node.text or "" for node in paragraph.iter(namespace + "t")]
        lines.append("".join(parts))
    return "\n".join(lines)



def _redact_capture_text(text: str) -> str:
    """Redact reusable credentials while retaining protocol evidence."""
    patterns = (
        (re.compile(r'(?i)("(?:license|type_license|key)"\s*:\s*")[^"]*(")'), r'\1<redacted>\2'),
        (re.compile(r'(?i)("password"\s*:\s*)\d+'), r'\1<redacted>'),
    )
    for pattern, replacement in patterns:
        text = pattern.sub(replacement, text)
    return text


def _copy_capture(source: Path, target: Path, raw: bool) -> None:
    if raw:
        shutil.copy2(source, target)
        return
    text = _read_capture_text(source)
    target = target.with_suffix(".txt")
    target.write_text(_redact_capture_text(text), encoding="utf-8")

def parse_capture(path: Path) -> tuple[list[ImportedFrame], list[dict], list[dict]]:
    """Parse one text capture, returning frames, quarantine records and timeline events."""
    text = _read_capture_text(path)
    frames: dict[str, ImportedFrame] = {}
    quarantine: list[dict] = []
    timeline: list[dict] = []
    active_mark = ""

    for line_number, raw_line in enumerate(text.splitlines(), 1):
        mark_match = MARK_RE.search(raw_line)
        if mark_match:
            active_mark = mark_match.group("mark").strip()
            timeline.append({
                "event": "mark",
                "source_file": path.name,
                "line_number": line_number,
                "timestamp": _timestamp(raw_line),
                "mark": active_mark,
            })

        frame, error = _extract_frame(raw_line)
        if error:
            quarantine.append({
                "source_file": path.name,
                "line_number": line_number,
                "raw_line": raw_line,
                "reason": error,
            })
            continue
        if frame is None:
            continue

        occurrence = Occurrence(
            source_file=path.name,
            line_number=line_number,
            raw_line=raw_line,
            timestamp=_timestamp(raw_line),
            mark=active_mark,
            direction=_direction(raw_line),
        )
        key = hashlib.sha256(frame).hexdigest()
        frames.setdefault(key, ImportedFrame(frame=frame)).occurrences.append(occurrence)
        timeline.append({
            "event": "frame",
            "source_file": path.name,
            "line_number": line_number,
            "timestamp": occurrence.timestamp,
            "mark": active_mark,
            "direction": occurrence.direction,
            "frame_id": f"yrk-observed-{key[:12]}",
            "frame_hex": frame.hex(" ").upper(),
        })

    return list(frames.values()), quarantine, timeline


def _merge_frames(frame_groups: Iterable[Iterable[ImportedFrame]]) -> list[ImportedFrame]:
    merged: dict[str, ImportedFrame] = {}
    for group in frame_groups:
        for item in group:
            merged.setdefault(item.digest, ImportedFrame(frame=item.frame)).occurrences.extend(item.occurrences)
    return sorted(merged.values(), key=lambda item: item.record_id)


def _consensus(values: Iterable[str], fallback: str = "unknown") -> str:
    nonempty = [value for value in values if value and value != "unknown"]
    return nonempty[0] if nonempty and len(set(nonempty)) == 1 else fallback


def _record(frame: ImportedFrame) -> dict:
    occurrences = frame.occurrences
    direction = _consensus(item.direction for item in occurrences)
    marks = sorted({item.mark for item in occurrences if item.mark})
    first = occurrences[0]
    last = occurrences[-1]
    return {
        "id": frame.record_id,
        "protocol": "york_tfiac_20014",
        "kind": "unknown",
        "direction": direction,
        "frame_hex": frame.frame_hex,
        "frame_length": len(frame.frame),
        "expected_state": {},
        "observations": {
            "occurrence_count": len(occurrences),
            "first_seen": first.timestamp,
            "last_seen": last.timestamp,
            "marks": marks,
            "locations": [
                {
                    "capture_file": item.source_file,
                    "line_number": item.line_number,
                    "timestamp": item.timestamp,
                    "direction": item.direction,
                    "mark": item.mark,
                }
                for item in occurrences
            ],
        },
        "source": {
            "capture_file": first.source_file,
            "capture_timestamp": first.timestamp,
            "tool": "York Capture Importer",
            "notes": "Automatically imported as observed evidence; human verification required.",
        },
        "verification": {
            "status": "observed",
            "verified_by": "",
            "verified_at": "",
            "replay_count": 0,
            "successful_responses": 0,
        },
    }


def discover_inputs(inputs: Iterable[Path]) -> list[Path]:
    discovered: list[Path] = []
    for item in inputs:
        if item.is_dir():
            discovered.extend(path for path in item.rglob("*") if path.is_file() and path.suffix.lower() in {".txt", ".log", ".docx"})
        elif item.is_file():
            discovered.append(item)
        else:
            raise FileNotFoundError(f"Capture input does not exist: {item}")
    return sorted(set(path.resolve() for path in discovered))


def import_captures(inputs: Iterable[Path], protocol_root: Path, copy_sources: bool = True, copy_raw_sources: bool = False) -> dict:
    files = discover_inputs(inputs)
    if not files:
        raise ValueError("No .txt, .log or .docx capture files were found")

    captures_dir = protocol_root / "captures" / "imported"
    library_dir = protocol_root / "packet_library" / "observed"
    reports_dir = protocol_root / "reports"
    timelines_dir = protocol_root / "timelines"
    quarantine_dir = protocol_root / "captures" / "quarantine"
    statistics_dir = protocol_root / "statistics"
    qualification_dir = protocol_root / "qualification-reports"
    for directory in (captures_dir, library_dir, reports_dir, timelines_dir, quarantine_dir, statistics_dir, qualification_dir):
        directory.mkdir(parents=True, exist_ok=True)

    parsed = []
    all_quarantine: list[dict] = []
    all_timeline: list[dict] = []
    for source in files:
        frames, quarantine, timeline = parse_capture(source)
        parsed.append(frames)
        all_quarantine.extend(quarantine)
        all_timeline.extend(timeline)
        if copy_sources:
            suffix = source.suffix if copy_raw_sources else ".txt"
            target = captures_dir / f"{source.stem}{suffix}"
            if target.exists():
                target = captures_dir / f"{source.stem}-{hashlib.sha256(source.read_bytes()).hexdigest()[:8]}{suffix}"
            _copy_capture(source, target, raw=copy_raw_sources)

    merged = _merge_frames(parsed)
    for frame in merged:
        (library_dir / f"{frame.record_id}.json").write_text(
            json.dumps(_record(frame), indent=2) + "\n", encoding="utf-8"
        )

    run_id = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    timeline_path = timelines_dir / f"import-{run_id}.json"
    timeline_path.write_text(json.dumps(all_timeline, indent=2) + "\n", encoding="utf-8")

    quarantine_path = quarantine_dir / f"import-{run_id}.json"
    quarantine_path.write_text(json.dumps(all_quarantine, indent=2) + "\n", encoding="utf-8")

    direction_counts: dict[str, int] = {}
    for frame in merged:
        direction = _consensus(item.direction for item in frame.occurrences)
        direction_counts[direction] = direction_counts.get(direction, 0) + 1

    report = {
        "import_id": run_id,
        "status": "completed",
        "source_files": [str(path) for path in files],
        "source_file_count": len(files),
        "unique_frame_count": len(merged),
        "total_frame_occurrences": sum(len(frame.occurrences) for frame in merged),
        "quarantined_candidate_count": len(all_quarantine),
        "direction_counts": direction_counts,
        "outputs": {
            "packet_library": str(library_dir),
            "timeline": str(timeline_path),
            "quarantine": str(quarantine_path),
        },
        "safety": "All imported packet records are observed and non-executable. Copied source logs are redacted unless raw copying is explicitly enabled.",
    }
    report_path = reports_dir / f"import-{run_id}.json"
    report_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    (statistics_dir / "latest_import.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    dashboard = generate_dashboard(protocol_root)
    report["outputs"]["dashboard"] = dashboard["dashboard"]
    report["report_file"] = str(report_path)
    return report
