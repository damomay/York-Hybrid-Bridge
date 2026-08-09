#!/usr/bin/env python3
"""Guarded one-shot qualification of York's Horizontal axis in Dry mode."""
from __future__ import annotations

import argparse
import hashlib
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from adapters.york import (
    BroadlinkYorkOneShotWriteClient,
    YORK_QUALIFICATION_DRY_LOW_BOTH_21,
    YORK_QUALIFICATION_DRY_LOW_VERTICAL_21,
    YorkPacketDecoder,
)
from adapters.york.broadlink import york_xor
from configuration import load_config
from version import APP_VERSION


@dataclass(frozen=True)
class SwingCase:
    name: str
    before_swing: str
    target_swing: str
    command: bytes
    confirmation_token: str
    evidence: str
    expected_sha256: str

    @property
    def before(self) -> dict[str, Any]:
        return _state(self.before_swing)

    @property
    def after(self) -> dict[str, Any]:
        return _state(self.target_swing)


def _state(swing: str) -> dict[str, Any]:
    return {
        "power": True,
        "mode": "dry",
        "temperature": 21.0,
        "fan": "low",
        "swing": swing,
        "turbo": False,
        "eco": False,
        "health": False,
        "display": True,
    }


CASES = {
    "vertical-to-both": SwingCase(
        name="vertical-to-both",
        before_swing="vertical",
        target_swing="both",
        command=YORK_QUALIFICATION_DRY_LOW_BOTH_21,
        confirmation_token="ENABLE-HORIZONTAL-AXIS-WITH-VERTICAL-DRY-21-ONCE",
        evidence=(
            "Relay v2 transaction physically changed Dry/21/Low from "
            "Vertical to Both: both axes moved. The exact command preserves "
            "Vertical while adding the command-side Horizontal flag 0x08"
        ),
        expected_sha256=(
            "3f5a886d4a3d41217c612a6e5a703425b85462cc9b5a1bcc78e7f4b26a40860b"
        ),
    ),
    "both-to-vertical": SwingCase(
        name="both-to-vertical",
        before_swing="both",
        target_swing="vertical",
        command=YORK_QUALIFICATION_DRY_LOW_VERTICAL_21,
        confirmation_token="DISABLE-HORIZONTAL-AXIS-KEEP-VERTICAL-DRY-21-ONCE",
        evidence=(
            "Relay v2 transaction physically changed Dry/21/Low from Both "
            "to Vertical: Horizontal stopped while Vertical continued. The "
            "exact command removes only the Horizontal 0x08 flag"
        ),
        expected_sha256=(
            "fffdf3843b37781ccec47fca45a25322600b54c37b0b03a56bd5afbf1f3a5d49"
        ),
    ),
}


class QualificationSafeStop(RuntimeError):
    """Stop before a write when the live state is not exactly qualified."""


def _compare(expected: dict[str, Any], observed: dict[str, Any]) -> dict[str, Any]:
    fields = {
        key: {
            "expected": expected_value,
            "observed": observed.get(key),
            "match": observed.get(key) == expected_value,
        }
        for key, expected_value in expected.items()
    }
    matches = sum(int(item["match"]) for item in fields.values())
    return {
        "fields": fields,
        "matches": matches,
        "compared": len(fields),
        "result": "MATCH" if matches == len(fields) else "MISMATCH",
    }


def _validate_case(case: SwingCase) -> None:
    if len(case.command) != 31:
        raise SystemExit(f"SAFE STOP: {case.name} command is not 31 bytes")
    if york_xor(case.command):
        raise SystemExit(f"SAFE STOP: {case.name} York checksum is invalid")
    if hashlib.sha256(case.command).hexdigest() != case.expected_sha256:
        raise SystemExit(f"SAFE STOP: {case.name} command fingerprint is invalid")


def _label(state: dict[str, Any]) -> str:
    return (
        f"On / Dry / {state['temperature']:.1f} °C / Fan Low / "
        f"Swing {str(state['swing']).title()}"
    )


