from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_suite_integrates_decoder_check() -> None:
    source = (ROOT / "qualification_suite.py").read_text(encoding="utf-8")
    assert "from york_decoder_qualification import run_qualification" in source
    assert 'self.check("York decoder fixtures", self.decoder_fixture_check)' in source
    assert "14/14" not in source


def test_docker_packages_both_qualification_entry_points() -> None:
    dockerfile = (ROOT / "Dockerfile").read_text(encoding="utf-8")
    assert "qualification_suite.py" in dockerfile
    assert "york_decoder_qualification.py" in dockerfile


def test_fixture_file_is_packaged() -> None:
    fixtures = (
        ROOT
        / "protocols"
        / "york"
        / "qualification"
        / "decoder_fixtures.json"
    )
    assert fixtures.is_file()
