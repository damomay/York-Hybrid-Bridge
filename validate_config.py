from pathlib import Path
import sys

import yaml


path = Path("/config/config.yml")
if not path.exists():
    print(f"Missing config file: {path}", file=sys.stderr)
    raise SystemExit(2)

try:
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
except (OSError, yaml.YAMLError) as exc:
    print(f"Unable to read configuration: {exc}", file=sys.stderr)
    raise SystemExit(2) from exc

if not isinstance(data, dict):
    print("Configuration root must be a YAML mapping.", file=sys.stderr)
    raise SystemExit(2)

transport = data.get("transport") or data.get("relay") or {}
transport_type = str(transport.get("type", "relay")).strip().lower()
missing = []

if transport_type in {"relay", "tablet_relay"}:
    if not transport.get("base_url"):
        missing.append("transport.base_url")
elif transport_type in {"york", "york_direct"}:
    direct = data.get("direct_device") or {}
    if not direct.get("enabled", False):
        missing.append("direct_device.enabled")
    if not direct.get("host"):
        missing.append("direct_device.host")
    if not direct.get("mac"):
        missing.append("direct_device.mac")
    if not direct.get("state_request_hex"):
        missing.append("direct_device.state_request_hex")
else:
    print(f"Unsupported transport.type: {transport_type}", file=sys.stderr)
    raise SystemExit(2)

for section, key in [
    ("mqtt", "host"),
    ("mqtt", "port"),
    ("device", "name"),
    ("device", "unique_id"),
]:
    if not (data.get(section) or {}).get(key):
        missing.append(f"{section}.{key}")

if missing:
    print("Missing required settings: " + ", ".join(missing), file=sys.stderr)
    raise SystemExit(2)

print(f"Configuration looks valid (transport: {transport_type}).")
