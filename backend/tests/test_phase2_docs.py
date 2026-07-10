from pathlib import Path


def test_phase2_a0_docs_exist() -> None:
    repo_root = Path(__file__).resolve().parents[2]

    assert (repo_root / "docs" / "PHASE2_ROADMAP.md").exists()
    assert (repo_root / "docs" / "PHASE2_SCOPE_GATE.md").exists()
    assert (repo_root / "docs" / "PHASE2_BACKLOG.md").exists()
    assert (repo_root / "docs" / "PHASE2_ARCHITECTURE_DECISIONS.md").exists()
    assert (repo_root / "docs" / "PHASE2_RISK_REGISTER.md").exists()
