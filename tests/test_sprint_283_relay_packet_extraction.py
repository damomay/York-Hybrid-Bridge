import json
from pathlib import Path
from unittest.mock import Mock

from transport.relay_extraction_logger import RelayExtractionLogger


def test_canonical_payload_is_stable():
    payload = RelayExtractionLogger.canonical_payload({"temperature": 24, "mode": "heat"})
    assert payload == b'{"mode":"heat","temperature":24}'


def test_logger_writes_json_and_markdown(tmp_path: Path):
    logger = RelayExtractionLogger(tmp_path)
    record = logger.pending(
        correlation_id="RELAY-TX-TEST-0001",
        endpoint="http://192.0.2.44:8765/command",
        payload={"temperature": 24},
    )
    json_path, md_path = logger.complete(
        record,
        response_status=200,
        response_json={"ok": True},
        response_text='{"ok":true}',
        elapsed_ms=12,
        result="success",
    )
    assert json_path.exists()
    assert md_path.exists()
    assert "native York packet" in md_path.read_text()
    data = json.loads(json_path.read_text())
    assert data["evidence_type"] == "android_relay_http_json"
    assert data["native_york_packet_extracted"] is False
