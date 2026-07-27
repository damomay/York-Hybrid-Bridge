from __future__ import annotations

import argparse
import hashlib
import json
import sys
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from adapters.york.decoder import YorkPacketDecoder


@dataclass
class Classification:
    record_id: str
    source_path: str
    frame_hex: str
    suggested_kind: str
    suggested_direction: str
    confidence: int
    fixture_id: str | None
    decoded_state: dict[str, Any] | None
    reasons: list[str]
    verification_status: str
    executable: bool
    evidence_trace: dict[str, Any]


def _normalise_hex(value: str) -> str:
    return " ".join(value.upper().split())


def _load_fixtures(path: Path) -> dict[str, dict[str, Any]]:
    raw = json.loads(path.read_text(encoding="utf-8"))
    fixtures: dict[str, dict[str, Any]] = {}
    for item in raw.get("fixtures", []):
        fixtures[_normalise_hex(str(item["frame_hex"]))] = item
    return fixtures


def _classify_record(path: Path, fixtures: dict[str, dict[str, Any]]) -> Classification:
    raw = json.loads(path.read_text(encoding="utf-8"))
    frame_hex = _normalise_hex(str(raw.get("frame_hex", "")))
    parts = frame_hex.split()
    reasons: list[str] = []
    kind = "unknown"
    direction = "unknown"
    confidence = 0
    fixture_id: str | None = None
    decoded_state: dict[str, Any] | None = None

    if len(parts) == 21 and parts[:4] == ["BB", "01", "00", "03"]:
        kind = "state_response"
        direction = "device_to_controller"
        confidence = 92
        reasons.append("Frame is 21 bytes and matches the observed York status header BB 01 00 03.")
        try:
            state = YorkPacketDecoder().decode_state(bytes.fromhex(frame_hex))
            decoded_state = asdict(state)
            confidence = 96
            reasons.append("Production York decoder accepted the frame and checksum.")
        except Exception as exc:
            reasons.append(f"Decoder rejected the frame: {type(exc).__name__}: {exc}")
            confidence = 70

    fixture = fixtures.get(frame_hex)
    if fixture:
        fixture_id = str(fixture.get("id"))
        kind = "state_response"
        direction = "device_to_controller"
        confidence = 99
        reasons.append(f"Exact match for qualified decoder fixture '{fixture_id}'.")

    verification = raw.get("verification") or {}
    status = str(verification.get("status", raw.get("status", "unverified"))).lower()
    source = raw.get("source") if isinstance(raw.get("source"), dict) else {}
    observations = raw.get("observations") if isinstance(raw.get("observations"), dict) else {}

    return Classification(
        record_id=str(raw.get("id", path.stem)),
        source_path=str(path),
        frame_hex=frame_hex,
        suggested_kind=kind,
        suggested_direction=direction,
        confidence=confidence,
        fixture_id=fixture_id,
        decoded_state=decoded_state,
        reasons=reasons or ["No recognised York response signature or decoder fixture match."],
        verification_status=status,
        executable=False,
        evidence_trace={
            "record_sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
            "capture_file": source.get("capture_file", ""),
            "capture_timestamp": source.get("capture_timestamp", ""),
            "source_evidence": source.get("evidence_files", []),
            "locations": observations.get("locations", []),
            "classification_is_inference": True,
        },
    )


def _write_classified_copy(source: Path, result: Classification, target_dir: Path) -> Path:
    raw = json.loads(source.read_text(encoding="utf-8"))
    raw["kind"] = result.suggested_kind
    raw["direction"] = result.suggested_direction
    raw["classification"] = {
        "tool": "York Packet Classifier",
        "classified_at": datetime.now(timezone.utc).isoformat(),
        "confidence": result.confidence,
        "fixture_id": result.fixture_id,
        "reasons": result.reasons,
        "safety": "classification_only_non_executable",
    }
    raw.setdefault("verification", {})["status"] = "observed"
    raw["verification"]["safe_to_transmit"] = False
    target_dir.mkdir(parents=True, exist_ok=True)
    output = target_dir / source.name
    output.write_text(json.dumps(raw, indent=2) + "\n", encoding="utf-8")
    return output


