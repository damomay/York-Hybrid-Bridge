"""Static repository checks for the Phase 6 qualification gate."""

from __future__ import annotations

import json
from pathlib import Path
import re
import subprocess
import sys

import yaml


ROOT = Path(__file__).resolve().parent
GENERATED_PARTS = {"__pycache__", ".pytest_cache", ".ruff_cache"}
GENERATED_SUFFIXES = {".pyc", ".pyo", ".log", ".pcap", ".pcapng", ".cap"}
TEXT_SUFFIXES = {
    "",
    ".cfg",
    ".env",
    ".ini",
    ".json",
    ".md",
    ".py",
    ".txt",
    ".yaml",
    ".yml",
}
PRIVATE_IPV4 = re.compile(
    r"(?<!\d)(?:"
    r"10(?:\.\d{1,3}){3}|"
    r"192\.168(?:\.\d{1,3}){2}|"
    r"172\.(?:1[6-9]|2\d|3[01])(?:\.\d{1,3}){2}"
    r")(?!\d)"
)
PERSONAL_PATHS = (
    re.compile(r"(?i)\b[A-Z]:\\Users\\[^\\\s]+"),
    re.compile(r"(?<!\w)/(?:home|Users)/[^/\s]+"),
    re.compile(r"(?<!\w)/work" r"space/scratch/[^/\s]+"),
)
TOKEN_PATTERNS = (
    re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
    re.compile(r"\bgh[opsu]_[A-Za-z0-9]{30,}\b"),
    re.compile(r"\bxox[baprs]-[A-Za-z0-9-]{10,}\b"),
    re.compile(r"\bAIza[0-9A-Za-z_-]{30,}\b"),
    re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
)
MAC_ADDRESS = re.compile(
    r"(?<![0-9A-Fa-f])"
    r"(?P<address>(?:[0-9A-Fa-f]{2}:){5}[0-9A-Fa-f]{2})"
    r"(?![0-9A-Fa-f])"
)


def tracked_files() -> list[Path]:
    """Return tracked files relative to the repository root."""
    result = subprocess.run(
        ["git", "ls-files", "-z"],
        cwd=ROOT,
        check=True,
        capture_output=True,
    )
    return [
        Path(item.decode("utf-8"))
        for item in result.stdout.split(b"\0")
        if item
    ]


def validate_paths(paths: list[Path]) -> list[str]:
    """Reject tracked caches, compiled files and generated runtime output."""
    errors = []
    for path in paths:
        if GENERATED_PARTS.intersection(path.parts):
            errors.append(f"generated directory is tracked: {path}")
        if path.suffix.lower() in GENERATED_SUFFIXES:
            errors.append(f"generated file is tracked: {path}")
        if (
            "qualification-reports" in path.parts
            and path.name not in {"README.md", ".gitkeep"}
        ):
            errors.append(f"generated qualification report is tracked: {path}")
    return errors


def _is_example_mac(address: str) -> bool:
    """Accept locally administered fixture MACs, reject device MACs."""
    first_octet = int(address.split(":", 1)[0], 16)
    return bool(first_octet & 0x02)


def validate_text(paths: list[Path]) -> list[str]:
    """Scan tracked text for private addresses, paths and credential forms."""
    errors = []
    for path in paths:
        if path.suffix.lower() not in TEXT_SUFFIXES:
            continue
        try:
            text = (ROOT / path).read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        if PRIVATE_IPV4.search(text):
            errors.append(f"private IPv4 address found: {path}")
        if any(pattern.search(text) for pattern in PERSONAL_PATHS):
            errors.append(f"personal filesystem path found: {path}")
        if any(pattern.search(text) for pattern in TOKEN_PATTERNS):
            errors.append(f"credential or private-key signature found: {path}")
        for match in MAC_ADDRESS.finditer(text):
            if not _is_example_mac(match.group("address")):
                errors.append(f"device MAC address found: {path}")
                break
    return errors


def validate_manifests(paths: list[Path]) -> list[str]:
    """Parse tracked JSON/YAML metadata and configuration files."""
    errors = []
    for path in paths:
        suffix = path.suffix.lower()
        if suffix not in {".json", ".yaml", ".yml"}:
            continue
        try:
            text = (ROOT / path).read_text(encoding="utf-8")
            if suffix == ".json":
                json.loads(text)
            else:
                yaml.safe_load(text)
        except (OSError, ValueError, yaml.YAMLError) as error:
            errors.append(f"invalid manifest {path}: {error}")
    return errors


def main() -> int:
    paths = tracked_files()
    errors = [
        *validate_paths(paths),
        *validate_text(paths),
        *validate_manifests(paths),
    ]
    if errors:
        for error in errors:
            print(error, file=sys.stderr)
        return 1
    print(
        f"Phase 6 tracked-tree gate passed: {len(paths)} files; "
        "manifests parsed; no generated or sensitive material detected."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
