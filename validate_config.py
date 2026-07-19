from pathlib import Path
import sys
import yaml

path = Path("/config/config.yml")
if not path.exists():
    print(f"Missing config file: {path}", file=sys.stderr)
    raise SystemExit(2)

data = yaml.safe_load(path.read_text())
required = [
    ("relay", "base_url"),
    ("mqtt", "host"),
    ("mqtt", "port"),
    ("device", "name"),
    ("device", "unique_id"),
]
missing = [f"{a}.{b}" for a, b in required if not data.get(a, {}).get(b)]
if missing:
    print("Missing required settings: " + ", ".join(missing), file=sys.stderr)
    raise SystemExit(2)

print("Configuration looks valid.")
