from __future__ import annotations

import json
import sys
from pathlib import Path

import paho.mqtt.client as mqtt
import yaml


def main() -> int:
    path = Path(sys.argv[1] if len(sys.argv) > 1 else "/config/config.yml")
    raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    mq = raw["mqtt"]
    dev = raw["device"]

    uid = str(dev.get("unique_id", "york_ac2"))
    name = str(dev.get("name", "York AC2"))
    prefix = str(mq.get("discovery_prefix", "homeassistant")).rstrip("/")
    base = str(mq.get("base_topic", "york/ac2")).rstrip("/")

    client = mqtt.Client(
        mqtt.CallbackAPIVersion.VERSION2,
        client_id=f"{uid}-discovery-refresh",
    )
    if mq.get("username"):
        client.username_pw_set(str(mq["username"]), str(mq.get("password", "")))

    client.connect(str(mq["host"]), int(mq.get("port", 1883)), 60)
    client.loop_start()

    device = {
        "identifiers": [uid],
        "name": name,
        "manufacturer": "York / TCL",
        "model": "YHKE12XEAATA-RX / TFIAC type 20014",
    }
    diagnostics = {
        "last_command": "Last command",
        "last_command_result": "Last command result",
        "last_command_duration": "Last command duration",
        "last_transaction_id": "Last transaction ID",
        "relay_status": "Relay status",
        "last_state_update": "Last state update",
    }

    for key, label in diagnostics.items():
        payload = {
            "name": label,
            "unique_id": f"{uid}_{key}",
            "state_topic": f"{base}/diagnostic/{key}",
            "availability_topic": f"{base}/availability",
            "entity_category": "diagnostic",
            "device": device,
        }
        if key == "last_command_duration":
            payload["unit_of_measurement"] = "ms"
        if key == "last_state_update":
            payload["device_class"] = "timestamp"

        topic = f"{prefix}/sensor/{uid}_{key}/config"
        result = client.publish(topic, json.dumps(payload), retain=True)
        result.wait_for_publish()
        print(f"Published {topic}")

    client.loop_stop()
    client.disconnect()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
