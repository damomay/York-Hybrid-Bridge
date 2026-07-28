"""Guarded importer for structured Android native-request captures.

This module is evidence tooling only. It does not open a network socket,
verify a request, or make an imported frame executable.
"""
from __future__ import annotations

import hashlib
import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from adapters.york.errors import YorkFrameError


CAPTURE_TYPE = "native_york_controller_request"
SHA256_RE = re.compile(r"^[0-9a-fA-F]{64}$")
HEX_RE = re.compile(r"^[0-9A-Fa-f]{2}( [0-9A-Fa-f]{2})*$")
MAC_RE = re.compile(r"^[0-9A-Fa-f]{12}$")


def _required_mapping(value: Any, field: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ValueError(f"{field} must be an object")
    return value


def _required_text(mapping: dict[str, Any], field: str) -> str:
    value = str(mapping.get(field, "")).strip()
    if not value:
        raise ValueError(f"{field} is required")
    return value


def _timestamp(value: str) -> str:
    candidate = value.replace("Z", "+00:00")
    try:
        parsed = datetime.fromisoformat(candidate)
    except ValueError as error:
        raise ValueError("timestamp_utc must be an ISO-8601 timestamp") from error
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise ValueError("timestamp_utc must include a UTC offset")
    if parsed.utcoffset().total_seconds() != 0:
        raise ValueError("timestamp_utc must be UTC")
    return parsed.isoformat()


def _frame(value: Any) -> bytes:
    frame_hex = str(value or "").strip()
    if not HEX_RE.fullmatch(frame_hex):
        raise YorkFrameError(
            "frame_hex must contain complete space-separated hexadecimal bytes"
        )
    frame = bytes.fromhex(frame_hex)
    if len(frame) < 4:
        raise YorkFrameError("Captured York request is too short")
    if frame[0] != 0xBB:
        raise YorkFrameError("Captured York request does not start with 0xBB")
    return frame


def _endpoint(value: Any) -> dict[str, Any]:
    endpoint = _required_mapping(value, "endpoint")
    transport = _required_text(endpoint, "transport").lower()
    if transport in {"udp", "tcp"}:
        host = _required_text(endpoint, "host")
        port = endpoint.get("port")
        if (
            not isinstance(port, int)
            or isinstance(port, bool)
            or not 1 <= port <= 65535
        ):
            raise ValueError("endpoint.port must be an integer from 1 to 65535")
        return {"transport": transport, "host": host, "port": port}
    if transport == "broadlink_sdk_passthrough":
        target_mac = re.sub(
            r"[:-]", "", _required_text(endpoint, "target_mac")
        ).lower()
        if not MAC_RE.fullmatch(target_mac):
            raise ValueError("endpoint.target_mac must be a six-byte MAC address")
        return {"transport": transport, "target_mac": target_mac}
    raise ValueError(
        "endpoint.transport must be udp, tcp, or broadlink_sdk_passthrough"
    )


def _xor_checksum(frame: bytes) -> dict[str, Any]:
    calculated = 0
    for value in frame[:-1]:
        calculated ^= value
    return {
        "algorithm_candidate": "xor_all_bytes_except_last",
        "calculated": f"{calculated:02X}",
        "captured": f"{frame[-1]:02X}",
        "matches": calculated == frame[-1],
        "status": "candidate_only",
    }


def import_native_capture(capture_path: Path, output_root: Path) -> dict[str, Any]:
    """Import one structured native request as private, non-executable evidence."""
    raw_bytes = capture_path.read_bytes()
    try:
        capture = json.loads(raw_bytes)
    except json.JSONDecodeError as error:
        raise ValueError(f"Invalid capture JSON: {error}") from error
    if not isinstance(capture, dict):
        raise ValueError("capture root must be an object")

    if capture.get("schema_version") != 1:
        raise ValueError("schema_version must be 1")
    if capture.get("evidence_type") != CAPTURE_TYPE:
        raise ValueError(f"evidence_type must be {CAPTURE_TYPE}")
    if capture.get("direction") != "controller_to_device":
        raise ValueError("direction must be controller_to_device")

    timestamp = _timestamp(_required_text(capture, "timestamp_utc"))
    endpoint = _endpoint(capture.get("endpoint"))

    action = _required_mapping(capture.get("action"), "action")
    marker = _required_text(action, "marker")
    requested_state = _required_mapping(
        action.get("requested_state"), "action.requested_state"
    )

    source = _required_mapping(capture.get("source"), "source")
    artifact = _required_text(source, "artifact")
    tool = _required_text(source, "tool")
    hook_point = _required_text(source, "hook_point")
    artifact_sha256 = _required_text(source, "artifact_sha256").lower()
    if not SHA256_RE.fullmatch(artifact_sha256):
        raise ValueError("source.artifact_sha256 must be a SHA-256 digest")

    frame = _frame(capture.get("frame_hex"))
    input_sha256 = hashlib.sha256(raw_bytes).hexdigest()
    frame_sha256 = hashlib.sha256(frame).hexdigest()
    record_id = f"yrk-observed-request-{input_sha256[:12]}"

    record = {
        "schema_version": 1,
        "id": record_id,
        "protocol": "york_tfiac_20014",
        "kind": "command_request",
        "purpose": str(action.get("purpose", "command_request")).strip()
        or "command_request",
        "direction": "controller_to_device",
        "frame_hex": frame.hex(" ").upper(),
        "frame_length": len(frame),
        "expected_state": requested_state,
        "observations": {
            "timestamp_utc": timestamp,
            "action_marker": marker,
            "endpoint": endpoint,
            "framing": {
                "header": "BB",
                "header_matches": frame[0] == 0xBB,
                "frame_sha256": frame_sha256,
            },
            "checksum_analysis": _xor_checksum(frame),
        },
        "source": {
            "capture_file": capture_path.name,
            "capture_timestamp": timestamp,
            "capture_sha256": input_sha256,
            "artifact": artifact,
            "artifact_sha256": artifact_sha256,
            "tool": tool,
            "hook_point": hook_point,
            "notes": (
                "Structured Android runtime capture imported without "
                "verification or transmission."
            ),
            "transformations": [
                "validated required controller-to-device provenance",
                "normalised hexadecimal frame bytes to uppercase",
                "calculated a candidate XOR checksum without accepting it",
            ],
        },
        "verification": {
            "status": "observed",
            "safe_to_transmit": False,
            "verified_by": "",
            "verified_at": "",
            "replay_count": 0,
            "successful_responses": 0,
        },
        "notes": (
            "Observed request evidence only. Independent human verification "
            "is required; no transmission is authorized."
        ),
    }
    relay_transaction = source.get("relay_transaction")
    if relay_transaction is not None:
        record["source"]["relay_transaction"] = _required_mapping(
            relay_transaction, "source.relay_transaction"
        )

    library = output_root / "packet_library" / "observed"
    reports = output_root / "reports"
    library.mkdir(parents=True, exist_ok=True)
    reports.mkdir(parents=True, exist_ok=True)
    record_path = library / f"{record_id}.json"
    report_path = reports / f"{record_id}-import.json"
    record_path.write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
    report = {
        "status": "IMPORTED_OBSERVED_NON_EXECUTABLE",
        "record_id": record_id,
        "record_file": str(record_path),
        "source_capture": capture_path.name,
        "source_capture_sha256": input_sha256,
        "frame_sha256": frame_sha256,
        "packets_transmitted": 0,
        "network_sockets_opened": 0,
        "safe_to_transmit": False,
    }
    report_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    report["report_file"] = str(report_path)
    return report


def _relay_timestamp(value: Any, source_timezone: str) -> str:
    raw = str(value or "").strip()
    try:
        local = datetime.strptime(raw, "%Y-%m-%d %H:%M:%S.%f")
    except ValueError as error:
        raise ValueError(
            "relay started_at must use yyyy-MM-dd HH:mm:ss.SSS"
        ) from error
    try:
        timezone = ZoneInfo(source_timezone)
    except ZoneInfoNotFoundError as error:
        raise ValueError(f"Unknown source timezone: {source_timezone}") from error
    return local.replace(tzinfo=timezone).astimezone(ZoneInfo("UTC")).isoformat()


def import_relay_transactions(
    export_path: Path,
    output_root: Path,
    *,
    artifact: str,
    artifact_sha256: str,
    target_mac: str,
    source_timezone: str,
) -> dict[str, Any]:
    """Import verified Relay v2 transactions as non-executable evidence."""
    raw_bytes = export_path.read_bytes()
    try:
        export = json.loads(raw_bytes)
    except json.JSONDecodeError as error:
        raise ValueError(f"Invalid relay export JSON: {error}") from error
    if not isinstance(export, dict) or not isinstance(
        export.get("transactions"), list
    ):
        raise ValueError("relay export must contain a transactions array")
    transactions = export["transactions"]
    if export.get("count") != len(transactions):
        raise ValueError("relay export count does not match transactions")
    if not transactions:
        raise ValueError("relay export contains no transactions")
    if not SHA256_RE.fullmatch(artifact_sha256):
        raise ValueError("artifact_sha256 must be a SHA-256 digest")

    export_sha256 = hashlib.sha256(raw_bytes).hexdigest()
    derived_root = output_root / "captures" / "derived"
    derived_root.mkdir(parents=True, exist_ok=True)
    imported: list[dict[str, Any]] = []

    for transaction in transactions:
        tx = _required_mapping(transaction, "transaction")
        transaction_id = tx.get("transaction_id")
        requested = _required_mapping(tx.get("requested"), "requested")
        verification = _required_mapping(tx.get("verification"), "verification")
        sdk_response = _required_mapping(tx.get("sdk_response"), "sdk_response")
        if tx.get("success") is not True or verification.get("success") is not True:
            raise ValueError(
                f"transaction {transaction_id} is not successfully verified"
            )
        if sdk_response.get("code") != 0:
            raise ValueError(
                f"transaction {transaction_id} has a non-zero SDK response"
            )
        marker = json.dumps(requested, sort_keys=True, separators=(",", ":"))
        capture = {
            "schema_version": 1,
            "evidence_type": CAPTURE_TYPE,
            "timestamp_utc": _relay_timestamp(
                tx.get("started_at"), source_timezone
            ),
            "direction": "controller_to_device",
            "endpoint": {
                "transport": "broadlink_sdk_passthrough",
                "target_mac": target_mac,
            },
            "action": {
                "marker": marker,
                "purpose": "command_request",
                "requested_state": requested,
            },
            "frame_hex": tx.get("generated_packet"),
            "source": {
                "artifact": artifact,
                "artifact_sha256": artifact_sha256.lower(),
                "tool": "York TFIAC Relay v2 GET /transactions",
                "hook_point": (
                    "generated_packet after setSplitAirconInfo and before "
                    "requestDispatch(buildPassthrough)"
                ),
                "relay_transaction": {
                    "relay_export": export_path.name,
                    "relay_export_sha256": export_sha256,
                    "transaction_id": transaction_id,
                    "finished_at_local": tx.get("finished_at"),
                    "duration_ms": tx.get("duration_ms"),
                    "before": tx.get("before"),
                    "target": tx.get("target"),
                    "after": tx.get("after"),
                    "sdk_response": sdk_response,
                    "verification": verification,
                },
            },
        }
        capture_path = derived_root / f"relay-transaction-{transaction_id}.json"
        capture_path.write_text(
            json.dumps(capture, indent=2) + "\n", encoding="utf-8"
        )
        imported.append(import_native_capture(capture_path, output_root))

    report = {
        "status": "IMPORTED_RELAY_TRANSACTIONS_OBSERVED_NON_EXECUTABLE",
        "source_export": export_path.name,
        "source_export_sha256": export_sha256,
        "transaction_count": len(transactions),
        "record_ids": [item["record_id"] for item in imported],
        "packets_transmitted": 0,
        "network_sockets_opened": 0,
        "safe_to_transmit": False,
    }
    report_path = output_root / "reports" / "relay-transactions-import.json"
    report_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    report["report_file"] = str(report_path)
    return report
