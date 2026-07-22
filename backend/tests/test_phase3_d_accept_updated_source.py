from datetime import datetime, timezone
from pathlib import Path

from app.models.cloud_source import CloudSourceFile
from app.models.project import CurriculumSourceAttachment
from app.services.curriculum_source_refresh import (
    accept_updated_source,
)


ROOT = Path(__file__).resolve().parents[2]


def build_attachment() -> CurriculumSourceAttachment:
    return CurriculumSourceAttachment(
        provider="google_drive",
        source_file_id="file-1",
        file_name="old.pdf",
        mime_type="application/pdf",
        size_bytes=100,
        checksum="old-checksum",
        grade=10,
        science_domain="physics",
        semester_id="g10-sem2",
        subject_id="g10-physics",
        source_modified_at=datetime(
            2026, 1, 1, tzinfo=timezone.utc
        ),
        source_refresh_status="changed",
    )


def build_current() -> CloudSourceFile:
    return CloudSourceFile(
        id="file-1",
        file_name="new.pdf",
        mime_type="application/pdf",
        size_bytes=200,
        checksum="new-checksum",
        modified_at=datetime(
            2026, 2, 1, tzinfo=timezone.utc
        ),
    )


def test_accept_update_preserves_previous_version() -> None:
    updated = accept_updated_source(
        build_attachment(),
        build_current(),
    )
    assert len(updated.version_history) == 1
    assert (
        updated.version_history[0].checksum
        == "old-checksum"
    )
    assert updated.version_history[0].file_name == "old.pdf"


def test_accept_update_applies_current_metadata() -> None:
    updated = accept_updated_source(
        build_attachment(),
        build_current(),
    )
    assert updated.checksum == "new-checksum"
    assert updated.file_name == "new.pdf"
    assert updated.size_bytes == 200
    assert updated.source_refresh_status == "current"


def test_version_history_default_is_compatible() -> None:
    assert build_attachment().version_history == []


def test_accept_update_route_exists() -> None:
    content = (
        ROOT / "backend/app/api/cloud_sources.py"
    ).read_text(encoding="utf-8")
    assert "accept_curriculum_source_update" in content
    assert "accept-update" in content


def test_frontend_exposes_accept_and_history() -> None:
    content = (
        ROOT
        / "frontend/src/features/curriculum/GoogleDriveSourcePanel.tsx"
    ).read_text(encoding="utf-8")
    assert "acceptProjectCurriculumSourceUpdate" in content
    assert "اعتماد النسخة الجديدة" in content
    assert "سجل النسخ السابقة" in content


def test_readme_tracks_phase_3d() -> None:
    content = (ROOT / "README.md").read_text(
        encoding="utf-8"
    )
    assert "Phase 3-D" in content
    assert "Source Version History" in content
