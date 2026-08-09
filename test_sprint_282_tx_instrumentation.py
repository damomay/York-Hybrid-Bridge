import hashlib
import json
from pathlib import Path

from transport.tx_logger import TransmissionLogger


def test_logger_preserves_exact_payload_and_writes_reports(tmp_path: Path):
    payload = bytes.fromhex("BB 00 01 04")
    logger = TransmissionLogger(tmp_path)
    record, json_path, md_path = logger.record(
        payload=payload,
        destination_host="192.0.2.1",
        destination_port=7777,
        protocol="York TFIAC",
        transport="udp",
        verified=True,
        metadata={"request_record_id": "fixture"},
    )

    assert payload == bytes.fromhex("BB 00 01 04")
    assert record.payload_hex == "BB 00 01 04"
    assert record.payload_length == 4
    assert record.payload_sha256 == hashlib.sha256(payload).hexdigest()
    assert record.transport == "UDP"
    assert json_path.exists()
    assert md_path.exists()

    saved = json.loads(json_path.read_text())
    assert saved["payload_hex"] == "BB 00 01 04"
    assert saved["destination_host"] == "192.0.2.1"
    assert saved["destination_port"] == 7777


def test_logger_generates_unique_correlation_ids(tmp_path: Path):
    logger = TransmissionLogger(tmp_path)
    first, *_ = logger.record(
        payload=b"a", destination_host="127.0.0.1", destination_port=1,
        protocol="test", transport="udp", verified=False,
    )
    second, *_ = logger.record(
        payload=b"b", destination_host="127.0.0.1", destination_port=1,
        protocol="test", transport="udp", verified=False,
    )
    assert first.tx_id == "TX-000001"
    assert second.tx_id == "TX-000002"


def test_dockerfile_packages_tx_logger():
    dockerfile = Path("Dockerfile").read_text()
    assert "COPY transport ./transport" in dockerfile
