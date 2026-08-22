import hashlib
import re
import subprocess
import sys
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github" / "workflows" / "release.yml"
BUILDER = ROOT / ".github" / "scripts" / "build_release_archive.py"

ACTION_PINS = {
    "actions/checkout": "11d5960a326750d5838078e36cf38b85af677262",
    "actions/setup-python": "a26af69be951a213d495a4c3e4e4022e16d87065",
    "actions/upload-artifact": "ea165f8d65b6e75b540449e92b4886f43607fa02",
    "actions/download-artifact": "d3f86a106a0bac45b974a628896c90dbdf5c8093",
}


def run(*args: str, cwd: Path) -> None:
    subprocess.run(args, cwd=cwd, check=True, capture_output=True, text=True)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_release_workflow_is_manual_and_verify_only_cannot_publish():
    text = WORKFLOW.read_text(encoding="utf-8")
    trigger = text[text.index("on:") : text.index("\npermissions:")]
    assert "workflow_dispatch:" in trigger
    assert "push:" not in trigger
    assert "pull_request:" not in trigger
    assert "default: verify_only" in text
    assert 'verify_only) test "$OPERATION_CONFIRMATION" = "VERIFY $RELEASE_TAG"' in text
    assert 'test "$OPERATION_CONFIRMATION" = "PUBLISH $RELEASE_TAG"' in text
    publish = text[text.index("  publish-release:") :]
    assert "if: ${{ inputs.operation == 'publish' }}" in publish
    assert "contents: write" not in text[: text.index("  publish-release:")]
    assert "contents: write" in publish


def test_actions_are_reviewed_full_sha_pins():
    text = WORKFLOW.read_text(encoding="utf-8")
    uses = re.findall(r"^\s*uses:\s*([^\s#]+)", text, flags=re.MULTILINE)
    assert uses
    for reference in uses:
        action, separator, revision = reference.partition("@")
        assert separator == "@"
        assert re.fullmatch(r"[0-9a-f]{40}", revision)
        assert ACTION_PINS[action] == revision


def test_publication_uses_controlled_notes_and_checks_native_immutability():
    text = WORKFLOW.read_text(encoding="utf-8")
    assert "--generate-notes" not in text
    assert "--notes-file release-artifacts/release-notes.md" in text
    assert 'cp "$RUNNER_TEMP/release-notes.md" candidate/release-notes.md' in text
    assert "docs/releases/<tag>.md" in text
    for section in (
        "Release scope",
        "Supported functions",
        "Known limitations",
        "Installation or upgrade",
        "Rollback",
    ):
        assert f'"{section}"' in text
    assert "cmp --silent release-artifacts/release-notes.md" in text
    assert "'.immutable == true'" in text


def test_deterministic_archive_matches_git_tree_and_changes_with_blob(tmp_path: Path):
    repository = tmp_path / "repository"
    repository.mkdir()
    run("git", "init", "-q", cwd=repository)
    run("git", "config", "user.name", "Release Contract", cwd=repository)
    run("git", "config", "user.email", "release-contract@example.invalid", cwd=repository)
    (repository / "app.py").write_text("print('one')\n", encoding="utf-8")
    (repository / "README.md").write_text("# Example\n", encoding="utf-8")
    tests = repository / "tests"
    tests.mkdir()
    (tests / "private_test.py").write_text("excluded\n", encoding="utf-8")
    release_notes = repository / "docs" / "releases"
    release_notes.mkdir(parents=True)
    (release_notes / "v1.2.3.md").write_text("controlled notes\n", encoding="utf-8")
    run("git", "add", ".", cwd=repository)
    run("git", "commit", "-qm", "candidate one", cwd=repository)

    first = tmp_path / "first.zip"
    first_checksum = tmp_path / "first.zip.sha256"
    run(
        sys.executable, str(BUILDER), "--repository", str(repository),
        "--revision", "HEAD", "--tag", "v1.2.3", "--output", str(first),
        "--checksum", str(first_checksum), cwd=ROOT,
    )
    second = tmp_path / "second.zip"
    run(
        sys.executable, str(BUILDER), "--repository", str(repository),
        "--revision", "HEAD", "--tag", "v1.2.3", "--output", str(second),
        "--checksum", str(tmp_path / "second.zip.sha256"), cwd=ROOT,
    )
    assert first.read_bytes() == second.read_bytes()
    assert first_checksum.read_text(encoding="ascii").startswith(sha256(first))
    with zipfile.ZipFile(first) as archive:
        assert archive.namelist() == [
            "Climate-Bridge-v1.2.3/README.md",
            "Climate-Bridge-v1.2.3/app.py",
        ]
        assert {entry.date_time for entry in archive.infolist()} == {
            (1980, 1, 1, 0, 0, 0)
        }
        assert {entry.compress_type for entry in archive.infolist()} == {
            zipfile.ZIP_STORED
        }

    (repository / "app.py").write_text("print('two')\n", encoding="utf-8")
    run("git", "add", "app.py", cwd=repository)
    run("git", "commit", "-qm", "candidate two", cwd=repository)
    changed = tmp_path / "changed.zip"
    run(
        sys.executable, str(BUILDER), "--repository", str(repository),
        "--revision", "HEAD", "--tag", "v1.2.3", "--output", str(changed),
        "--checksum", str(tmp_path / "changed.zip.sha256"), cwd=ROOT,
    )
    assert sha256(first) != sha256(changed)


def test_current_release_and_historical_identity_are_unambiguous():
    status = (ROOT / "PROJECT_STATUS.md").read_text(encoding="utf-8")
    checklist = (ROOT / "RELEASE_CHECKLIST.md").read_text(encoding="utf-8")
    process = (ROOT / "docs" / "RELEASE_PROCESS.md").read_text(encoding="utf-8")
    for text in (status, checklist, process):
        assert "current software release is `v1.0.0`" in text.lower()
        assert "`v3.0.0`" in text
        assert "historical" in text.lower()
