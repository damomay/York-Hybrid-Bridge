#!/usr/bin/env python3
"""Summarise relay command extraction records without transmitting anything."""
from __future__ import annotations

import argparse
import json
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(description="Summarise Climate Bridge relay command extraction records")
    parser.add_argument("--input-dir", default="/reports/relay-extraction")
    args = parser.parse_args()
    root = Path(args.input_dir)
    files = sorted(root.glob("RELAY-TX-*.json")) if root.exists() else []
    print("Climate Bridge Relay Extraction Report 1.0.0")
    print(f"Records: {len(files)}")
    if not files:
        print("Result: NO_RELAY_COMMAND_RECORDS")
        print("Use Home Assistant to issue one harmless command through Relay (Legacy), then rerun.")
        return 0
    for path in files[-20:]:
        data = json.loads(path.read_text(encoding="utf-8"))
        print(
            f"{data['correlation_id']} | {data['result']} | "
            f"{data['request_json']} | HTTP {data['response_status']} | "
            f"{data['elapsed_ms']} ms"
        )
    print(f"Reports: {root}")
    print("Important: these are HTTP relay commands, not yet native York packet bytes.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
