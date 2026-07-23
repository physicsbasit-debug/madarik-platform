from pathlib import Path


def test_phase2_rc1_docs_exist_and_lock_scope() -> None:
    docs_dir = Path(__file__).resolve().parents[2] / "docs"

    required_docs = [
        "PHASE2_RC1_RELEASE_NOTES.md",
        "PHASE2_RC1_TEST_PLAN.md",
        "PHASE2_RC1_SCOPE_LOCK.md",
        "PHASE2_RC1_ACCEPTANCE_CHECKLIST.md",
    ]

    for filename in required_docs:
        path = docs_dir / filename
        assert path.exists(), f"Missing {filename}"
        content = path.read_text(encoding="utf-8")
        assert "Phase 2-RC1" in content

    scope_lock = (docs_dir / "PHASE2_RC1_SCOPE_LOCK.md").read_text(encoding="utf-8")
    assert "لا تُضاف ميزات جديدة" in scope_lock
    assert "Phase 3" in scope_lock


def test_readme_reflects_current_release_candidate() -> None:
    readme = Path(__file__).resolve().parents[2] / "README.md"
    content = readme.read_text(encoding="utf-8")

    assert content.startswith("# منصة مدارك\n")
    assert "2.0.0-rc.2" in content
    assert "Phase 4-B1" in content
    assert "Final Release Candidate" in content
