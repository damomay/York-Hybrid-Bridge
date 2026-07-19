from pathlib import Path
import sys

import requests
import yaml

CONFIG = Path("/config/config.yml")

try:
    data = yaml.safe_load(CONFIG.read_text(encoding="utf-8")) or {}
    base_url = str(data["relay"]["base_url"]).rstrip("/")
    timeout = min(float(data["relay"].get("timeout_seconds", 10)), 5.0)
    response = requests.get(f"{base_url}/health", timeout=timeout)
    response.raise_for_status()
except Exception as error:
    print(f"Unhealthy: {error}", file=sys.stderr)
    raise SystemExit(1)

print("Healthy")
