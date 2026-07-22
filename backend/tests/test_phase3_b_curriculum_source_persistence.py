from pathlib import Path

from app.models.cloud_source import CloudSourceFile
from app.models.project import ProjectSession
from app.services.curriculum_sources import (
    attach_curriculum_source,
    remove_curriculum_source,
)


ROOT = Path(__file__).resolve().parents[2]


def build_project() -> ProjectSession:
    return ProjectSession()


def build_source() -> CloudSourceFile:
    return CloudSourceFile(
        id="drive-file-1",
        file_name="waves.pdf",
        mime_type="application/pdf",
        size_bytes=100,
        checksum="checksum-1",
    )


def test_project_has_curriculum_sources_default() -> None:
    project = build_project()
    assert project.curriculum_sources == []


def test_attach_source_persists_curriculum_metadata() -> None:
    project = build_project()
    attachment = attach_curriculum_source(
        project,
        build_source(),
        grade=10,
        science_domain="physics",
        semester_id="g10-sem2",
        subject_id="g10-physics",
        unit_id="g10-physics-sem2-waves",
        source_document_type="student_book",
    )

    assert attachment in project.curriculum_sources
    assert attachment.grade == 10
    assert attachment.science_domain == "physics"
    assert (
        attachment.unit_id
        == "g10-physics-sem2-waves"
    )


def test_same_source_and_checksum_is_not_duplicated() -> None:
    project = build_project()
    first = attach_curriculum_source(
        project,
        build_source(),
        grade=10,
        science_domain="physics",
        semester_id="g10-sem2",
        subject_id="g10-physics",
    )
    second = attach_curriculum_source(
        project,
        build_source(),
        grade=10,
        science_domain="physics",
        semester_id="g10-sem2",
        subject_id="g10-physics",
    )

    assert first.id == second.id
    assert len(project.curriculum_sources) == 1


def test_remove_source_attachment() -> None:
    project = build_project()
    attachment = attach_curriculum_source(
        project,
        build_source(),
        grade=10,
        science_domain="physics",
        semester_id="g10-sem2",
        subject_id="g10-physics",
    )

    removed = remove_curriculum_source(
        project,
        attachment.id,
    )
    assert removed.id == attachment.id
    assert project.curriculum_sources == []


def test_api_routes_exist() -> None:
    content = (
        ROOT / "backend/app/api/cloud_sources.py"
    ).read_text(encoding="utf-8")

    assert "list_project_curriculum_sources" in content
    assert "attach_google_drive_source_to_project" in content
    assert "delete_project_curriculum_source" in content
    assert "project_store.touch(project_id)" in content


def test_frontend_panel_uses_persisted_source_api() -> None:
    content = (
        ROOT
        / "frontend/src/features/curriculum/GoogleDriveSourcePanel.tsx"
    ).read_text(encoding="utf-8")

    assert "listProjectCurriculumSources" in content
    assert "attachGoogleDriveCurriculumSource" in content
    assert "deleteProjectCurriculumSource" in content
    assert "استيراد وربط" in content


def test_curriculum_browser_passes_context() -> None:
    content = (
        ROOT
        / "frontend/src/features/curriculum/CurriculumBrowser.tsx"
    ).read_text(encoding="utf-8")

    assert "projectId={projectId}" in content
    assert "scienceDomain={" in content
    assert "semesterId={semester?.id" in content
    assert "unitId={activeUnit?.id" in content
