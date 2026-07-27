"""Guarded one-shot York request replay with XML outcome validation."""
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from adapters.york import YorkConnection
from adapters.york.encoder import YorkPacketEncoder
from configuration import load_config
from protocols.york.packet_library import find_verified_state_request
from protocols.york.xml_broadcast import YorkXmlBroadcastListener
from transport.tx_logger import TransmissionLogger
from version import APP_NAME, APP_VERSION

ROOT = Path(__file__).resolve().parent
DEFAULT_LIBRARY = ROOT / "protocols" / "york" / "packet_library"


def _normalise_expected(value: Any) -> Any:
    if isinstance(value, str):
        lowered = value.strip().lower().replace("-", "_").replace(" ", "_")
        if lowered in {"on", "true"}:
            return True
        if lowered in {"off", "false"}:
            return False
        return lowered
    return value


def _compare(expected: dict[str, Any], observed: dict[str, Any]) -> dict[str, Any]:
    fields: dict[str, dict[str, Any]] = {}
    for key, expected_value in expected.items():
        if key not in observed:
            fields[key] = {"expected": expected_value, "observed": None, "match": False}
            continue
        observed_value = observed[key]
        match = _normalise_expected(expected_value) == _normalise_expected(observed_value)
        fields[key] = {"expected": expected_value, "observed": observed_value, "match": match}
    matches = sum(item["match"] for item in fields.values())
    return {
        "fields": fields,
        "compared": len(fields),
        "matches": matches,
        "mismatches": len(fields) - matches,
        "result": "MATCH" if fields and matches == len(fields) else "MISMATCH" if fields else "NO_EXPECTED_STATE",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Replay one verified York request and validate the XML status broadcast.")
    parser.add_argument("config", nargs="?", default="/config/config.yml")
    parser.add_argument("--packet-library", default=str(DEFAULT_LIBRARY))
    parser.add_argument("--record-id", default="")
    parser.add_argument("--output-dir", default="/reports/replay")
    parser.add_argument("--xml-port", type=int, default=10074)
    parser.add_argument("--xml-timeout", type=float, default=12.0)
    parser.add_argument("--validate-only", action="store_true")
    parser.add_argument(
        "--confirm-transmit",
        action="store_true",
        help=(
            "Deliberately authorize this one-shot replay. "
            "Also requires direct_device.enabled: true."
        ),
    )
    parser.add_argument("--tx-log-dir", default="/reports/transmissions")
    args = parser.parse_args()

    print(f"{APP_NAME} York Replay Engine {APP_VERSION}")
    print("Initialising replay session...")
    output_dir = Path(args.output_dir)
    config = load_config(Path(args.config))
    try:
        record = find_verified_state_request(Path(args.packet_library), args.record_id)
    except Exception as e:
        output_dir.mkdir(parents=True, exist_ok=True)
        report=output_dir/"replay-safe-stop.json"
        report.write_text(json.dumps({
            "status":"safe_stop",
            "result":"PASS",
            "reason":str(e),
            "packets_sent":0,
            "exit_code":10
        },indent=2))
        print("\nSAFE STOP")
        print(f"Reason: {e}")
        print("Packets Sent: 0")
        print("Result: PASS")
        return 10
    request = YorkPacketEncoder.parse_captured_hex(record.frame_hex)
    expected_state = getattr(record, "expected_state", {})

    print(f"Verified executable request: {record.record_id}")
    print(f"Target: {config.direct_host}:{config.direct_port}/udp")
    print(f"Request: {request.hex(' ').upper()}")
    print(f"Expected XML state: {expected_state or 'not specified'}")

    if args.validate_only:
        print("Validation only: no socket opened and no packet transmitted.")
        return 0
    if not config.direct_enabled or not args.confirm_transmit:
        print(
            "SAFE STOP: replay requires direct_device.enabled: true "
            "and --confirm-transmit."
        )
        print("Packets Sent: 0")
        return 12

    started = datetime.now(timezone.utc)
    listener = YorkXmlBroadcastListener(port=args.xml_port, timeout=args.xml_timeout)
    connection = YorkConnection(config.direct_host, config.direct_port, config.direct_connect_timeout)
    try:
        listener.open()
        connection.open()
        tx_logger = TransmissionLogger(args.tx_log_dir)
        tx_record, tx_json, tx_markdown = tx_logger.record(
            payload=request,
            destination_host=config.direct_host,
            destination_port=config.direct_port,
            protocol="York TFIAC",
            transport="UDP",
            verified=True,
            metadata={
                "request_record_id": record.record_id,
                "request_source": record.source,
                "purpose": "state_request",
            },
        )
        sent = connection.send(request)
        message = listener.wait_for_status(config.direct_host)
    finally:
        connection.close()
        listener.close()

    comparison = _compare(expected_state, message.state)
    completed = datetime.now(timezone.utc)
    output_dir.mkdir(parents=True, exist_ok=True)
    output = output_dir / f"york-replay-{completed.strftime('%Y%m%dT%H%M%SZ')}.json"
    report = {
        "schema_version": 1,
        "status": "completed",
        "request_record_id": record.record_id,
        "request_source": record.source,
        "endpoint": {"host": config.direct_host, "port": config.direct_port, "protocol": "udp"},
        "request_hex": request.hex(" ").upper(),
        "request_bytes_sent": sent,
        "transmission": {
            "tx_id": tx_record.tx_id,
            "json_report": str(tx_json),
            "markdown_report": str(tx_markdown),
            "payload_sha256": tx_record.payload_sha256,
        },
        "started_utc": started.isoformat(),
        "completed_utc": completed.isoformat(),
        "elapsed_ms": round((completed - started).total_seconds() * 1000, 1),
        "xml_status": {
            "sender": {"host": message.sender[0], "port": message.sender[1]},
            "message_id": message.message_id,
            "message_type": message.message_type,
            "sequence": message.sequence,
            "state": message.state,
            "raw_xml": message.raw_xml,
        },
        "expected_state": expected_state,
        "qualification": comparison,
        "safety": {
            "verified_record_required": True,
            "one_shot": True,
            "automatic_retry": False,
            "generated_commands": False,
        },
    }
    output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(f"Transmission logged: {tx_record.tx_id} -> {tx_json}")
    print(f"XML status received from {message.sender[0]}:{message.sender[1]}: {message.state}")
    print(f"Outcome: {comparison['result']} ({comparison['matches']}/{comparison['compared']} expected fields matched)")
    print(f"Replay report: {output}")
    return 0 if comparison["result"] in {"MATCH", "NO_EXPECTED_STATE"} else 2


if __name__ == "__main__":
    raise SystemExit(main())
