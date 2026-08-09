"""One-shot, operator-controlled native York state probe for Sprint 2.7."""
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from adapters.york import YorkConnection, YorkProtocolSession
from adapters.york.encoder import YorkPacketEncoder
from configuration import load_config
from protocols.york.packet_library import find_verified_state_request

ROOT = Path(__file__).resolve().parent
DEFAULT_LIBRARY = ROOT / "protocols" / "york" / "packet_library"


def _normalise_relay_state(state: dict[str, Any]) -> dict[str, Any]:
    aliases = {
        "power": ("power", "is_on", "on"),
        "mode": ("mode", "hvac_mode"),
        "fan": ("fan", "fan_mode", "fanspeed", "fan_speed"),
        "swing": ("swing", "swing_mode"),
        "turbo": ("turbo",),
        "eco": ("eco",),
        "health": ("health",),
        "display": ("display", "display_on"),
    }
    normalised: dict[str, Any] = {}
    for target, keys in aliases.items():
        for key in keys:
            if key in state and state[key] is not None:
                value = state[key]
                if target == "power" and isinstance(value, str):
                    value = value.strip().lower() in {"on", "true", "1"}
                if target in {"mode", "fan", "swing"} and isinstance(value, str):
                    value = value.strip().lower().replace("-", "_").replace(" ", "_")
                normalised[target] = value
                break
    return normalised


def _compare(native: dict[str, Any], relay: dict[str, Any]) -> dict[str, Any]:
    fields: dict[str, dict[str, Any]] = {}
    matches = 0
    mismatches = 0
    for key, native_value in native.items():
        if key not in relay:
            continue
        relay_value = relay[key]
        matched = native_value == relay_value
        fields[key] = {"native": native_value, "relay": relay_value, "match": matched}
        if matched:
            matches += 1
        else:
            mismatches += 1
    return {
        "fields": fields,
        "compared": len(fields),
        "matches": matches,
        "mismatches": mismatches,
        "result": "MATCH" if fields and mismatches == 0 else "MISMATCH" if fields else "NO_COMMON_FIELDS",
    }


def _update_aggregate(path: Path, comparison: dict[str, Any]) -> dict[str, Any]:
    try:
        aggregate = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        aggregate = {
            "schema_version": 1,
            "probes": 0,
            "replies": 0,
            "decoded_replies": 0,
            "relay_matches": 0,
            "relay_mismatches": 0,
        }
    aggregate["probes"] = int(aggregate.get("probes", 0)) + 1
    aggregate["replies"] = int(aggregate.get("replies", 0)) + 1
    aggregate["decoded_replies"] = int(aggregate.get("decoded_replies", 0)) + 1
    if comparison["result"] == "MATCH":
        aggregate["relay_matches"] = int(aggregate.get("relay_matches", 0)) + 1
    elif comparison["result"] == "MISMATCH":
        aggregate["relay_mismatches"] = int(aggregate.get("relay_mismatches", 0)) + 1
    compared = int(aggregate.get("relay_matches", 0)) + int(aggregate.get("relay_mismatches", 0))
    aggregate["confidence_percent"] = round(100 * int(aggregate.get("relay_matches", 0)) / compared, 2) if compared else None
    aggregate["updated_utc"] = datetime.now(timezone.utc).isoformat()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(aggregate, indent=2) + "\n", encoding="utf-8")
    return aggregate


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Send one verified York state request, decode the response, and save "
            "direct-LAN qualification evidence."
        )
    )
    parser.add_argument("config", nargs="?", default="/config/config.yml")
    parser.add_argument("--packet-library", default=str(DEFAULT_LIBRARY))
    parser.add_argument("--record-id", default="")
    parser.add_argument("--output-dir", default="/reports/native-probes")
    parser.add_argument(
        "--validate-only",
        action="store_true",
        help="Validate and print the selected request without opening a socket.",
    )
    parser.add_argument(
        "--confirm-transmit",
        action="store_true",
        help=(
            "Deliberately authorize this one-shot state request. "
            "Also requires direct_device.enabled: true."
        ),
    )
    args = parser.parse_args()

    config = load_config(Path(args.config))
    record = find_verified_state_request(Path(args.packet_library), args.record_id)
    request = YorkPacketEncoder.parse_captured_hex(record.frame_hex)

    if args.validate_only:
        print(f"Verified York request: {record.record_id}")
        print(record.frame_hex)
        print("Validation only: no socket opened and no packet transmitted.")
        return 0
    if not config.direct_enabled or not args.confirm_transmit:
        print(
            "SAFE STOP: native transmission requires "
            "direct_device.enabled: true and --confirm-transmit."
        )
        print("Packets Sent: 0")
        return 12

    session = YorkProtocolSession(
        YorkConnection(config.direct_host, config.direct_port, config.direct_connect_timeout),
        encoder=YorkPacketEncoder(record.frame_hex),
    )

    started = datetime.now(timezone.utc)
    try:
        session.open()
        response = session.connection.exchange(request)
        frame = session.inspect_captured_frame(response)
        native_state = session.decoder.decode_state(response).to_dict()
    finally:
        session.close()

    comparison = {
        "fields": {},
        "compared": 0,
        "matches": 0,
        "mismatches": 0,
        "result": "DIRECT_ONLY",
    }

    completed = datetime.now(timezone.utc)
    timestamp = completed.strftime("%Y%m%dT%H%M%SZ")
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    output = output_dir / f"york-native-probe-{timestamp}.json"
    aggregate_path = output_dir / "native-qualification.json"
    aggregate = _update_aggregate(aggregate_path, comparison)

    report = {
        "schema_version": 2,
        "probe_status": "decoded_direct_lan",
        "request_record_id": record.record_id,
        "request_record_status": record.status,
        "request_source": record.source,
        "started_utc": started.isoformat(),
        "completed_utc": completed.isoformat(),
        "elapsed_ms": round((completed - started).total_seconds() * 1000, 1),
        "endpoint": {"host": config.direct_host, "port": config.direct_port},
        "request_hex": request.hex(" ").upper(),
        "request_length": len(request),
        "response_hex": frame.hex,
        "response_length": len(frame.raw),
        "response_header": f"0x{frame.header:02X}",
        "decoded_state": native_state,
        "qualification": comparison,
        "aggregate": aggregate,
        "safety": {
            "one_shot": True,
            "automatic_retry": False,
            "write_commands_enabled": False,
        },
    }
    output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

    print(f"Native York response decoded: {native_state}")
    print("Qualification source: authenticated direct LAN read")
    print(f"Probe report: {output}")
    print(f"Aggregate qualification: {aggregate_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
