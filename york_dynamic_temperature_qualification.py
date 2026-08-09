"""Guarded one-shot qualification of generated York temperature commands."""
from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from adapters.york import (
    BroadlinkYorkTemperatureWriteClient,
    YorkPacketDecoder,
    build_qualified_temperature_command,
)
from configuration import load_config

APP_VERSION = "1.0.0-alpha.27"
CONFIRMATION_TOKEN = "WRITE-GENERATED-HEAT-24-TO-23P5-ONCE"
TARGET_MODE = "heat"
TARGET_TEMPERATURE = 23.5
CAPTURED_HEAT_23P5 = bytes.fromhex(
    "BB0001031901004401080202000000000000000000000000000000000000EC"
)
CAPTURED_SHA256 = "368c47d78986e29e129b32d4b1b5e6cea0be99df63fc59eda2c0556369cd26a0"

EXPECTED_BEFORE: dict[str, Any] = {
    "power": True,
    "mode": "heat",
    "temperature": 24.0,
    "fan": "low",
    "swing": "off",
    "turbo": False,
    "eco": False,
    "health": False,
    "display": True,
}
EXPECTED_AFTER = {**EXPECTED_BEFORE, "temperature": TARGET_TEMPERATURE}


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
    path = output_dir / f"alpha27-dynamic-temperature-{stamp}.json"
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return path


def _validated_generated_command() -> bytes:
    generated = build_qualified_temperature_command(
        TARGET_MODE, TARGET_TEMPERATURE
    )
    if generated != CAPTURED_HEAT_23P5:
        raise SystemExit(
            "SAFE STOP: generated command does not match the captured Relay v2 frame"
        )
    generated_hash = hashlib.sha256(generated).hexdigest()
    if generated_hash != CAPTURED_SHA256:
        raise SystemExit("SAFE STOP: captured command fingerprint is invalid")
    return generated


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate or execute Alpha.27's generated Heat command once."
    )
    parser.add_argument("config", nargs="?", default="/config/config.yml")
    parser.add_argument("--execute", action="store_true")
    parser.add_argument("--confirm", default="")
    parser.add_argument("--output-dir", default="/reports/direct-write")
    parser.add_argument("--post-write-delay", type=float, default=2.0)
    args = parser.parse_args()

    print(
        f"Climate Bridge {APP_VERSION} — "
        "Dynamic Temperature Command Qualification"
    )
    config = load_config(Path(args.config))
    generated = _validated_generated_command()
    command_hash = hashlib.sha256(generated).hexdigest()
    if not config.direct_read_enabled:
        raise SystemExit("SAFE STOP: direct_read.enabled must be true")
    if not config.direct_host or not config.direct_mac:
        raise SystemExit("SAFE STOP: direct host and MAC are required")

    print(f"Target: {config.direct_host}:{config.direct_port}/udp")
    print(f"Generated command: {generated.hex(' ').upper()}")
    print(f"Generated SHA-256: {command_hash}")
    print("Captured Relay v2 match: exact (31/31 bytes)")
    print("Required live state: On / Heat / 24 °C / Fan Low / Swing Off")
    print("Qualified result: On / Heat / 23.5 °C / Fan Low / Swing Off")
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

    decoder = YorkPacketDecoder()
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
    client = BroadlinkYorkTemperatureWriteClient(
        config.direct_host,
        config.direct_port,
        config.direct_mac,
        config.direct_connect_timeout,
        TARGET_MODE,
        TARGET_TEMPERATURE,
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
                    "generated_command": True,
                    "capture_match_required": True,
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
                "source": "generated and matched to Relay v2 transactions 22/23",
                "mode": TARGET_MODE,
                "target_temperature": TARGET_TEMPERATURE,
                "frame_hex": generated.hex(" ").upper(),
                "sha256": command_hash,
                "capture_match": True,
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
                "generated_command": True,
                "capture_match_required": True,
                "pre_read_required": True,
                "post_read_required": True,
                "automatic_retries": 0,
                "automatic_restore": False,
                "mqtt_command_path": False,
            },
        },
    )
    print(
        f"DYNAMIC ONE-SHOT RESULT: {after_comparison['result']} "
        f"({after_comparison['matches']}/{after_comparison['compared']})"
    )
    print(f"Write commands sent: 1; total UDP sends: {result.send_count}")
    print(f"Before temperature: {before['temperature']}")
    print(f"After temperature: {after['temperature']}")
    print(f"Report: {report}")
    return 0 if status == "passed" else 2


if __name__ == "__main__":
    raise SystemExit(main())