def _write_report(
    output_dir: Path,
    case: SwingCase,
    payload: dict[str, Any],
) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    path = output_dir / f"alpha51-dry-horizontal-axis-{case.name}-{stamp}.json"
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return path


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Validate Alpha.51 Dry-mode Horizontal-axis frames offline or execute "
            "one explicitly confirmed guarded case once."
        )
    )
    parser.add_argument("config", nargs="?", default="/config/config.yml")
    parser.add_argument("--case", choices=tuple(CASES))
    parser.add_argument("--execute", action="store_true")
    parser.add_argument("--confirm", default="")
    parser.add_argument("--output-dir", default="/reports/direct-write")
    parser.add_argument("--post-write-delay", type=float, default=2.0)
    args = parser.parse_args()

    print(f"Climate Bridge {APP_VERSION} — Dry-Mode Horizontal Axis Qualification")
    for case in CASES.values():
        _validate_case(case)
        print(f"{case.name}:")
        print(f"  Required: {_label(case.before)}")
        print(f"  Target:   {_label(case.after)}")
        print(f"  Command:  {case.command.hex(' ').upper()}")
        print(f"  SHA-256:  {case.expected_sha256}")
        print(f"  Evidence: {case.evidence}")
        print(f"  Confirmation token: {case.confirmation_token}")
    print("Automatic retries: 0")
    print("Automatic restore: disabled")
    print("Normal Home Assistant Horizontal/Both routing: Relay v2")
    print("Alpha.50 Heat qualification tool: not executable in this container")
    print("Rejected Alpha.49 0x20 status-bit candidate: excluded")

    if not args.execute:
        print("VALIDATION PASSED — no socket opened and no packet transmitted.")
        print("Execution requires --case plus that case's exact token.")
        return 0
    if args.case is None:
        raise SystemExit("SAFE STOP: --case is required; no socket opened")
    case = CASES[args.case]
    if args.confirm != case.confirmation_token:
        raise SystemExit(
            "SAFE STOP: exact confirmation token is required; no socket opened"
        )
    if not 0 <= args.post_write_delay <= 10:
        raise SystemExit(
            "SAFE STOP: post-write delay must be between 0 and 10 seconds"
        )

    config = load_config(Path(args.config))
    if not config.direct_read_enabled:
        raise SystemExit("SAFE STOP: direct_read.enabled must be true")
    if not config.direct_host or not config.direct_mac:
        raise SystemExit("SAFE STOP: direct host and MAC are required")

    decoder = YorkPacketDecoder()
    before_comparison: dict[str, Any] = {}

    def approve_precondition(frame: bytes) -> None:
        nonlocal before_comparison
        observed = decoder.decode_state(frame).to_dict()
        before_comparison = _compare(case.before, observed)
        if before_comparison["result"] != "MATCH":
            raise QualificationSafeStop(
                "live precondition mismatch "
                f"({before_comparison['matches']}/{before_comparison['compared']})"
            )

    client = BroadlinkYorkOneShotWriteClient(
        config.direct_host,
        config.direct_port,
        config.direct_mac,
        config.direct_connect_timeout,
        case.command,
    )
    started = datetime.now(timezone.utc)
    try:
        result = client.execute(
            approve_precondition,
            post_write_delay_seconds=args.post_write_delay,
        )
    except QualificationSafeStop as error:
        report = _write_report(
            Path(args.output_dir),
            case,
            {
                "schema_version": 1,
                "version": APP_VERSION,
                "case": case.name,
                "status": "safe_stop",
                "reason": str(error),
                "write_commands_sent": 0,
                "udp_sends": client.last_send_count,
                "before_qualification": before_comparison,
            },
        )
        print(f"SAFE STOP: {error}")
        print("Write commands sent: 0")
        print(f"Report: {report}")
        return 10

    before = decoder.decode_state(result.before_frame).to_dict()
    command_reply = decoder.decode_state(result.command_reply_frame).to_dict()
    after = decoder.decode_state(result.after_frame).to_dict()
    after_comparison = _compare(case.after, after)
    completed = datetime.now(timezone.utc)
    status = "passed" if after_comparison["result"] == "MATCH" else "failed"
    report = _write_report(
        Path(args.output_dir),
        case,
        {
            "schema_version": 1,
            "version": APP_VERSION,
            "case": case.name,
            "status": status,
            "evidence": case.evidence,
            "command": {
                "frame_hex": case.command.hex(" ").upper(),
                "sha256": case.expected_sha256,
                "write_commands_sent": 1,
            },
            "before_state": before,
            "command_reply_state": command_reply,
            "after_state": after,
            "before_qualification": before_comparison,
            "after_qualification": after_comparison,
            "udp_sends": result.send_count,
            "session_id": result.session_id,
            "started_utc": started.isoformat(),
            "completed_utc": completed.isoformat(),
            "safety": {
                "operator_triggered": True,
                "confirmation_token_required": True,
                "pre_read_required": True,
                "post_read_required": True,
                "automatic_retries": 0,
                "automatic_restore": False,
                "mqtt_command_path": False,
            },
        },
    )
    print(f"Before: {_label(before)}")
    print(f"After: {_label(after)}")
    print(
        f"Verification: {after_comparison['result']} "
        f"({after_comparison['matches']}/{after_comparison['compared']})"
    )
    print("Write commands sent: 1")
    print(f"UDP sends: {result.send_count}")
    print("Automatic retries: 0")
    print(f"Report: {report}")
    if status != "passed":
        raise SystemExit("QUALIFICATION FAILED — do not rerun automatically")
    print("QUALIFICATION PASSED — do not rerun this case.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
