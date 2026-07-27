from pathlib import Path
import re

import yaml

from version import APP_VERSION


ROOT = Path(__file__).resolve().parents[1]
CURRENT_DOCS = [
    ROOT / "README.md",
    ROOT / "CHANGELOG.md",
    ROOT / "ROADMAP.md",
    ROOT / "RELEASE_NOTES.md",
    ROOT / "docs" / "ARCHITECTURE.md",
    ROOT / "docs" / "CONFIGURATION.md",
    ROOT / "docs" / "TESTING.md",
    ROOT / "docs" / "TROUBLESHOOTING.md",
]


def test_current_documents_agree_on_version_transport_and_limitations():
    for path in CURRENT_DOCS:
        text = path.read_text(encoding="utf-8")
        assert APP_VERSION in text, path

    joined = "\n".join(path.read_text(encoding="utf-8") for path in CURRENT_DOCS)
    assert "Android relay" in joined
    assert "Native direct control and tablet removal are not achieved" in joined
    assert "Multiple-device" in joined or "multiple-device" in joined
    assert "**v3.0.0**" not in joined
    assert "## Version 3.1" not in joined


def test_readme_local_markdown_links_resolve():
    text = (ROOT / "README.md").read_text(encoding="utf-8")
    targets = re.findall(r"\[[^\]]+\]\(([^)]+)\)", text)
    local_targets = [
        target.split("#", 1)[0]
        for target in targets
        if target and not target.startswith(("http://", "https://", "#"))
    ]
    assert local_targets
    for target in local_targets:
        assert (ROOT / target).exists(), target


def test_documented_paths_entry_points_and_config_keys_exist():
    required_paths = [
        "config.example.yml",
        "docker-compose.yml",
        ".github/workflows/qualification.yml",
        "phase6_quality_gate.py",
        "release_verifier.py",
        "validate_config.py",
        "york_decoder_qualification.py",
        "york_packet_classifier.py",
        "york_request_hunter.py",
        "york_capture_importer.py",
        "york_relay_extraction_report.py",
    ]
    for relative in required_paths:
        assert (ROOT / relative).exists(), relative

    config = yaml.safe_load((ROOT / "config.example.yml").read_text(encoding="utf-8"))
    assert config["transport"]["type"] == "relay"
    assert config["direct_device"]["enabled"] is False
    assert all(value is False for key, value in config["debug"].items() if key != "probe_interval_seconds" and key != "capture_directory")


def test_public_roadmap_preserves_post_reconciliation_order():
    text = (ROOT / "ROADMAP.md").read_text(encoding="utf-8")
    milestones = [
        "### 1. Native command discovery and tablet removal",
        "### 2. Direct-device communication qualification",
        "### 3. Controlled single-device direct testing",
        "### 4. Multiple-device support",
        "### 5. Broader HVAC adapter framework",
    ]
    positions = [text.index(item) for item in milestones]
    assert positions == sorted(positions)


def test_changelog_and_release_notes_have_one_current_release_story():
    changelog = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
    release_notes = (ROOT / "RELEASE_NOTES.md").read_text(encoding="utf-8")
    assert changelog.count("## [1.0.0-alpha.20]") == 1
    assert release_notes.startswith("# Climate Bridge 1.0.0-alpha.20")
    assert "23 state responses" in release_notes
    assert "zero eligible native request" in release_notes
