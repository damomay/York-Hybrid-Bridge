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
from adapters.york.errors import YorkFrameError
from version import APP_VERSION

ROOT = Path(__file__).resolve().parent
DEFAULT_FIXTURES = ROOT / "protocols/york/qualification/decoder_fixtures.json"
DEFAULT_OUTPUT = ROOT / "qualification-reports"


@dataclass(frozen=True)
class FixtureResult:
    fixture_id: str
    status: str
    expected: dict[str, Any]
    actual: dict[str, Any] | None
    differences: dict[str, dict[str, Any]]
    error: str | None = None


def _bytes_from_hex(value: str) -> bytes:
    try:
        return bytes.fromhex(value)
    except ValueError as exc:
        raise ValueError(f"invalid frame_hex: {exc}") from exc


def compare(expected: dict[str, Any], actual: dict[str, Any]) -> dict[str, dict[str, Any]]:
    differences: dict[str, dict[str, Any]] = {}
    for key, expected_value in expected.items():
        actual_value = actual.get(key)
        if actual_value != expected_value:
            differences[key] = {"expected": expected_value, "actual": actual_value}
    return differences


def run_qualification(fixtures_path: Path = DEFAULT_FIXTURES) -> dict[str, Any]:
    payload = json.loads(fixtures_path.read_text(encoding="utf-8"))
    fixtures = payload.get("fixtures")
    if not isinstance(fixtures, list) or not fixtures:
        raise ValueError("qualification fixture file contains no fixtures")

    decoder = YorkPacketDecoder()
    results: list[FixtureResult] = []
    for fixture in fixtures:
        fixture_id = str(fixture.get("id", "unnamed"))
        expected = fixture.get("expected")
        if not isinstance(expected, dict):
            results.append(FixtureResult(fixture_id, "FAIL", {}, None, {}, "missing expected state"))
            continue
        try:
            state = decoder.decode_state(_bytes_from_hex(str(fixture.get("frame_hex", ""))))
            actual = state.to_dict()
            differences = compare(expected, actual)
            results.append(
                FixtureResult(
                    fixture_id=fixture_id,
                    status="PASS" if not differences else "FAIL",
                    expected=expected,
                    actual=actual,
                    differences=differences,
                )
            )
        except (ValueError, YorkFrameError) as exc:
            results.append(FixtureResult(fixture_id, "FAIL", expected, None, {}, str(exc)))

    passed = sum(item.status == "PASS" for item in results)
    total = len(results)
    return {
        "report_type": "york_decoder_qualification",
        "climate_bridge_version": APP_VERSION,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "fixture_source": str(fixtures_path),
        "fixture_sha256": hashlib.sha256(fixtures_path.read_bytes()).hexdigest(),
        "safety": payload.get("safety", "offline_decoder_only"),
        "summary": {
            "passed": passed,
            "failed": total - passed,
            "total": total,
            "confidence_percent": round((passed / total) * 100, 2) if total else 0.0,
            "result": "PASS" if passed == total else "FAIL",
        },
        "results": [asdict(item) for item in results],
        "unresolved_fields": ["temperature", "current_temperature", "sleep", "timer", "clock"],
        "protocol_boundary": (
            "Fixtures are observed device state responses used for offline decoder validation. "
            "They are not controller-to-device command candidates. Android relay JSON is not a "
            "native York packet, and tablet removal is not achieved."
        ),
    }


def write_report(report: dict[str, Any], output_dir: Path) -> tuple[Path, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    json_path = output_dir / f"york-decoder-qualification-{stamp}.json"
    md_path = output_dir / f"york-decoder-qualification-{stamp}.md"
    json_path.write_text(json.dumps(report, indent=2), encoding="utf-8")

    summary = report["summary"]
    lines = [
        "# York Decoder Qualification Report",
        "",
        f"- Climate Bridge: `{report['climate_bridge_version']}`",
        f"- Generated: `{report['generated_at']}`",
        f"- Result: **{summary['result']}**",
        f"- Fixtures: **{summary['passed']}/{summary['total']} passed**",
        f"- Evidence confidence: **{summary['confidence_percent']}%**",
        "- Safety: offline decoder validation only; no packets transmitted",
        f"- Fixture SHA-256: `{report['fixture_sha256']}`",
        "",
        "| Fixture | Result | Differences / error |",
        "|---|---:|---|",
    ]
    for item in report["results"]:
        detail = item.get("error") or json.dumps(item.get("differences", {}), sort_keys=True)
        lines.append(f"| {item['fixture_id']} | {item['status']} | `{detail}` |")
    lines.extend([
        "",
        "## Unresolved fields",
        "",
        ", ".join(report["unresolved_fields"]),
        "",
        "## Protocol boundary",
        "",
        report["protocol_boundary"],
        "",
    ])
    md_path.write_text("\n".join(lines), encoding="utf-8")
    return json_path, md_path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Qualify the York state decoder against recovered Protocol Explorer fixtures.")
    parser.add_argument("--fixtures", type=Path, default=DEFAULT_FIXTURES)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--no-write", action="store_true", help="Run checks without creating report files")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    report = run_qualification(args.fixtures)
    summary = report["summary"]
    print(f"York decoder qualification: {summary['result']} ({summary['passed']}/{summary['total']})")
    for item in report["results"]:
        suffix = item.get("error") or (json.dumps(item["differences"], sort_keys=True) if item["differences"] else "")
        print(f"[{item['status']}] {item['fixture_id']} {suffix}".rstrip())
    if not args.no_write:
        json_path, md_path = write_report(report, args.output_dir)
        print(f"JSON report: {json_path}")
        print(f"Markdown report: {md_path}")
    return 0 if summary["result"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
