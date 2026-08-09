"""Guarded one-shot qualification of exact captured York power commands."""
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
    YORK_QUALIFICATION_POWER_OFF,
    YORK_QUALIFICATION_POWER_OFF_HEAT,
    YORK_QUALIFICATION_POWER_ON_COOL,
    YORK_QUALIFICATION_POWER_ON_HEAT,
    YorkPacketDecoder,
)
from adapters.york.broadlink import york_xor
from configuration import load_config
from version import APP_VERSION


@dataclass(frozen=True)
class PowerCase:
    name: str
    command: bytes
    confirmation_token: str
    before: dict[str, Any]
    after: dict[str, Any]
    source_reference: str
    expected_sha256: str
    expected_length: int


COMMON_DISABLED = {
    "turbo": False,
    "eco": False,
    "health": False,
    "display": True,
}

CASES = {
    "off": PowerCase(
        name="off",
        command=YORK_QUALIFICATION_POWER_OFF,
        confirmation_token="WRITE-QUALIFIED-POWER-OFF-ONCE",
        before={
            "power": True,
            "mode": "cool",
            "temperature": 25.0,
            "fan": "high",
            "swing": "vertical",
            **COMMON_DISABLED,
        },
        after={
            "power": False,
            "mode": "cool",
            "temperature": 25.0,
            "fan": "high",
            "swing": "vertical",
            **COMMON_DISABLED,
        },
        source_reference="Relay v2 transaction 46",
        expected_sha256=(
            "46b8d41444e8363bf591b41c4334386fe509b2063a42863bd143900c0cbfc629"
        ),
        expected_length=31,
    ),
    "off-heat": PowerCase(
        name="off-heat",
        command=YORK_QUALIFICATION_POWER_OFF_HEAT,
        confirmation_token="WRITE-QUALIFIED-POWER-OFF-HEAT-ONCE",
        before={
            "power": True,
            "mode": "heat",
            "temperature": 25.0,
            "fan": "high",
            "swing": "vertical",
            **COMMON_DISABLED,
        },
        after={
            "power": False,
            "mode": "heat",
            "temperature": 25.0,
            "fan": "high",
            "swing": "vertical",
            **COMMON_DISABLED,
        },
        source_reference=(
            "successful Relay v2 Power Off from Heat transaction #7 "
            "(2026-07-30)"
        ),
        expected_sha256=(
            "6be1093e8fb776faf047513d3b0bd6b9cca2166fac49d60346ce1f3575707b58"
        ),
        expected_length=31,
    ),
    "on-heat": PowerCase(
        name="on-heat",
        command=YORK_QUALIFICATION_POWER_ON_HEAT,
        confirmation_token="WRITE-QUALIFIED-POWER-ON-HEAT-ONCE",
        before={
            "power": False,
            "mode": "cool",
            "temperature": 25.0,
            "fan": "high",
            "swing": "vertical",
            **COMMON_DISABLED,
        },
        after={
            "power": True,
            "mode": "heat",
            "temperature": 25.0,
            "fan": "high",
            "swing": "vertical",
            **COMMON_DISABLED,
        },
        source_reference=(
            "fresh successful Relay v2 Power On + Heat log (2026-07-29)"
        ),
        expected_sha256=(
            "a499631892d2f17255351c7fd8ff2974532d508c01f1e589a49e49bd9a891515"
        ),
        expected_length=31,
    ),
    "on-cool": PowerCase(
        name="on-cool",
        command=YORK_QUALIFICATION_POWER_ON_COOL,
        confirmation_token="WRITE-QUALIFIED-POWER-ON-COOL-ONCE",
        before={
            "power": False,
            "mode": "heat",
            "temperature": 25.0,
            "fan": "high",
            "swing": "vertical",
            **COMMON_DISABLED,
        },
        after={
            "power": True,
            "mode": "cool",
            "temperature": 25.0,
            "fan": "high",
            "swing": "vertical",
            **COMMON_DISABLED,
        },
        source_reference=(
            "fresh successful Relay v2 Power On + Cool transaction #4 "
            "(2026-07-29)"
        ),
        expected_sha256=(
            "41fc632383cbbe62b9db91e018f9b9f73eaac3315e218439fa4e6f93c01e667c"
        ),
        expected_length=31,
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


def _validate_case(case: PowerCase) -> None:
    if len(case.command) != case.expected_length:
        raise SystemExit(
            f"SAFE STOP: {case.name} command is not "
            f"{case.expected_length} bytes"
        )
    if york_xor(case.command):
        raise SystemExit(f"SAFE STOP: {case.name} York checksum is invalid")
    if hashlib.sha256(case.command).hexdigest() != case.expected_sha256:
        raise SystemExit(f"SAFE STOP: {case.name} command fingerprint is invalid")


def _state_label(state: dict[str, Any]) -> str:
    power = "On" if state["power"] else "Off"
    return (
        f"{power} / {state['mode'].title()} / {state['temperature']:g} °C / "
        f"Fan {state['fan'].title()} / Swing {state['swing'].title()}"
    )


def _print_case(case: PowerCase) -> None:
    print(f"Power {case.name.replace('-', ' ').title()} case:")
    print(f"  Required live state: {_state_label(case.before)}")
    print(f"  Qualified result: {_state_label(case.after)}")
    print(f"  Exact captured command: {case.command.hex(' ').upper()}")
    print(f"  Command SHA-256: {hashlib.sha256(case.command).hexdigest()}")
    print(f"  Official Relay v2 source: {case.source_reference}")
    print(
        f"  Captured frame: exact "
        f"({case.expected_length}/{case.expected_length} bytes)"
    )
    print(f"  Confirmation token: {case.confirmation_token}")


def _write_report(
    output_dir: Path, case: PowerCase, payload: dict[str, Any]
) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    version_tag = APP_VERSION.replace(".", "-")
    path = output_dir / f"{version_tag}-power-{case.name}-{stamp}.json"
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return path


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Validate the exact Power Off from Cool, Power Off from Heat, "
            "Power On + Heat, and Power On + Cool frames or execute "
            "one guarded case once."
        )
    )
    parser.add_argument("config", nargs="?", default="/config/config.yml")
    parser.add_argument("--case", choices=tuple(CASES))
    parser.add_argument("--execute", action="store_true")
    parser.add_argument("--confirm", default="")
    parser.add_argument("--output-dir", default="/reports/direct-write")
    parser.add_argument("--post-write-delay", type=float, default=2.0)
    args = parser.parse_args()

    print(f"Climate Bridge {APP_VERSION} — Power One-Shot Qualification")
    config = load_config(Path(args.config))
    if not config.direct_read_enabled:
        raise SystemExit("SAFE STOP: direct_read.enabled must be true")
    if not config.direct_host or not config.direct_mac:
        raise SystemExit("SAFE STOP: direct host and MAC are required")

    for case in CASES.values():
        _validate_case(case)
    print(f"Target: {config.direct_host}:{config.direct_port}/udp")
    for case in CASES.values():
        _print_case(case)
    print("Automatic retries: 0")
    print("Automatic restore: disabled")
    print(
        "Normal MQTT power path: four exact guarded cases with Relay v2 fallback"
    )

    if not args.execute:
        print("VALIDATION PASSED — no socket opened and no packet transmitted.")
        print("Execution requires --case plus that case's exact confirmation token.")
        return 0
    if args.case is None:
        raise SystemExit(
            "SAFE STOP: --case off, --case off-heat, --case on-heat, or "
            "--case on-cool is required; "
            "no socket opened"
        )
    case = CASES[args.case]
    if args.confirm != case.confirmation_token:
        raise SystemExit(
            "SAFE STOP: exact confirmation token is required; no socket opened"
        )
    if not 0 <= args.post_write_delay <= 10:
        raise SystemExit(
            "SAFE STOP: post-write delay must be between 0 and 10 seconds"
        )

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
            "source_reference": case.source_reference,
            "command": {
                "frame_hex": case.command.hex(" ").upper(),
                "sha256": hashlib.sha256(case.command).hexdigest(),
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
                "captured_command_only": True,
                "pre_read_required": True,
                "post_read_required": True,
                "automatic_retries": 0,
                "automatic_restore": False,
                "mqtt_command_path": False,
            },
        },
    )
    print(
        f"POWER {case.name.upper()} ONE-SHOT RESULT: "
        f"{after_comparison['result']} "
        f"({after_comparison['matches']}/{after_comparison['compared']})"
    )
    print(f"Write commands sent: 1; total UDP sends: {result.send_count}")
    print(f"Before power: {before['power']}")
    print(f"After power: {after['power']}")
    print(f"Report: {report}")
    return 0 if status == "passed" else 2


if __name__ == "__main__":
    raise SystemExit(main())
