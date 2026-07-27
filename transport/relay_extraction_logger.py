"""Persistent instrumentation for commands sent to the legacy Android relay.

This logger records the exact HTTP JSON payload Climate Bridge submits to the
relay and the relay's HTTP response. It deliberately does not claim to expose
the relay's internal native York packet; that packet is constructed inside the
Android application and requires instrumentation at that layer.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import threading
from typing import Any


@dataclass(frozen=True)
class RelayExtractionRecord:
    correlation_id: str
    timestamp_utc: str
    method: str
    endpoint: str
    request_content_type: str
    request_length: int
    request_json: dict[str, Any]
    request_utf8_hex: str
    request_sha256: str
    evidence_type: str = "android_relay_http_json"
    native_york_packet_extracted: bool = False
    response_status: int | None = None
    response_json: Any = None
    response_text: str = ""
    response_length: int = 0
    elapsed_ms: int | None = None
    result: str = "pending"
    note: str = (
        "This record captures the Climate Bridge HTTP exchange with the Android "
        "relay. It is not proof of the native York packet generated inside Android."
    )


class RelayExtractionLogger:
    """Write one JSON and one Markdown artifact for each relay command."""

    def __init__(self, output_dir: str | Path = "/reports/relay-extraction") -> None:
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self._lock = threading.Lock()
        self._counter = 0

    def next_id(self) -> str:
        with self._lock:
            self._counter += 1
            stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
            return f"RELAY-TX-{stamp}-{self._counter:04d}"

    @staticmethod
    def canonical_payload(payload: dict[str, Any]) -> bytes:
        return json.dumps(
            payload,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
        ).encode("utf-8")

    def pending(
        self,
        *,
        correlation_id: str,
        endpoint: str,
        payload: dict[str, Any],
    ) -> RelayExtractionRecord:
        raw = self.canonical_payload(payload)
        return RelayExtractionRecord(
            correlation_id=correlation_id,
            timestamp_utc=datetime.now(timezone.utc).isoformat(),
            method="POST",
            endpoint=endpoint,
            request_content_type="application/json",
            request_length=len(raw),
            request_json=payload,
            request_utf8_hex=raw.hex(" ").upper(),
            request_sha256=hashlib.sha256(raw).hexdigest(),
        )

    def complete(
        self,
        record: RelayExtractionRecord,
        *,
        response_status: int | None,
        response_json: Any,
        response_text: str,
        elapsed_ms: int | None,
        result: str,
    ) -> tuple[Path, Path]:
        completed = RelayExtractionRecord(
            **{
                **asdict(record),
                "response_status": response_status,
                "response_json": response_json,
                "response_text": response_text,
                "response_length": len(response_text.encode("utf-8")),
                "elapsed_ms": elapsed_ms,
                "result": result,
            }
        )
        return self.write(completed)

    def write(self, record: RelayExtractionRecord) -> tuple[Path, Path]:
        json_path = self.output_dir / f"{record.correlation_id}.json"
        md_path = self.output_dir / f"{record.correlation_id}.md"
        data = asdict(record)
        json_path.write_text(json.dumps(data, indent=2), encoding="utf-8")

        response_json = (
            json.dumps(record.response_json, indent=2, ensure_ascii=False)
            if record.response_json is not None
            else "Not available"
        )
        md = f"""# Climate Bridge Relay Command Extraction

- Correlation ID: `{record.correlation_id}`
- Timestamp: `{record.timestamp_utc}`
- Result: **{record.result}**
- Endpoint: `{record.endpoint}`
- Request length: `{record.request_length}` bytes
- Request SHA-256: `{record.request_sha256}`
- HTTP status: `{record.response_status}`
- Elapsed: `{record.elapsed_ms}` ms

## Request JSON

```json
{json.dumps(record.request_json, indent=2, ensure_ascii=False)}
```

## Exact UTF-8 request bytes

```text
{record.request_utf8_hex}
```

## Relay response JSON

```json
{response_json}
```

## Important limitation

{record.note}
"""
        md_path.write_text(md, encoding="utf-8")
        return json_path, md_path
