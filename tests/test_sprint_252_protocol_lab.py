import json
from pathlib import Path
from zipfile import ZipFile

from protocols.york.capture_importer import import_captures
from protocols.york.lab_dashboard import generate_dashboard


def make_docx(path: Path, paragraphs: list[str]) -> None:
    body = ''.join(
        '<w:p><w:r><w:t>' + value.replace('&', '&amp;').replace('<', '&lt;') + '</w:t></w:r></w:p>'
        for value in paragraphs
    )
    xml = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
           '<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">'
           f'<w:body>{body}</w:body></w:document>')
    with ZipFile(path, 'w') as archive:
        archive.writestr('word/document.xml', xml)


def test_docx_import_and_dashboard(tmp_path):
    capture = tmp_path / 'capture.docx'
    make_docx(capture, [
        '[2026-07-13 17:20:03.672] MARK: swing left right on',
        'HEX: BB 01 00 03 0F 01 00 35 07 20 20 00 00 00 00 00 00 5F 00 00 DA',
    ])
    root = tmp_path / 'protocol'
    report = import_captures([capture], root)
    assert report['unique_frame_count'] == 1
    assert Path(report['outputs']['dashboard']).exists()
    model = json.loads((root / 'dashboard' / 'protocol-lab.json').read_text())
    assert model['feature_status']['swing_lr']['status'] == 'observed'
    copied = next((root / 'captures' / 'imported').glob('*.txt'))
    assert copied.exists()


def test_dashboard_handles_empty_reference(tmp_path):
    result = generate_dashboard(tmp_path)
    assert Path(result['dashboard']).exists()
    assert result['model']['unique_observed_packets'] == 0
