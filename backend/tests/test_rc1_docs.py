from pathlib import Path


def test_rc1_release_docs_exist() -> None:
    repo_root = Path(__file__).resolve().parents[2]

    assert (repo_root / "docs" / "RELEASE_NOTES_RC1.md").exists()
    assert (repo_root / "docs" / "RC1_TEST_PLAN.md").exists()
    assert (repo_root / "docs" / "RC1_SCOPE_LOCK.md").exists()
