#!/usr/bin/env python3
"""Import one structured Android York request capture without transmitting it."""
from __future__ import annotations

import argparse
from pathlib import Path

from protocols.york.native_capture import (
    import_native_capture,
    import_relay_transactions,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Import a complete Android controller-to-device capture as "
            "observed, non-executable York evidence."
        )
    )
    parser.add_argument("capture", type=Path)
    parser.add_argument(
        "--relay-export",
        action="store_true",
        help="Import a York TFIAC Relay v2 /transactions JSON export.",
    )
    parser.add_argument("--artifact", help="Recovered relay source artifact name.")
    parser.add_argument("--artifact-sha256", help="Recovered source SHA-256.")
    parser.add_argument("--target-mac", help="Relay target York MAC address.")
    parser.add_argument(
        "--source-timezone",
        help="IANA timezone used by the relay's timezone-naive timestamps.",
    )
    parser.add_argument(
        "--output-root",
        type=Path,
        default=Path("/reports/york-native-evidence"),
        help="Private evidence root; keep raw device captures out of Git.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.relay_export:
        required = {
            "--artifact": args.artifact,
            "--artifact-sha256": args.artifact_sha256,
            "--target-mac": args.target_mac,
            "--source-timezone": args.source_timezone,
        }
        missing = [name for name, value in required.items() if not value]
        if missing:
            raise SystemExit(
                "Relay export import requires " + ", ".join(missing)
            )
        report = import_relay_transactions(
            args.capture,
            args.output_root,
            artifact=args.artifact,
            artifact_sha256=args.artifact_sha256,
            target_mac=args.target_mac,
            source_timezone=args.source_timezone,
        )
    else:
        report = import_native_capture(args.capture, args.output_root)
    print(f"Result: {report['status']}")
    if "record_id" in report:
        print(f"Record: {report['record_id']}")
    else:
        print(f"Records: {report['transaction_count']}")
    print(f"Report: {report['report_file']}")
    print("Packets transmitted: 0")
    print("Safe to transmit: false")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
