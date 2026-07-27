from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_root_qualification_reports_directory_is_packaged():
    assert (ROOT / "qualification-reports").is_dir()
    assert (ROOT / "qualification-reports" / "README.md").is_file()


def test_protocol_qualification_reports_directory_is_packaged():
    assert (
        ROOT / "protocols" / "york" / "qualification-reports" / "README.md"
    ).is_file()


def test_compose_mount_source_exists():
    compose = (ROOT / "docker-compose.yml").read_text(encoding="utf-8")
    assert "source: ./qualification-reports" in compose
    assert "target: /reports" in compose


def test_docker_startup_avoids_nonportable_brace_expansion():
    dockerfile = (ROOT / "Dockerfile").read_text(encoding="utf-8")
    assert "/config/york_protocol/{" not in dockerfile
    assert "mkdir -p /reports" in dockerfile
