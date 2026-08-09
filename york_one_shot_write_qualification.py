"""Guarded one-shot direct-write qualification for one captured York command."""
from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from adapters.york import (
    BroadlinkYorkOneShotWriteClient,
    YORK_QUALIFICATION_COOL_22_TO_25,
    YorkPacketDecoder,
)
from configuration import load_config

APP_VERSION = "1.0.0-alpha.25"
CONFIRMATION_TOKEN = "WRITE-COOL-22-TO-25-ONCE"
COMMAND_SHA256 = "acb05ce375487cb3093b86d3c71ffe211acb46a9c15f2a26047972615ffa60b4"

EXPECTED_BEFORE: dict[str, Any] = {
    "power": True,
    "mode": "cool",
    "temperature": 22.0,
    "fan": "low",
    "swing": "off",
    "turbo": False,
    "eco": False,
    "health": False,
    "display": True,
}
EXPECTED_AFTER = {**EXPECTED_BEFORE, "temperature": 25.0}


class QualificationSafeStop(RuntimeError):
    pass


def _compare(expected: dict[str, Any], observed: dict[str, Any]) -> dict[str, Any]:
    fields: dict[str, dict[str, Any]] = {}
    for key, expected_value in expected.items():
        observed_value = observed.get(key)
        fields[key] = {
            "expected": expected_value,
            "observed": observed_value,
            "match": observed_value == expected_value,
        }
    matches = sum(int(item["match"]) for item in fields.values())
    return {
        "fields": fields,
        "matches": matches,
        "compared": len(fields),
        "result": "MATCH" if matches == len(fields) else "MISMATCH",
    }


def _write_report(output_dir: Path, payload: dict[str, Any]) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    path = output_dir / f"alpha25-one-shot-{stamp}.json"
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return path


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate or execute Alpha.25's one captured York command once."
    )
    parser.add_argument("config", nargs="?", default="/config/config.yml")
    parser.add_argument("--execute", action="store_true")
    parser.add_argument("--confirm", default="")
    parser.add_argument("--output-dir", default="/reports/direct-write")
    parser.add_argument("--post-write-delay", type=float, default=2.0)
    args = parser.parse_args()

    print(f"Climate Bridge {APP_VERSION} — One-Shot Direct-Write Qualification")
    config = load_config(Path(args.config))
    decoder = YorkPacketDecoder()
    command_hash = hashlib.sha256(YORK_QUALIFICATION_COOL_22_TO_25).hexdigest()
    if command_hash != COMMAND_SHA256:
        raise SystemExit("SAFE STOP: embedded command fingerprint is invalid")
    if not config.direct_read_enabled:
        raise SystemExit("SAFE STOP: direct_read.enabled must be true")
    if not config.direct_host or not config.direct_mac:
        raise SystemExit("SAFE STOP: direct host and MAC are required")

    print(f"Target: {config.direct_host}:{config.direct_port}/udp")
    print(f"Fixed command SHA-256: {command_hash}")
    print("Required live state: On / Cool / 22 °C / Fan Low / Swing Off")
    print("Qualified result: On / Cool / 25 °C / Fan Low / Swing Off")
    print("Automatic retries: 0")
    print("Automatic restore: disabled")

    if not args.execute:
        print("VALIDATION PASSED — no socket opened and no packet transmitted.")
        print(f"To execute once, supply --execute --confirm {CONFIRMATION_TOKEN}")
        return 0
    if args.confirm != CONFIRMATION_TOKEN:
        raise SystemExit(
            "SAFE STOP: exact confirmation token is required; no socket opened"
        )
    if not 0 <= args.post_write_delay <= 10:
        raise SystemExit("SAFE STOP: post-write delay must be between 0 and 10 seconds")

    before_comparison: dict[str, Any] = {}

    def approve_precondition(frame: bytes) -> None:
        nonlocal before_comparison
        observed = decoder.decode_state(frame).to_dict()
        before_comparison = _compare(EXPECTED_BEFORE, observed)
        if before_comparison["result"] != "MATCH":
            raise QualificationSafeStop(
                f"live precondition mismatch "
                f"({before_comparison['matches']}/{before_comparison['compared']})"
            )

    started = datetime.now(timezone.utc)
    client = BroadlinkYorkOneShotWriteClient(
        config.direct_host,
        config.direct_port,
        config.direct_mac,
        config.direct_connect_timeout,
    )
    try:
        result = client.execute(
            approve_precondition,
            post_write_delay_seconds=args.post_write_delay,
        )
    except QualificationSafeStop as error:
        report = _write_report(
            Path(args.output_dir),
            {
                "schema_version": 1,
                "version": APP_VERSION,
                "status": "safe_stop",
                "reason": str(error),
                "write_commands_sent": 0,
                "udp_sends": client.last_send_count,
                "before_qualification": before_comparison,
                "safety": {
                    "fixed_command_only": True,
                    "automatic_retries": 0,
                    "automatic_restore": False,
                },
            },
        )
        print(f"SAFE STOP: {error}")
        print("Write commands sent: 0")
        print(f"Report: {report}")
        return 10

    before = decoder.decode_state(result.before_frame).to_dict()
    command_reply = decoder.decode_state(result.command_reply_frame).to_dict()
    after = decoder.decode_state(result.after_frame).to_dict()
    after_comparison = _compare(EXPECTED_AFTER, after)
    completed = datetime.now(timezone.utc)
    status = "passed" if after_comparison["result"] == "MATCH" else "failed"
    report = _write_report(
        Path(args.output_dir),
        {
            "schema_version": 1,
            "version": APP_VERSION,
            "status": status,
            "command": {
                "source": "York TFIAC Relay v2 transaction 2",
                "frame_hex": YORK_QUALIFICATION_COOL_22_TO_25.hex(" ").upper(),
                "sha256": command_hash,
                "write_commands_sent": 1,
            },
            "endpoint": {
                "host": config.direct_host,
                "port": config.direct_port,
                "mac": config.direct_mac,
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
            "elapsed_ms": round((completed - started).total_seconds() * 1000, 1),
            "safety": {
                "operator_triggered": True,
                "confirmation_token_required": True,
                "fixed_command_only": True,
                "pre_read_required": True,
                "post_read_required": True,
                "automatic_retries": 0,
                "automatic_restore": False,
                "mqtt_command_path": False,
            },
        },
    )
    print(
        f"ONE-SHOT RESULT: {after_comparison['result']} "
        f"({after_comparison['matches']}/{after_comparison['compared']})"
    )
    print(f"Write commands sent: 1; total UDP sends: {result.send_count}")
    print(f"Before temperature: {before['temperature']}")
    print(f"After temperature: {after['temperature']}")
    print(f"Report: {report}")
    return 0 if status == "passed" else 2


if __name__ == "__main__":
    raise SystemExit(main())
