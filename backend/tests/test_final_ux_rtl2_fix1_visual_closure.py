from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def test_start_workspace_has_single_stage_heading() -> None:
    content = read("frontend/src/features/workflow/StartWorkspace.tsx")
    assert "start-workspace-heading" not in content


def test_upload_card_contains_inline_parse_action() -> None:
    content = read("frontend/src/features/file-upload/FileUploadStep.tsx")
    assert "start-upload-inline-action" in content
    assert "استخراج الأسئلة" in content


def test_topbar_uses_compact_more_menu() -> None:
    content = read("frontend/src/components/WorkspaceTopBar.tsx")
    assert "workspace-more-menu" in content
    assert "إدارة المشاريع" in content


def test_auth_panel_is_collapsed_by_default() -> None:
    content = read("frontend/src/app/App.tsx")
    assert "useState(false)" in content
    assert "setAuthPanelOpen(!authAccount)" not in content


def test_start_navigation_requires_extracted_text() -> None:
    content = read("frontend/src/app/App.tsx")
    assert "canAdvanceFromStart" in content
    assert "أكمل رفع الملف واستخراج النص أولًا" in content


def test_empty_library_is_compact() -> None:
    content = read("frontend/src/features/project-library/ProjectLibraryPanel.tsx")
    assert "library-empty-compact" in content
