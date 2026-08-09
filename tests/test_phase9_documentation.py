from pathlib import Path
import re

import yaml

from version import APP_VERSION


ROOT = Path(__file__).resolve().parents[1]


def test_current_release_documents_identify_stable_v1():
    for relative in ("README.md", "CHANGELOG.md", "RELEASE_NOTES.md"):
        text = (ROOT / relative).read_text(encoding="utf-8")
        assert APP_VERSION in text, relative
    assert (ROOT / "RELEASE_NOTES.md").read_text(encoding="utf-8").startswith("# Climate Bridge 1.0.0")


def test_readme_local_markdown_links_resolve():
    text = (ROOT / "README.md").read_text(encoding="utf-8")
    targets = re.findall(r"\[[^\]]+\]\(([^)]+)\)", text)
    local = [target.split("#", 1)[0] for target in targets if target and not target.startswith(("http://", "https://", "#"))]
    assert local
    for target in local:
        assert (ROOT / target).exists(), target


def test_current_entry_points_and_native_configuration_exist():
    for relative in (
        "config.example.yml", "docker-compose.yml", ".github/workflows/qualification.yml",
        "phase6_quality_gate.py", "release_verifier.py", "validate_config.py",
        "york_decoder_qualification.py", "york_packet_classifier.py",
        "york_request_hunter.py", "york_capture_importer.py",
    ):
        assert (ROOT / relative).exists(), relative
    config = yaml.safe_load((ROOT / "config.example.yml").read_text(encoding="utf-8"))
    assert config["transport"]["type"] == "native"
    assert config["direct_read"]["enabled"] is True
    assert not (ROOT / "transport" / "relay_transport.py").exists()


def test_changelog_and_release_notes_have_one_stable_release_story():
    changelog = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
    release_notes = (ROOT / "RELEASE_NOTES.md").read_text(encoding="utf-8")
    assert changelog.count("# 1.0.0 — Sprint 3.2.1 First York Stable Release") == 1
    assert "eight-step end-to-end acceptance sequence" in release_notes
    assert "allowlist has been changed or widened" in release_notes
