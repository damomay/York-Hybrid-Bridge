from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RECONCILIATION = ROOT / "docs" / "reconciliation"
CLOSEOUT = RECONCILIATION / "phase-12-reconciliation-closeout.md"
NEXT_ROADMAP = ROOT / "docs" / "roadmaps" / "tablet-removal.md"
BASELINE = "137b509b5dadd6459b43f70c5a8295beba477d5c"


def test_reconciliation_index_accounts_for_all_published_gates():
    text = (RECONCILIATION / "README.md").read_text(encoding="utf-8")
    for phase in range(2, 13):
        assert f"| {phase} |" in text
    for phase in range(2, 12):
        assert f"| {phase} | PASS |" in text
    assert "| 12 | IN PROGRESS | `phase-12-reconciliation-closeout.md` |" in text


def test_closeout_records_source_manifest_and_canonical_baseline():
    text = CLOSEOUT.read_text(encoding="utf-8")
    assert BASELINE in text
    assert "all 45 files tracked by polished repository baseline" in text
    assert "all 244 files" in text
    assert "84 generated cache or bytecode files assigned omission" in text
    assert "eight generated outputs assigned regeneration" in text
    assert (
        "c2668aefb17d672e3c146ccecd43988d09d056b35fd2bda3fc6a7f3fe12c9ed4"
        in text
    )
    assert (
        "2d53cc8a01b409433086605c3640d8840975f7663ab516b17676f59864ac17a2"
        in text
    )


def test_closeout_preserves_verified_limitations_and_release_boundary():
    text = CLOSEOUT.read_text(encoding="utf-8")
    normalized = " ".join(text.split())
    for requirement in (
        "Android tablet relay remains required",
        "still constructs the native York command",
        "23 state responses",
        "zero eligible native request candidates",
        "Only one York unit",
        "Multiple-device operation has not been implemented",
        "No alpha.20 tag or GitHub release",
    ):
        assert requirement in normalized


def test_next_roadmap_starts_at_baseline_and_preserves_locked_order():
    text = NEXT_ROADMAP.read_text(encoding="utf-8")
    assert BASELINE in text
    stages = [
        "## Stage 1 — Native command discovery",
        "## Stage 2 — Direct communication qualification",
        "## Stage 3 — Controlled single-device direct test",
        "## Stage 4 — Tablet removal",
        "## Stage 5 — Multiple-device support",
    ]
    positions = [text.index(stage) for stage in stages]
    assert positions == sorted(positions)
    assert "This stage is locked until tablet-free single-device operation passes." in text


def test_closeout_handoff_and_release_boundary_are_explicit():
    closeout = CLOSEOUT.read_text(encoding="utf-8")
    assert "without changing the verified runtime" in closeout
    assert "131/131 tests" in closeout
    assert "204 staged files" in closeout
    assert "`../roadmaps/tablet-removal.md`" in closeout
    assert NEXT_ROADMAP.exists()

    checklist = (ROOT / "RELEASE_CHECKLIST.md").read_text(encoding="utf-8")
    assert "- [ ] Phase 12 reconciliation closeout has passed." in checklist
    assert "- [ ] Any tag or release publication has separate approval." in checklist
