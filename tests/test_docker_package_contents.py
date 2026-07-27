from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_dockerfile_copies_all_python_packages():
    dockerfile = (ROOT / "Dockerfile").read_text(encoding="utf-8")
    assert "COPY transport ./transport" in dockerfile
    assert "COPY adapters ./adapters" in dockerfile
    assert "COPY protocols ./protocols" in dockerfile


def test_adapter_package_is_complete():
    adapter_root = ROOT / "adapters" / "york"
    required = {
        "__init__.py",
        "connection.py",
        "session.py",
        "encoder.py",
        "decoder.py",
        "state.py",
        "errors.py",
    }
    assert required.issubset({path.name for path in adapter_root.iterdir()})
