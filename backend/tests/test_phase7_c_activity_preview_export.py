from pathlib import Path
from zipfile import ZipFile

from app.models.differentiated_activity import (
    DifferentiatedActivity,
    DifferentiationLevel,
)
from app.services.differentiated_activity_export import (
    build_activity_preview,
    export_activity,
)

ROOT = Path(__file__).resolve().parents[2]


def activity() -> DifferentiatedActivity:
    return DifferentiatedActivity(
        title="نشاط الموجات - دعم",
        grade=10,
        science_domain="physics",
        subject_id="g10-physics",
        level=DifferentiationLevel.support,
        objective="تفسير خصائص الموجات.",
        instructions="نفذ المهمة خطوة خطوة.",
        success_criteria=["يحدد الفكرة العلمية الرئيسة."],
        estimated_minutes=30,
        materials=["نابض"],
    )


def test_preview_is_export_ready() -> None:
    preview = build_activity_preview(activity())
    assert preview.export_ready is True
    assert preview.level_label == "دعم"


def test_preview_reports_missing_criteria() -> None:
    item = activity()
    item.success_criteria = []
    preview = build_activity_preview(item)
    assert preview.export_ready is False
    assert preview.issues


def test_docx_export(tmp_path: Path, monkeypatch) -> None:
    import app.services.differentiated_activity_export as module
    monkeypatch.setattr(module, "EXPORT_DIR", tmp_path / "exports")
    result = export_activity(activity(), "docx")
    assert result.export_ready is True
    with ZipFile(result.path) as archive:
        assert "word/document.xml" in archive.namelist()


def test_pdf_export(tmp_path: Path, monkeypatch) -> None:
    import app.services.differentiated_activity_export as module
    monkeypatch.setattr(module, "EXPORT_DIR", tmp_path / "exports")
    result = export_activity(activity(), "pdf")
    assert result.export_ready is True
    assert Path(result.path).read_bytes().startswith(b"%PDF")


def test_api_routes_exist() -> None:
    content = (ROOT / "backend/app/api/projects.py").read_text(encoding="utf-8")
    assert "get_differentiated_activity_preview" in content
    assert "export_differentiated_activity" in content
    assert "FileResponse" in content


def test_frontend_has_preview_and_export_controls() -> None:
    content = (
        ROOT / "frontend/src/features/activities/DifferentiatedActivities.tsx"
    ).read_text(encoding="utf-8")
    assert "DifferentiatedActivityPreviewCard" in content
    assert 'runExport(item.id, "docx")' in content
    assert 'runExport(item.id, "pdf")' in content


def test_readme_tracks_phase_7c() -> None:
    content = (ROOT / "README.md").read_text(encoding="utf-8")
    assert "Phase 7-C" in content
    assert "Differentiated Activity Preview and Export" in content
