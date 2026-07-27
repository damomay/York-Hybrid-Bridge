"""Fail-fast release/package verification for Climate Bridge."""

from __future__ import annotations

from pathlib import Path

from version import APP_VERSION


ROOT = Path(__file__).resolve().parent
REQUIRED = [
    "VERSION",
    "Dockerfile",
    "docker-compose.yml",
    "bridge.py",
    "configuration.py",
    "transport/__init__.py",
    "transport/factory.py",
    "adapters/__init__.py",
    "adapters/york/__init__.py",
    "york_capture_probe.py",
    "transport/tx_logger.py",
    "york_replay_engine.py",
    "york_request_hunter.py",
    "protocols/york/analysis/__init__.py",
    "protocols/york/analysis/loader.py",
    "protocols/york/analysis/scoring.py",
    "tests/test_sprint_282_phase2_request_hunter.py",
    "tests/test_sprint_282_tx_instrumentation.py",
    "york_capture_importer.py",
    "york_protocol_lab.py",
    "protocols/york/lab_dashboard.py",
    "protocols/york/dashboard/README.md",
    "protocols/york/qualification-reports/README.md",
    "qualification-reports/README.md",
    "protocols/york/capture_importer.py",
    "tests/test_sprint_251_capture_importer.py",
    "protocols/york/README.md",
    "protocols/york/packet_library/template.json",
    "protocols/york/packet_library.py",
    "tests/test_sprint_25_packet_library.py",
    "protocols/york/documentation/observations.md",
    "protocols/york/qualification/decoder_fixtures.json",
    "york_decoder_qualification.py",
    "tests/test_sprint_26_decoder_qualification.py",
]


def main() -> int:
    missing = [item for item in REQUIRED if not (ROOT / item).exists()]
    if missing:
        raise SystemExit("Missing release files: " + ", ".join(missing))

    version_file = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
    if version_file != APP_VERSION:
        raise SystemExit("VERSION does not match version.py")

    dockerfile = (ROOT / "Dockerfile").read_text(encoding="utf-8")
    if "COPY VERSION version.py" not in dockerfile:
        raise SystemExit("Dockerfile must package the canonical VERSION file")

    copy_sources = []
    for line in dockerfile.splitlines():
        stripped = line.strip()
        if not stripped.startswith("COPY "):
            continue
        parts = stripped.split()
        for source in parts[1:-1]:
            if not source.startswith("--"):
                copy_sources.append(source)
    missing_copy_sources = [
        source for source in copy_sources if not (ROOT / source).exists()
    ]
    if missing_copy_sources:
        raise SystemExit(
            "Dockerfile COPY sources missing: " + ", ".join(missing_copy_sources)
        )

    compose = (ROOT / "docker-compose.yml").read_text(encoding="utf-8")
    if "source: ./qualification-reports" not in compose:
        raise SystemExit(
            "docker-compose.yml must mount ./qualification-reports"
        )
    if not (ROOT / "qualification-reports").is_dir():
        raise SystemExit("Missing root qualification-reports directory")

    print(f"Release verification passed for Climate Bridge {APP_VERSION}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
