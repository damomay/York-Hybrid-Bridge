"""Transport-agnostic transmission audit logging.

The logger records the exact payload presented to a transport immediately before
send. It never mutates the payload and performs no network activity itself.
"""
from __future__ import annotations

import hashlib
import json
import threading
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class TransmissionRecord:
    tx_id: str
    timestamp_utc: str
    protocol: str
    transport: str
    destination_host: str
    destination_port: int
    payload_length: int
    payload_hex: str
    payload_sha256: str
    verified: bool
    metadata: dict[str, Any]


class TransmissionLogger:
    """Create durable JSON and Markdown records for outbound payloads."""

    def __init__(self, output_dir: Path | str = "/reports/transmissions") -> None:
        self.output_dir = Path(output_dir)
        self._lock = threading.Lock()
        self._counter = 0

    def _next_id(self) -> str:
        with self._lock:
            self._counter += 1
            return f"TX-{self._counter:06d}"

    def record(
        self,
        *,
        payload: bytes,
        destination_host: str,
        destination_port: int,
        protocol: str,
        transport: str,
        verified: bool,
        metadata: dict[str, Any] | None = None,
    ) -> tuple[TransmissionRecord, Path, Path]:
        """Record payload bytes without altering them.

        Returns the immutable record plus the JSON and Markdown paths.
        """
        if not isinstance(payload, bytes):
            raise TypeError("payload must be bytes")
        if not payload:
            raise ValueError("payload must not be empty")

        now = datetime.now(timezone.utc)
        tx_id = self._next_id()
        record = TransmissionRecord(
            tx_id=tx_id,
            timestamp_utc=now.isoformat(),
            protocol=protocol,
            transport=transport.upper(),
            destination_host=destination_host,
            destination_port=int(destination_port),
            payload_length=len(payload),
            payload_hex=payload.hex(" ").upper(),
            payload_sha256=hashlib.sha256(payload).hexdigest(),
            verified=bool(verified),
            metadata=dict(metadata or {}),
        )

        self.output_dir.mkdir(parents=True, exist_ok=True)
        stamp = now.strftime("%Y%m%dT%H%M%S.%fZ")
        stem = f"{stamp}-{tx_id}"
        json_path = self.output_dir / f"{stem}.json"
        md_path = self.output_dir / f"{stem}.md"

        json_path.write_text(json.dumps(asdict(record), indent=2) + "\n", encoding="utf-8")
        md_path.write_text(self._to_markdown(record), encoding="utf-8")
        return record, json_path, md_path

    @staticmethod
    def _to_markdown(record: TransmissionRecord) -> str:
        metadata = "\n".join(
            f"- **{key}:** `{value}`" for key, value in sorted(record.metadata.items())
        ) or "- None"
        return (
            "# Climate Bridge Transmission Record\n\n"
            f"- **TX ID:** `{record.tx_id}`\n"
            f"- **Timestamp (UTC):** `{record.timestamp_utc}`\n"
            f"- **Protocol:** `{record.protocol}`\n"
            f"- **Transport:** `{record.transport}`\n"
            f"- **Destination:** `{record.destination_host}:{record.destination_port}`\n"
            f"- **Length:** `{record.payload_length}` bytes\n"
            f"- **Verified source:** `{record.verified}`\n"
            f"- **SHA-256:** `{record.payload_sha256}`\n\n"
            "## Payload\n\n"
            f"```text\n{record.payload_hex}\n```\n\n"
            "## Metadata\n\n"
            f"{metadata}\n"
        )
