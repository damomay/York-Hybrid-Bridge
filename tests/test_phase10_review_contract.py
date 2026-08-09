from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
HISTORY = ROOT / "docs" / "history"


def test_historical_evidence_is_grouped_and_labelled():
    names = {path.name for path in HISTORY.glob("*.md")}
    assert "SPRINT_2_8_3_RELAY_PACKET_EXTRACTION.md" in names
    assert "SPRINT_3_1_63_GENERAL_COOL_QUALIFIED_FAN_TEMPERATURE_ENCODER.md" in names
    assert "V1_0_0_ACCEPTANCE_AND_STABILITY_EVIDENCE.md" in names
    readme = " ".join((HISTORY / "README.md").read_text(encoding="utf-8").split())
    assert "historical evidence" in readme


def test_reconciliation_records_source_policy_and_open_pr_gate():
    evidence = (ROOT / "docs" / "reconciliation" / "sprint-3.2.1-v1-source-reconciliation.md").read_text(encoding="utf-8")
    assert "Sprint 3.2.1" in evidence
    assert "preserved" in evidence.lower()
    assert "draft pull request" in evidence.lower()
