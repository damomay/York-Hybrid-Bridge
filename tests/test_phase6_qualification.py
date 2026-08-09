from __future__ import annotations

import os
from pathlib import Path
import signal
import subprocess
import sys
import time
from unittest.mock import patch

from container_qualification import qualification_snapshot


ROOT = Path(__file__).resolve().parents[1]


def test_qualification_does_not_replace_normal_container_startup():
    dockerfile = (ROOT / "Dockerfile").read_text(encoding="utf-8")
    workflow = (
        ROOT / ".github" / "workflows" / "qualification.yml"
    ).read_text(encoding="utf-8")

    assert (
        'python /app/validate_config.py && exec python /app/bridge.py /config/config.yml'
    ) in dockerfile
    assert "python /app/container_qualification.py /config/config.yml" in workflow
    assert "container_qualification.py" in dockerfile
    assert "COPY VERSION version.py" in dockerfile
    assert "network-free qualification container" in workflow.lower()


def test_container_qualification_is_network_free():
    with patch(
        "socket.socket",
        side_effect=AssertionError("qualification must not open a socket"),
    ):
        snapshot = qualification_snapshot(ROOT / "config.example.yml")

    assert snapshot["application"] == "Climate Bridge"
    assert snapshot["version"] == "1.0.0"
    assert snapshot["transport"] == "native"
    assert snapshot["direct_enabled"] is True
    assert snapshot["network"] == "disabled"
    assert snapshot["dependencies"] == {
        "paho-mqtt": "2.1.0",
        "PyYAML": "6.0.2",
        "cryptography": "46.0.3",
        "tzdata": "2025.2",
    }


def test_container_qualification_stops_cleanly(tmp_path: Path):
    ready = tmp_path / "ready"
    heartbeat = tmp_path / "heartbeat"
    environment = {
        "CLIMATE_BRIDGE_QUALIFICATION_READY_FILE": str(ready),
        "CLIMATE_BRIDGE_QUALIFICATION_HEARTBEAT_FILE": str(heartbeat),
    }
    creationflags = subprocess.CREATE_NEW_PROCESS_GROUP if os.name == "nt" else 0
    process = subprocess.Popen(
        [
            sys.executable,
            str(ROOT / "container_qualification.py"),
            str(ROOT / "config.example.yml"),
        ],
        cwd=ROOT,
        env={**os.environ, **environment},
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        creationflags=creationflags,
    )
    try:
        deadline = time.monotonic() + 5
        while not ready.exists() and time.monotonic() < deadline:
            time.sleep(0.05)
        assert ready.is_file()
        if os.name == "nt":
            # Windows does not provide the Linux container's SIGTERM semantics.
            process.terminate()
            output, _ = process.communicate(timeout=5)
        else:
            process.send_signal(signal.SIGTERM)
            output, _ = process.communicate(timeout=5)
    finally:
        if process.poll() is None:
            process.kill()
            process.wait(timeout=5)

    if os.name != "nt":
        assert process.returncode == 0
    assert "network disabled" in output
    assert "Container qualification ready" in output
    if os.name != "nt":
        assert "Container qualification shutdown complete" in output
        assert not ready.exists()
        assert not heartbeat.exists()