def classify(input_dir: Path, fixtures_path: Path, output_dir: Path, apply_dir: Path | None) -> dict[str, Any]:
    fixtures = _load_fixtures(fixtures_path)
    results: list[Classification] = []
    applied: list[str] = []

    for path in sorted(input_dir.rglob("*.json")):
        if path.name in {"template.json"}:
            continue
        result = _classify_record(path, fixtures)
        results.append(result)
        if apply_dir is not None:
            applied.append(str(_write_classified_copy(path, result, apply_dir)))

    classified = sum(item.suggested_kind != "unknown" for item in results)
    response_count = sum(item.suggested_kind == "state_response" for item in results)
    request_count = sum(item.suggested_kind == "state_request" for item in results)
    high_confidence = sum(item.confidence >= 90 for item in results)

    report = {
        "tool": "York Packet Classifier",
        "version": "1.0.0",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "safety": {
            "classification_only": True,
            "records_verified": 0,
            "records_made_executable": 0,
            "packets_transmitted": 0,
            "classification_is_verification": False,
        },
        "inputs": {
            "packet_library": str(input_dir),
            "decoder_fixtures": str(fixtures_path),
        },
        "summary": {
            "total_records": len(results),
            "classified_records": classified,
            "unknown_records": len(results) - classified,
            "state_responses": response_count,
            "state_requests": request_count,
            "high_confidence_records": high_confidence,
            "verified_state_requests": 0,
        },
        "results": [asdict(item) for item in results],
        "classified_copies": applied,
        "protocol_boundary": (
            "State-response classification does not identify a native request or command. "
            "Android relay JSON is separate from native York packet evidence. The Android "
            "application still constructs the native command, so tablet removal is not achieved."
        ),
    }

    output_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    json_path = output_dir / f"york-packet-classification-{stamp}.json"
    md_path = output_dir / f"york-packet-classification-{stamp}.md"
    json_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

    lines = [
        "# York Packet Classification Report",
        "",
        f"Generated: {report['generated_at']}",
        "",
        "## Safety",
        "",
        "- Classification only: **Yes**",
        "- Records verified: **0**",
        "- Records made executable: **0**",
        "- Packets transmitted: **0**",
        "- Classification promoted to verification: **No**",
        "",
        "## Summary",
        "",
        f"- Total records: **{len(results)}**",
        f"- Classified: **{classified}**",
        f"- Unknown: **{len(results) - classified}**",
        f"- State responses: **{response_count}**",
        f"- State requests: **{request_count}**",
        f"- High confidence: **{high_confidence}**",
        "",
        "| Record | Suggested kind | Direction | Confidence | Fixture |",
        "|---|---|---|---:|---|",
    ]
    for item in results:
        lines.append(
            f"| {item.record_id} | {item.suggested_kind} | {item.suggested_direction} | "
            f"{item.confidence}% | {item.fixture_id or ''} |"
        )
    lines += [
        "",
        "## Important",
        "",
        "This report does not identify or verify a controller-to-device state request. "
        "No record is made safe to transmit by this tool.",
        "",
        "Android relay JSON is not a native York packet. The Android application still constructs "
        "the native command; tablet removal is not achieved.",
    ]
    md_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    report["report_paths"] = {"json": str(json_path), "markdown": str(md_path)}
    return report


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Classify observed York packet records without verifying or transmitting them.")
    parser.add_argument(
        "--packet-library",
        type=Path,
        default=Path("/app/protocols/york/packet_library/observed"),
    )
    parser.add_argument(
        "--fixtures",
        type=Path,
        default=Path("/app/protocols/york/qualification/decoder_fixtures.json"),
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("/reports/classification"),
    )
    parser.add_argument(
        "--apply-dir",
        type=Path,
        default=None,
        help="Write classified observed copies here. Verification remains observed and safe_to_transmit remains false.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    report = classify(args.packet_library, args.fixtures, args.output_dir, args.apply_dir)
    summary = report["summary"]
    print("York Packet Classifier 1.0.0")
    print(f"Records: {summary['total_records']}")
    print(f"Classified: {summary['classified_records']}")
    print(f"State responses: {summary['state_responses']}")
    print(f"State requests: {summary['state_requests']}")
    print(f"Unknown: {summary['unknown_records']}")
    print("Verified/executable records created: 0")
    print(f"JSON report: {report['report_paths']['json']}")
    print(f"Markdown report: {report['report_paths']['markdown']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
