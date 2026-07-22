from datetime import datetime, timedelta, timezone
from pathlib import Path

from app.models.cloud_source import CloudSourceFile
from app.models.project import (
    CurriculumSourceAttachment,
    ProjectSession,
)
from app.services.curriculum_source_refresh import (
    SourceRefreshState,
    compare_source_version,
)


ROOT = Path(__file__).resolve().parents[2]


def attachment(
    checksum: str | None = "same",
    modified_at: datetime | None = None,
) -> CurriculumSourceAttachment:
    return CurriculumSourceAttachment(
        provider="google_drive",
        source_file_id="file-1",
        file_name="waves.pdf",
        mime_type="application/pdf",
        checksum=checksum,
        grade=10,
        science_domain="physics",
        semester_id="g10-sem2",
        subject_id="g10-physics",
        source_modified_at=modified_at,
    )


def current(
    checksum: str | None = "same",
    modified_at: datetime | None = None,
) -> CloudSourceFile:
    return CloudSourceFile(
        id="file-1",
        file_name="waves.pdf",
        mime_type="application/pdf",
        checksum=checksum,
        modified_at=modified_at,
    )


def test_matching_checksum_is_current() -> None:
    state, _ = compare_source_version(
        attachment(),
        current(),
    )
    assert state is SourceRefreshState.current


def test_changed_checksum_is_detected() -> None:
    state, _ = compare_source_version(
        attachment("old"),
        current("new"),
    )
    assert state is SourceRefreshState.changed


def test_newer_modified_time_is_changed() -> None:
    old = datetime.now(timezone.utc) - timedelta(days=1)
    new = datetime.now(timezone.utc)
    state, _ = compare_source_version(
        attachment(None, old),
        current(None, new),
    )
    assert state is SourceRefreshState.changed


def test_missing_source_is_detected() -> None:
    state, _ = compare_source_version(
        attachment(),
        None,
    )
    assert state is SourceRefreshState.missing


def test_unverifiable_source_is_detected() -> None:
    state, _ = compare_source_version(
        attachment(None, None),
        current(None, None),
    )
    assert state is SourceRefreshState.unverifiable


def test_model_defaults_are_backward_compatible() -> None:
    project = ProjectSession(
        curriculum_sources=[attachment()]
    )
    source = project.curriculum_sources[0]

    assert source.source_refresh_status == "unknown"
    assert source.last_checked_at is None
    assert source.refresh_message is None


def test_refresh_api_route_exists() -> None:
    content = (
        ROOT / "backend/app/api/cloud_sources.py"
    ).read_text(encoding="utf-8")

    assert "check_curriculum_source_updates" in content
    assert "check-refresh" in content
    assert "changed_count" in content
    assert "project_store.touch(project_id)" in content


def test_frontend_has_refresh_states() -> None:
    content = (
        ROOT
        / "frontend/src/features/curriculum/GoogleDriveSourcePanel.tsx"
    ).read_text(encoding="utf-8")

    assert "checkProjectCurriculumSourceUpdates" in content
    assert "فحص التحديثات" in content
    assert "تغيّر المصدر" in content
    assert "المصدر مفقود" in content
