import json
from pathlib import Path

import pytest

from adapters.york.errors import YorkProtocolNotReady
from configuration import load_config
from transport.relay_transport import RelayTransport
import york_capture_probe
import york_replay_engine


def write_config(path: Path, *, direct_enabled: bool = False) -> None:
    path.write_text(
        f"""
transport:
  type: relay
  base_url: http://192.0.2.20:8765
direct_device:
  enabled: {str(direct_enabled).lower()}
  host: 192.0.2.30
  mac: 02:00:00:00:00:01
  port: 16384
  state_request_hex: BB 00 00 00
mqtt:
  host: 192.0.2.10
  port: 1883
device:
  name: Test York
  unique_id: test_york
""",
        encoding="utf-8",
    )


def write_record(path: Path, *, status: str = "verified") -> None:
    path.write_text(
        json.dumps(
            {
                "id": "state-request-test",
                "purpose": "state_request",
                "kind": "state_request",
                "direction": "controller_to_device",
                "frame_hex": "BB 00 00 00",
                "source": {
                    "capture_file": "approved-fixture.log",
                    "tool": "test",
                },
                "verification": {
                    "status": status,
                    "replay_count": 1 if status == "verified" else 0,
                    "successful_responses": 1 if status == "verified" else 0,
                    "safe_to_transmit": status == "verified",
                },
            }
        ),
        encoding="utf-8",
    )


def test_default_relay_does_not_activate_extraction_logger(tmp_path: Path):
    config_path = tmp_path / "config.yml"
    write_config(config_path)
    transport = RelayTransport(load_config(config_path))
    assert transport.extraction_logger is None
    transport.close()


def test_probe_requires_config_and_deliberate_confirmation(
    tmp_path: Path,
    monkeypatch,
):
    config_path = tmp_path / "config.yml"
    library = tmp_path / "library"
    library.mkdir()
    write_config(config_path, direct_enabled=True)
    write_record(library / "request.json")

    def reject_connection(*args, **kwargs):
        raise AssertionError("probe opened a connection without confirmation")

    monkeypatch.setattr(york_capture_probe, "YorkConnection", reject_connection)
    monkeypatch.setattr(
        "sys.argv",
        [
            "york_capture_probe.py",
            str(config_path),
            "--packet-library",
            str(library),
        ],
    )
    assert york_capture_probe.main() == 12


def test_probe_validate_only_never_opens_socket(tmp_path: Path, monkeypatch):
    config_path = tmp_path / "config.yml"
    library = tmp_path / "library"
    library.mkdir()
    write_config(config_path, direct_enabled=False)
    write_record(library / "request.json")

    def reject_connection(*args, **kwargs):
        raise AssertionError("validate-only opened a connection")

    monkeypatch.setattr(york_capture_probe, "YorkConnection", reject_connection)
    monkeypatch.setattr(
        "sys.argv",
        [
            "york_capture_probe.py",
            str(config_path),
            "--packet-library",
            str(library),
            "--validate-only",
        ],
    )
    assert york_capture_probe.main() == 0


def test_replay_requires_config_and_deliberate_confirmation(
    tmp_path: Path,
    monkeypatch,
):
    config_path = tmp_path / "config.yml"
    library = tmp_path / "library"
    library.mkdir()
    write_config(config_path, direct_enabled=True)
    write_record(library / "request.json")

    def reject_network(*args, **kwargs):
        raise AssertionError("replay opened network resources without confirmation")

    monkeypatch.setattr(york_replay_engine, "YorkConnection", reject_network)
    monkeypatch.setattr(
        york_replay_engine,
        "YorkXmlBroadcastListener",
        reject_network,
    )
    monkeypatch.setattr(
        "sys.argv",
        [
            "york_replay_engine.py",
            str(config_path),
            "--packet-library",
            str(library),
            "--output-dir",
            str(tmp_path / "reports"),
        ],
    )
    assert york_replay_engine.main() == 12


def test_unqualified_probe_candidate_is_rejected_before_network(
    tmp_path: Path,
    monkeypatch,
):
    config_path = tmp_path / "config.yml"
    library = tmp_path / "library"
    library.mkdir()
    write_config(config_path, direct_enabled=True)
    write_record(library / "request.json", status="observed")

    def reject_connection(*args, **kwargs):
        raise AssertionError("unqualified candidate reached the network")

    monkeypatch.setattr(york_capture_probe, "YorkConnection", reject_connection)
    monkeypatch.setattr(
        "sys.argv",
        [
            "york_capture_probe.py",
            str(config_path),
            "--packet-library",
            str(library),
            "--confirm-transmit",
        ],
    )
    with pytest.raises(YorkProtocolNotReady):
        york_capture_probe.main()
