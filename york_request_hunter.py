"""Rank York controller-request candidates from existing evidence.

Safety: analysis only. This tool never verifies records, never writes to the
verified packet library, and never opens a network socket.
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from protocols.york.analysis import load_analysis_data, rank_request_candidates

VERSION = "1.0.0"


def _candidate_record(candidate: dict[str, Any], generated_at: str) -> dict[str, Any]:
    return {
        "schema_version": 1,
        "id": f"candidate-{candidate['record_id']}",
        "source_record_id": candidate["record_id"],
        "purpose": candidate["suggested_purpose"],
        "direction": candidate["suggested_direction"],
        "frame_hex": candidate["frame_hex"],
        "expected_state": {},
        "candidate_analysis": {
            "tool": "York Request Hunter",
            "tool_version": VERSION,
            "generated_at": generated_at,
            "score": candidate["score"],
            "confidence": candidate["confidence"],
            "reasons": candidate["reasons"],
            "evidence": candidate["evidence"],
        },
        "verification": {
            "status": "observed",
            "safe_to_transmit": False,
            "verified_by": "",
            "verified_at": "",
        },
        "notes": "Candidate only. Requires a complete controller-to-device capture and human verification before promotion.",
    }


def hunt(
    packet_library: Path,
    fixtures: Path,
    output_dir: Path,
    timeline: Path | None = None,
    classifier_report: Path | None = None,
    candidate_dir: Path | None = None,
    minimum_score: int = 60,
) -> dict[str, Any]:
    data = load_analysis_data(packet_library, fixtures, timeline, classifier_report)
    candidates, excluded = rank_request_candidates(data)
    eligible = [item for item in candidates if item.score >= minimum_score]
    generated_at = datetime.now(timezone.utc).isoformat()

    report: dict[str, Any] = {
        "tool": "York Request Hunter",
        "version": VERSION,
        "generated_at": generated_at,
        "safety": {
            "analysis_only": True,
            "records_verified": 0,
            "records_made_executable": 0,
            "packets_transmitted": 0,
            "network_sockets_opened": 0,
        },
        "inputs": data.source_paths,
        "summary": {
            "observed_records": len(data.records),
            "decoder_fixtures": len(data.fixtures),
            "timeline_events": len(data.timeline_events),
            "ranked_candidates": len(candidates),
            "eligible_candidates": len(eligible),
            "excluded_known_responses": len(excluded),
            "minimum_score": minimum_score,
            "result": "CANDIDATES_FOUND" if eligible else "NO_REQUEST_CANDIDATES",
        },
        "candidates": [item.as_dict() for item in candidates],
        "excluded_records": excluded,
        "conclusion": (
            "One or more candidates require capture-level confirmation before promotion."
            if eligible
            else "All imported York records are known state responses or lack sufficient controller-to-device evidence. A new full-duplex capture is required."
        ),
    }

    output_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    json_path = output_dir / f"york-request-hunter-{stamp}.json"
    md_path = output_dir / f"york-request-hunter-{stamp}.md"

    candidate_paths: list[str] = []
    if candidate_dir is not None:
        candidate_dir.mkdir(parents=True, exist_ok=True)
        for item in eligible:
            path = candidate_dir / f"candidate-{item.record_id}.json"
            path.write_text(json.dumps(_candidate_record(item.as_dict(), generated_at), indent=2) + "\n", encoding="utf-8")
            candidate_paths.append(str(path))
    report["candidate_files"] = candidate_paths

    report["report_paths"] = {"json": str(json_path), "markdown": str(md_path)}
    json_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

    lines = [
        "# York Request Hunter Report",
        "",
        f"Generated: {generated_at}",
        "",
        "## Safety",
        "",
        "- Analysis only: **Yes**",
        "- Records verified: **0**",
        "- Records made executable: **0**",
        "- Packets transmitted: **0**",
        "- Network sockets opened: **0**",
        "",
        "## Summary",
        "",
        f"- Observed records: **{len(data.records)}**",
        f"- Decoder fixtures: **{len(data.fixtures)}**",
        f"- Timeline events: **{len(data.timeline_events)}**",
        f"- Ranked candidates: **{len(candidates)}**",
        f"- Eligible candidates (score >= {minimum_score}): **{len(eligible)}**",
        f"- Excluded known responses: **{len(excluded)}**",
        f"- Result: **{report['summary']['result']}**",
        "",
        "## Candidate Ranking",
        "",
    ]
    if candidates:
        lines += [
            "| Rank | Record | Score | Confidence | Suggested direction | Suggested purpose |",
            "|---:|---|---:|---|---|---|",
        ]
        for index, item in enumerate(candidates, 1):
            lines.append(
                f"| {index} | {item.record_id} | {item.score}% | {item.confidence} | "
                f"{item.suggested_direction} | {item.suggested_purpose} |"
            )
    else:
        lines.append("No request candidates survived the response-exclusion rules.")

    lines += [
        "",
        "## Conclusion",
        "",
        report["conclusion"],
        "",
        "## Important",
        "",
        "This tool does not promote or verify any packet. Candidate files, when requested, remain `observed` and `safe_to_transmit: false`.",
    ]
    md_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return report


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Rank possible York controller-request records without transmitting or verifying them.")
    parser.add_argument("--packet-library", type=Path, default=Path("/app/protocols/york/packet_library/observed"))
    parser.add_argument("--fixtures", type=Path, default=Path("/app/protocols/york/qualification/decoder_fixtures.json"))
    parser.add_argument("--timeline", type=Path, default=None)
    parser.add_argument("--classifier-report", type=Path, default=None)
    parser.add_argument("--output-dir", type=Path, default=Path("/reports/request-hunter"))
    parser.add_argument("--candidate-dir", type=Path, default=None, help="Write non-executable candidate records for candidates meeting the score threshold.")
    parser.add_argument("--minimum-score", type=int, default=60)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    report = hunt(
        args.packet_library,
        args.fixtures,
        args.output_dir,
        args.timeline,
        args.classifier_report,
        args.candidate_dir,
        args.minimum_score,
    )
    summary = report["summary"]
    print(f"York Request Hunter {VERSION}")
    print(f"Observed records: {summary['observed_records']}")
    print(f"Decoder fixtures: {summary['decoder_fixtures']}")
    print(f"Timeline events: {summary['timeline_events']}")
    print(f"Ranked candidates: {summary['ranked_candidates']}")
    print(f"Eligible candidates: {summary['eligible_candidates']}")
    print(f"Excluded known responses: {summary['excluded_known_responses']}")
    print(f"Result: {summary['result']}")
    print(f"JSON report: {report['report_paths']['json']}")
    print(f"Markdown report: {report['report_paths']['markdown']}")
    print("Verified/executable records created: 0")
    return 0


if __name__ == "__main__":
    sys.exit(main())
