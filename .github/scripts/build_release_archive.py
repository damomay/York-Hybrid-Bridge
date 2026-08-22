#!/usr/bin/env python3
"""Build and verify a deterministic, sanitized release archive from a Git tree."""

from __future__ import annotations

import argparse
import hashlib
import re
import subprocess
import sys
import zipfile
from dataclasses import dataclass
from pathlib import Path, PurePosixPath


FIXED_TIMESTAMP = (1980, 1, 1, 0, 0, 0)
PROHIBITED = re.compile(
    r"(?:^|/)(?:\.github|\.git|__pycache__|\.pytest_cache|\.ruff_cache|\.mypy_cache|\.cache|cache|caches|node_modules)(?:/|$)|"
    r"(?:^|/)\.env[^/]*$|(?:^|/)[^/]*\.(?:pyc|pyo|pyd|log|zip|tar|tgz|gz|bz2|xz|7z|rar|whl|sha256|sha512|checksum|md5)$|"
    r"^(?:AGENTS\.md|PROJECT_STATUS\.md|ROADMAP\.md|RELEASE_CHECKLIST\.md|CONTRIBUTING\.md|pytest\.ini)$|"
    r"^(?:tests?/|test_[^/]*\.py$|screenshots/|tools/|docs/(?:testing|history|reconciliation|releases|roadmaps|tablet-removal)/|"
    r"qualification-reports/|protocols/york/(?:captures|qualification|qualification-reports|reports|statistics|timelines)/)"
)


@dataclass(frozen=True)
class TreeEntry:
    mode: int
    object_id: str
    path: str


def git(repository: Path, *args: str, text: bool = False) -> bytes | str:
    return subprocess.check_output(
        ["git", "-C", str(repository), *args],
        text=text,
    )


def selected_tree(repository: Path, revision: str) -> list[TreeEntry]:
    raw = git(repository, "ls-tree", "-rz", revision)
    assert isinstance(raw, bytes)
    entries: list[TreeEntry] = []
    for record in raw.split(b"\0"):
        if not record:
            continue
        metadata, raw_path = record.split(b"\t", 1)
        raw_mode, object_type, raw_object_id = metadata.split(b" ", 2)
        path = raw_path.decode("utf-8")
        pure_path = PurePosixPath(path)
        if pure_path.is_absolute() or ".." in pure_path.parts:
            raise SystemExit(f"unsafe Git path: {path}")
        if object_type != b"blob":
            raise SystemExit(f"unsupported Git object type for {path}: {object_type.decode()}")
        if PROHIBITED.search(path):
            continue
        entries.append(
            TreeEntry(
                mode=int(raw_mode, 8),
                object_id=raw_object_id.decode("ascii"),
                path=path,
            )
        )
    entries.sort(key=lambda item: item.path.encode("utf-8"))
    if not entries:
        raise SystemExit("release archive selection is empty")
    if len({entry.path for entry in entries}) != len(entries):
        raise SystemExit("release archive selection contains duplicate paths")
    return entries


def write_archive(
    repository: Path,
    revision: str,
    tag: str,
    output: Path,
) -> list[TreeEntry]:
    if not re.fullmatch(r"v[0-9]+\.[0-9]+\.[0-9]+", tag):
        raise SystemExit("tag must use vX.Y.Z format")
    entries = selected_tree(repository, revision)
    prefix = f"Climate-Bridge-{tag}/"
    output.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_STORED) as archive:
        for entry in entries:
            data = git(repository, "cat-file", "blob", entry.object_id)
            assert isinstance(data, bytes)
            info = zipfile.ZipInfo(prefix + entry.path, FIXED_TIMESTAMP)
            info.create_system = 3
            info.compress_type = zipfile.ZIP_STORED
            info.external_attr = (entry.mode & 0xFFFF) << 16
            archive.writestr(info, data)
    verify_inventory(output, prefix, entries)
    return entries


def verify_inventory(archive_path: Path, prefix: str, entries: list[TreeEntry]) -> None:
    expected = [prefix + entry.path for entry in entries]
    with zipfile.ZipFile(archive_path) as archive:
        actual = archive.namelist()
        if actual != expected:
            raise SystemExit("archive inventory differs from selected Git tree")
        if any(PROHIBITED.search(name.removeprefix(prefix)) for name in actual):
            raise SystemExit("archive contains prohibited material")


def digest(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            value.update(chunk)
    return value.hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repository", type=Path, required=True)
    parser.add_argument("--revision", required=True)
    parser.add_argument("--tag", required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--checksum", type=Path, required=True)
    args = parser.parse_args()

    first = args.output
    second = first.with_name(first.name + ".independent")
    write_archive(args.repository, args.revision, args.tag, first)
    write_archive(args.repository, args.revision, args.tag, second)
    if first.read_bytes() != second.read_bytes():
        raise SystemExit("independent archive builds are not byte-identical")
    second.unlink()
    checksum = digest(first)
    args.checksum.write_text(f"{checksum}  {first.name}\n", encoding="ascii")
    print(f"archive={first} sha256={checksum}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
