"""Container health check for the bridge process, heartbeat and relay path."""

from __future__ import annotations

from pathlib import Path
import sys
import time

import requests
import yaml


CONFIG = Path("/config/config.yml")
READY_FILE = Path("/tmp/climate_bridge.ready")
HEARTBEAT_FILE = Path("/tmp/climate_bridge.heartbeat")
MAX_HEARTBEAT_AGE_SECONDS = 120.0


def _pid1_is_bridge() -> bool:
    try:
        command = (
            Path("/proc/1/cmdline")
            .read_bytes()
            .replace(b"\x00", b" ")
            .decode("utf-8", "replace")
        )
    except OSError:
        return False
    return "python" in command and "/app/bridge.py" in command


def _check_relay(data: dict) -> None:
    transport = data.get("transport") or data.get("relay") or {}
    transport_type = str(transport.get("type", "relay")).strip().lower()
    if transport_type not in {"relay", "tablet_relay"}:
        return
    base_url = str(transport["base_url"]).rstrip("/")
    timeout = min(float(transport.get("timeout_seconds", 10)), 5.0)
    response = requests.get(f"{base_url}/health", timeout=timeout)
    response.raise_for_status()


def main() -> int:
    try:
        if not _pid1_is_bridge():
            raise RuntimeError("bridge process is not PID 1")
        if not READY_FILE.is_file():
            raise RuntimeError("bridge has not reached READY")
        if not HEARTBEAT_FILE.is_file():
            raise RuntimeError("event-loop heartbeat is missing")
        age = time.time() - HEARTBEAT_FILE.stat().st_mtime
        if age > MAX_HEARTBEAT_AGE_SECONDS:
            raise RuntimeError(f"event-loop heartbeat is {age:.0f}s old")

        data = yaml.safe_load(CONFIG.read_text(encoding="utf-8")) or {}
        if not isinstance(data, dict):
            raise RuntimeError("configuration root is not a mapping")
        _check_relay(data)
    except Exception as error:
        print(f"Unhealthy: {error}", file=sys.stderr)
        return 1

    print(f"Healthy: bridge ready; heartbeat age {age:.0f}s")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
