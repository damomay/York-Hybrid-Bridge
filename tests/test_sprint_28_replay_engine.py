from pathlib import Path

from protocols.york.packet_library import load_packet_record
from protocols.york.xml_broadcast import parse_xml_payload


def test_status_update_xml_is_decoded():
    payload = (
        b'<msg msgid="statusUpdateMsg" type="Notify" seq="1234">'
        b'<statusUpdateMsg><BaseMode>heat</BaseMode><TurnOn>on</TurnOn>'
        b'<SetTemp>77</SetTemp><WindSpeed>Auto</WindSpeed>'
        b'<IndoorTemp>73</IndoorTemp></statusUpdateMsg></msg>'
    )
    message = parse_xml_payload(payload, ("192.0.2.30", 7777))
    assert message.message_id == "statusUpdateMsg"
    assert message.state["mode"] == "heat"
    assert message.state["power"] is True
    assert message.state["temperature_f"] == 77.0
    assert message.state["temperature"] == 25.0
    assert message.state["current_temperature"] == 22.8
    assert message.state["fan"] == "auto"


def test_packet_record_loads_expected_state(tmp_path: Path):
    record = tmp_path / "request.json"
    record.write_text('''{
      "id": "test-request",
      "purpose": "state_request",
      "direction": "controller_to_device",
      "frame_hex": "BB 00 01 04",
      "expected_state": {"power": true, "mode": "heat"},
      "verification": {"status": "verified"}
    }''')
    loaded = load_packet_record(record)
    assert loaded.executable is True
    assert loaded.expected_state == {"power": True, "mode": "heat"}


def test_dockerfile_packages_replay_engine():
    dockerfile = Path("Dockerfile").read_text()
    assert "york_replay_engine.py" in dockerfile
