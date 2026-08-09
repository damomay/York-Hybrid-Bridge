"""Network-free container startup and shutdown qualification.

This module is not part of normal Climate Bridge startup. Phase 6 CI
overrides the image command explicitly so packaging can be exercised without
contacting MQTT, the Android relay, or an HVAC device.
"""

from __future__ import annotations

import argparse
import importlib
import importlib.metadata
import json
import os
from pathlib import Path
import platform
import signal
import sys
import threading
import time

from configuration import load_config
from version import APP_NAME, APP_VERSION


READY_FILE = Path(
    os.environ.get(
        "CLIMATE_BRIDGE_QUALIFICATION_READY_FILE",
        "/tmp/climate_bridge_qualification.ready",
    )
)
HEARTBEAT_FILE = Path(
    os.environ.get(
        "CLIMATE_BRIDGE_QUALIFICATION_HEARTBEAT_FILE",
        "/tmp/climate_bridge_qualification.heartbeat",
    )
)
MAX_HEARTBEAT_AGE_SECONDS = 10.0
REQUIRED_MODULES = (
    "bridge",
    "configuration",
    "diagnostics_manager",
    "discovery_manager",
    "health_manager",
    "mqtt_manager",
    "recovery_manager",
    "transport",
    "adapters.york",
    "protocols.york",
)
DEPENDENCIES = ("paho-mqtt", "PyYAML", "cryptography", "tzdata")


def qualification_snapshot(config_path: Path) -> dict[str, object]:
    """Validate packaged imports and configuration without opening sockets."""
    config = load_config(config_path)
    imported = []
    for module_name in REQUIRED_MODULES:
        importlib.import_module(module_name)
        imported.append(module_name)

    dependencies = {
        name: importlib.metadata.version(name)
        for name in DEPENDENCIES
    }
    return {
        "application": APP_NAME,
        "version": APP_VERSION,
        "python": platform.python_version(),
        "transport": config.transport_type,
        "direct_enabled": config.direct_enabled,
        "modules": imported,
        "dependencies": dependencies,
        "network": "disabled",
    }


def healthcheck() -> int:
    """Return success only while the qualification process is responsive."""
    if not READY_FILE.is_file():
        print("Unhealthy: qualification readiness marker is missing", file=sys.stderr)
        return 1
    if not HEARTBEAT_FILE.is_file():
        print("Unhealthy: qualification heartbeat is missing", file=sys.stderr)
        return 1
    age = time.time() - HEARTBEAT_FILE.stat().st_mtime
    if age > MAX_HEARTBEAT_AGE_SECONDS:
        print(
            f"Unhealthy: qualification heartbeat is {age:.1f}s old",
            file=sys.stderr,
        )
        return 1
    print(f"Healthy: network-free qualification; heartbeat age {age:.1f}s")
    return 0


def run(config_path: Path) -> int:
    """Run until SIGTERM/SIGINT and then remove all qualification markers."""
    stop_event = threading.Event()

    def shutdown(signum: int, frame: object) -> None:
        del frame
        print(f"Qualification shutdown requested by signal {signum}", flush=True)
        stop_event.set()

    signal.signal(signal.SIGTERM, shutdown)
    signal.signal(signal.SIGINT, shutdown)

    READY_FILE.unlink(missing_ok=True)
    HEARTBEAT_FILE.unlink(missing_ok=True)
    snapshot = qualification_snapshot(config_path)
    print(json.dumps(snapshot, sort_keys=True), flush=True)
    print(
        "Qualification mode is network disabled; no MQTT or HVAC "
        "connection will be attempted.",
        flush=True,
    )
    HEARTBEAT_FILE.touch()
    READY_FILE.touch()
    print("Container qualification ready", flush=True)

    try:
        while not stop_event.wait(1.0):
            HEARTBEAT_FILE.touch()
    finally:
        READY_FILE.unlink(missing_ok=True)
        HEARTBEAT_FILE.unlink(missing_ok=True)
        print("Container qualification shutdown complete", flush=True)
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "config",
        nargs="?",
        type=Path,
        default=Path("/config/config.yml"),
    )
    parser.add_argument(
        "--healthcheck",
        action="store_true",
        help="Check the qualification readiness and heartbeat markers.",
    )
    args = parser.parse_args()
    if args.healthcheck:
        return healthcheck()
    return run(args.config)


if __name__ == "__main__":
    raise SystemExit(main())
