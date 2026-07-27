#!/usr/bin/env python3
"""Command-line York Protocol Explorer capture importer."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from protocols.york.capture_importer import import_captures


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(
        description="Import York Protocol Explorer text logs as observed, non-executable evidence."
    )
    result.add_argument("inputs", nargs="+", type=Path, help="Capture .txt/.log/.docx files or directories")
    result.add_argument(
        "--protocol-root",
        type=Path,
        default=Path(__file__).resolve().parent / "protocols" / "york",
        help="York protocol reference directory",
    )
    result.add_argument("--no-copy", action="store_true", help="Do not copy source captures into the reference")
    result.add_argument("--copy-raw", action="store_true", help="Copy original unredacted source files (contains device credentials)")
    return result


def main() -> int:
    args = parser().parse_args()
    try:
        report = import_captures(args.inputs, args.protocol_root, copy_sources=not args.no_copy, copy_raw_sources=args.copy_raw)
    except (OSError, ValueError) as error:
        print(f"Import failed: {error}")
        return 2
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
