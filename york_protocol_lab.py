#!/usr/bin/env python3
"""Build the York Protocol Lab static dashboard."""
from __future__ import annotations
import argparse
import json
from pathlib import Path
from protocols.york.lab_dashboard import generate_dashboard


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate the York Protocol Lab dashboard")
    parser.add_argument("--protocol-root", type=Path, default=Path(__file__).resolve().parent / "protocols" / "york")
    parser.add_argument("--output", type=Path, default=None)
    args = parser.parse_args()
    result = generate_dashboard(args.protocol_root, args.output)
    print(json.dumps({"dashboard": result["dashboard"], "data": result["data"]}, indent=2))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
