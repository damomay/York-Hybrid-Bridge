from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
HISTORY = ROOT / "docs" / "history"
APPROVED_HISTORY = {
    "RC4_QUALIFICATION_GUIDE.md",
    "RC4_TEST_RESULTS.md",
    "README_V3_RC44.md",
    "README_V3_RC441.md",
    "SPRINT_1_NOTES.md",
    "SPRINT_2_2_NOTES.md",
    "SPRINT_2_3_ALPHA4_NOTES.md",
    "SPRINT_2_3_ALPHA5_NOTES.md",
    "SPRINT_2_3_NOTES.md",
    "SPRINT_2_4_PROTOCOL_REFERENCE_NOTES.md",
    "SPRINT_2_5_1_CAPTURE_IMPORTER_NOTES.md",
    "SPRINT_2_5_2_PROTOCOL_LAB_NOTES.md",
    "SPRINT_2_5_3_DECODER_NOTES.md",
    "SPRINT_2_5_4_DEPLOYMENT_HARDENING.md",
    "SPRINT_2_5_ALPHA7_NOTES.md",
    "SPRINT_2_6_1_INTEGRATED_QUALIFICATION.md",
    "SPRINT_2_6_DECODER_QUALIFICATION.md",
    "SPRINT_2_7_1_PACKET_CLASSIFIER.md",
    "SPRINT_2_7_NATIVE_STATE_PROBE.md",
    "SPRINT_2_8_2_PHASE_1_TX_INSTRUMENTATION.md",
    "SPRINT_2_8_2_PHASE_2_REQUEST_HUNTER.md",
    "SPRINT_2_8_3_RELAY_PACKET_EXTRACTION.md",
    "SPRINT_2_8_REPLAY_ENGINE.md",
    "SPRINT_2_NOTES.md",
}


def test_phase1_approved_history_is_present_and_labelled_historical():
    assert {path.name for path in HISTORY.glob("*.md")} == (
        APPROVED_HISTORY | {"README.md"}
    )
    readme = (HISTORY / "README.md").read_text(encoding="utf-8")
    normalized_readme = " ".join(readme.split())
    assert (
        "historical evidence, not current operating or release guidance"
        in normalized_readme
    )


def test_release_checklist_records_completed_merge_and_post_merge_gates():
    checklist = (ROOT / "RELEASE_CHECKLIST.md").read_text(encoding="utf-8")
    assert "Climate Bridge 1.0.0-alpha.20" in checklist
    assert "- [x] Phase 10 pull-request diff review is complete." in checklist
    assert "- [x] Explicit approval to merge has been recorded." in checklist
    assert "- [x] Phase 11 clean post-merge verification has passed." in checklist
    assert "- [ ] Phase 12 reconciliation closeout has passed." in checklist
    assert "- [ ] Any tag or release publication has separate approval." in checklist


def test_published_phase_evidence_no_longer_claims_publication_is_pending():
    for phase in (2, 3, 9):
        matches = list((ROOT / "docs" / "reconciliation").glob(f"phase-{phase}-*.md"))
        assert len(matches) == 1
        text = matches[0].read_text(encoding="utf-8")
        assert "Status: PASS." in text
        assert "publication pending" not in text
        assert "Gate " + str(phase) + ": PASS." in text


def test_phase9_test_count_is_not_described_as_latest():
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    assert "Phase 9 reconciliation gate collected **122 tests**" in readme
    assert "latest reconciliation gate collected **117 tests**" not in readme
