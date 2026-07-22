from pathlib import Path
import re


REPO_ROOT = Path(__file__).resolve().parents[2]


def test_final_ux_uses_three_stage_workflow() -> None:
    steps_file = REPO_ROOT / "frontend" / "src" / "constants" / "steps.ts"
    content = steps_file.read_text(encoding="utf-8")

    stage_keys = re.findall(r"key: '(start|review|export)'", content)
    assert stage_keys == ["start", "review", "export"]
    assert "getWorkflowStageIndex" in content
    assert "getLegacyStepForStage" in content


def test_final_ux_keeps_advanced_tools_but_removes_them_from_main_navigation() -> None:
    app = (REPO_ROOT / "frontend" / "src" / "app" / "App.tsx").read_text(
        encoding="utf-8"
    )
    review = (
        REPO_ROOT
        / "frontend"
        / "src"
        / "features"
        / "workflow"
        / "UnifiedReviewWorkspace.tsx"
    ).read_text(encoding="utf-8")

    assert "StartWorkspace" in app
    assert "UnifiedReviewWorkspace" in app
    assert "أدوات متقدمة" in review
    assert "ExtractionStep" in review
    assert "GlossaryStep" in review


def test_final_ux_adds_bulk_project_delete_and_glossary_approval() -> None:
    library = (
        REPO_ROOT
        / "frontend"
        / "src"
        / "features"
        / "project-library"
        / "ProjectLibraryPanel.tsx"
    ).read_text(encoding="utf-8")
    glossary = (
        REPO_ROOT
        / "frontend"
        / "src"
        / "features"
        / "glossary"
        / "GlossaryStep.tsx"
    ).read_text(encoding="utf-8")

    assert "تحديد الكل" in library
    assert "حذف المحدد" in library
    assert "onDeleteProjects" in library
    assert "اعتماد المكتمل" in glossary
    assert "onApproveAll" in glossary


def test_final_ux_document_exists() -> None:
    document = REPO_ROOT / "docs" / "FINAL_UX_1_THREE_STAGE_WORKFLOW.md"
    assert document.exists()
    content = document.read_text(encoding="utf-8")
    assert "البدء والرفع" in content
    assert "المراجعة" in content
    assert "التصدير" in content
