from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]


def read(relative_path: str) -> str:
    return (REPO_ROOT / relative_path).read_text(encoding="utf-8")


def test_start_workspace_uses_three_rtl_columns() -> None:
    workspace = read("frontend/src/features/workflow/StartWorkspace.tsx")

    assert 'className="start-workspace-grid"' in workspace
    assert 'className="start-details-column"' in workspace
    assert 'className="start-upload-column"' in workspace
    assert 'className="start-library-column"' in workspace
    assert workspace.index("start-details-column") < workspace.index(
        "start-upload-column"
    )
    assert workspace.index("start-upload-column") < workspace.index(
        "start-library-column"
    )


def test_start_workspace_preserves_existing_business_callbacks() -> None:
    workspace = read("frontend/src/features/workflow/StartWorkspace.tsx")

    for callback in (
        "onMetadataChange",
        "onLogoSelected",
        "onLogoRemove",
        "onFileSelected",
        "onRefreshProjects",
        "onOpenProject",
        "onDeleteProject",
        "onDeleteProjects",
        "onParseQuestions",
    ):
        assert callback in workspace

    assert "../services/api" not in workspace
    assert "fetch(" not in workspace


def test_start_project_details_keep_metadata_and_export_preferences() -> None:
    setup = read(
        "frontend/src/features/project-setup/ProjectSetupStep.tsx"
    )

    for field in (
        "schoolName",
        "directorate",
        "subject",
        "grade",
        "semester",
        "paperTitle",
        "duration",
        "totalMarks",
        "teacherName",
        "date",
    ):
        assert field in setup

    assert "setOutputMode" in setup
    assert "toggleFormat" in setup
    assert "onLogoSelected" in setup
    assert 'className="start-advanced-details"' in setup


def test_upload_card_preserves_file_callback_and_status_data() -> None:
    upload = read("frontend/src/features/file-upload/FileUploadStep.tsx")

    assert "onFileSelected(file)" in upload
    assert "onFileSelected(null)" in upload
    assert "extractedText.pageCount" in upload
    assert "extractedText.characterCount" in upload
    assert "layoutAssets.length" in upload
    assert "start-upload-zone" in upload
    assert "is-drag-active" in upload


def test_rtl_start_layout_has_expected_visual_order() -> None:
    css = read("frontend/src/styles/global.css")

    assert ".start-workspace-grid" in css
    assert "direction: rtl" in css
    assert ".start-details-column" in css
    assert "grid-column: 1" in css
    assert ".start-upload-column" in css
    assert "grid-column: 2" in css
    assert ".start-library-column" in css
    assert "grid-column: 3" in css


def test_start_layout_is_responsive() -> None:
    css = read("frontend/src/styles/global.css")

    assert "@media (max-width: 1280px)" in css
    assert "@media (max-width: 860px)" in css
    assert "@media (max-width: 560px)" in css
    assert ".start-parse-button" in css
