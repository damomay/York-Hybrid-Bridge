"""Validated access to York protocol-reference packet records."""
from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

from adapters.york.errors import YorkFrameError, YorkProtocolNotReady

_HEX_CLEAN_RE = re.compile(r"[^0-9a-fA-F]")
_ALLOWED_STATUS = {"unverified", "observed", "verified", "rejected"}


@dataclass(frozen=True)
class YorkPacketRecord:
    record_id: str
    purpose: str
    direction: str
    status: str
    frame: bytes
    source: str
    safe_to_transmit: bool = False
    replay_count: int = 0
    successful_responses: int = 0
    notes: str = ""
    expected_state: dict[str, Any] | None = None

    @property
    def frame_hex(self) -> str:
        return self.frame.hex(" ").upper()

    @property
    def executable(self) -> bool:
        return (
            self.status == "verified"
            and self.direction == "request"
            and self.purpose == "state_request"
            and self.safe_to_transmit is True
            and self.replay_count >= 1
            and self.successful_responses >= 1
            and bool(self.source)
        )


def _parse_hex(value: str) -> bytes:
    compact = _HEX_CLEAN_RE.sub("", value or "")
    if not compact:
        raise YorkFrameError("Packet record does not contain frame_hex")
    if len(compact) % 2:
        raise YorkFrameError("Packet record contains an incomplete hex byte")
    frame = bytes.fromhex(compact)
    if len(frame) < 4:
        raise YorkFrameError("Packet record frame is too short")
    if frame[0] != 0xBB:
        raise YorkFrameError("Packet record does not start with the York 0xBB header")
    return frame


def load_packet_record(path: Path) -> YorkPacketRecord:
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise YorkFrameError(f"Unable to read packet record {path}: {error}") from error

    status = str((raw.get("verification") or {}).get("status", raw.get("status", "unverified"))).lower()
    if status not in _ALLOWED_STATUS:
        raise YorkFrameError(f"Unsupported packet status: {status}")

    verification = raw.get("verification") or {}
    if not isinstance(verification, dict):
        raise YorkFrameError("Packet record verification metadata must be an object")

    return YorkPacketRecord(
        record_id=str(raw.get("id", path.stem)).strip(),
        purpose=str(raw.get("purpose", raw.get("kind", ""))).strip().lower(),
        direction=("request" if str(raw.get("direction", "")).strip().lower() == "controller_to_device" else "response" if str(raw.get("direction", "")).strip().lower() == "device_to_controller" else str(raw.get("direction", "")).strip().lower()),
        status=status,
        frame=_parse_hex(str(raw.get("frame_hex", ""))),
        source=(str((raw.get("source") or {}).get("capture_file", "")).strip() if isinstance(raw.get("source"), dict) else str(raw.get("source", "")).strip()),
        safe_to_transmit=verification.get("safe_to_transmit") is True,
        replay_count=int(verification.get("replay_count", 0) or 0),
        successful_responses=int(verification.get("successful_responses", 0) or 0),
        notes=str(raw.get("notes", "")).strip(),
        expected_state=(raw.get("expected_state") if isinstance(raw.get("expected_state"), dict) else {}),
    )


def iter_packet_records(directory: Path) -> Iterable[tuple[Path, YorkPacketRecord]]:
    for path in sorted(directory.glob("*.json")):
        if path.name == "template.json":
            continue
        yield path, load_packet_record(path)


def find_verified_state_request(directory: Path, record_id: str = "") -> YorkPacketRecord:
    matches: list[YorkPacketRecord] = []
    for _, record in iter_packet_records(directory):
        if record_id and record.record_id != record_id:
            continue
        if record.executable:
            matches.append(record)

    if not matches:
        suffix = f" with id '{record_id}'" if record_id else ""
        raise YorkProtocolNotReady(
            "No verified executable York state-request record was found"
            f"{suffix}. Import a complete capture and mark it verified before probing."
        )
    if len(matches) > 1 and not record_id:
        raise YorkProtocolNotReady(
            "More than one verified York state-request record exists; select one by id."
        )
    return matches[0]
