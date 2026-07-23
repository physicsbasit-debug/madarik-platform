from pathlib import Path

import httpx
from reportlab.pdfgen import canvas

from app.models.cloud_source import (
    CloudSource,
    CloudSourceProvider,
    CloudSourceSyncResponse,
)
from app.models.cloud_source_version import (
    CloudSourceVersion,
    CloudSourceVersionState,
)
from app.services.cloud_source_lifecycle import (
    accept_cloud_source_version,
    intake_cloud_source_version,
    refresh_cloud_source,
)
from app.services.cloud_source_repository import (
    CloudSourceRepository,
)
from app.services.cloud_source_version_repository import (
    CloudSourceVersionRepository,
)
from app.services.project_repository import ProjectRepository
from app.services.session_store import InMemoryProjectStore


ROOT = Path(__file__).resolve().parents[2]


def source() -> CloudSource:
    return CloudSource(
        provider=CloudSourceProvider.onedrive,
        display_name="science.pdf",
        external_id="item-1",
        web_url="https://example.invalid/science.pdf",
        mime_type="application/pdf",
    )


def write_pdf(path: Path, text: str = "Question 1") -> None:
    pdf = canvas.Canvas(str(path))
    pdf.drawString(72, 760, text)
    pdf.save()


def test_version_repository_deduplicates_fingerprint(
    tmp_path: Path,
) -> None:
    repository = CloudSourceVersionRepository(
        tmp_path / "db.sqlite"
    )
    version = CloudSourceVersion(
        source_id="source-1",
        fingerprint="fingerprint",
        display_name="science.pdf",
        external_id="item-1",
        web_url="https://example.invalid/file",
    )

    first, created_first = repository.create_or_update(version)
    second, created_second = repository.create_or_update(
        version.model_copy(update={"id": "other-id"})
    )

    assert created_first is True
    assert created_second is False
    assert first.id == second.id
    assert len(repository.list("source-1")) == 1


def test_first_refresh_becomes_accepted(
    tmp_path: Path,
    monkeypatch,
) -> None:
    source_repository = CloudSourceRepository(
        tmp_path / "db.sqlite"
    )
    version_repository = CloudSourceVersionRepository(
        tmp_path / "db.sqlite"
    )
    item = source_repository.save(source())
    downloaded = tmp_path / "science.pdf"
    write_pdf(downloaded)

    def fake_sync(*args, **kwargs):
        current = args[0]
        current.etag = "etag-1"
        return CloudSourceSyncResponse(
            source=current,
            changed=False,
            downloaded=True,
            local_path=str(downloaded),
            message="synced",
        )

    monkeypatch.setattr(
        "app.services.cloud_source_lifecycle."
        "synchronize_onedrive_source",
        fake_sync,
    )

    result = refresh_cloud_source(
        item,
        source_repository,
        version_repository,
    )

    assert result.changed is False
    assert result.version.state is CloudSourceVersionState.accepted
    assert result.source.sync_status.value == "ready"
    assert result.source.metadata["accepted_version_id"] == (
        result.version.id
    )


def test_second_refresh_waits_for_acceptance(
    tmp_path: Path,
    monkeypatch,
) -> None:
    source_repository = CloudSourceRepository(
        tmp_path / "db.sqlite"
    )
    version_repository = CloudSourceVersionRepository(
        tmp_path / "db.sqlite"
    )
    item = source_repository.save(source())
    first_pdf = tmp_path / "first.pdf"
    second_pdf = tmp_path / "second.pdf"
    write_pdf(first_pdf, "First")
    write_pdf(second_pdf, "Second")
    calls = {"count": 0}

    def fake_sync(*args, **kwargs):
        current = args[0]
        calls["count"] += 1
        current.etag = f"etag-{calls['count']}"
        return CloudSourceSyncResponse(
            source=current,
            changed=calls["count"] > 1,
            downloaded=True,
            local_path=str(
                first_pdf if calls["count"] == 1 else second_pdf
            ),
            message="synced",
        )

    monkeypatch.setattr(
        "app.services.cloud_source_lifecycle."
        "synchronize_onedrive_source",
        fake_sync,
    )

    first = refresh_cloud_source(
        item,
        source_repository,
        version_repository,
    )
    second = refresh_cloud_source(
        first.source,
        source_repository,
        version_repository,
    )

    assert second.changed is True
    assert second.version.state is CloudSourceVersionState.detected
    assert second.source.metadata["pending_version_id"] == (
        second.version.id
    )

    accepted = accept_cloud_source_version(
        second.source,
        second.version,
        source_repository,
        version_repository,
    )
    assert accepted.version.state is CloudSourceVersionState.accepted
    assert accepted.source.sync_status.value == "ready"
    assert "pending_version_id" not in accepted.source.metadata
    old = version_repository.get(first.version.id)
    assert old is not None
    assert old.state is CloudSourceVersionState.superseded


def test_accepted_pdf_enters_existing_project(
    tmp_path: Path,
) -> None:
    database = tmp_path / "db.sqlite"
    source_repository = CloudSourceRepository(database)
    version_repository = CloudSourceVersionRepository(database)
    project_store = InMemoryProjectStore(
        ProjectRepository(database)
    )
    project = project_store.create()
    pdf_path = tmp_path / "science.pdf"
    write_pdf(pdf_path, "1 Explain velocity")

    item = source_repository.save(source())
    version = version_repository.save(
        CloudSourceVersion(
            source_id=item.id,
            fingerprint="accepted",
            state=CloudSourceVersionState.accepted,
            display_name="science.pdf",
            external_id="item-1",
            web_url=item.web_url,
            mime_type="application/pdf",
            local_path=str(pdf_path),
        )
    )

    result = intake_cloud_source_version(
        item,
        version,
        source_repository,
        version_repository,
        project_store,
        target_project=project,
    )

    assert result.created_project is False
    assert result.project.uploaded_file is not None
    assert result.project.uploaded_file.name == "science.pdf"
    assert result.project.extracted_text is not None
    assert "velocity" in result.project.extracted_text.text
    assert result.version.intake_project_id == project.id


def test_intake_rejects_unaccepted_version(
    tmp_path: Path,
) -> None:
    database = tmp_path / "db.sqlite"
    source_repository = CloudSourceRepository(database)
    version_repository = CloudSourceVersionRepository(database)
    project_store = InMemoryProjectStore(
        ProjectRepository(database)
    )
    item = source_repository.save(source())
    version = CloudSourceVersion(
        source_id=item.id,
        fingerprint="pending",
        state=CloudSourceVersionState.detected,
        display_name="science.pdf",
        external_id="item-1",
        web_url=item.web_url,
        mime_type="application/pdf",
        local_path=str(tmp_path / "missing.pdf"),
    )

    try:
        intake_cloud_source_version(
            item,
            version,
            source_repository,
            version_repository,
            project_store,
        )
    except ValueError as exc:
        assert "accepted" in str(exc)
    else:
        raise AssertionError("unaccepted version was not rejected")


def test_api_routes_exist() -> None:
    content = (
        ROOT / "backend/app/api/projects.py"
    ).read_text(encoding="utf-8")

    assert "list_cloud_source_versions" in content
    assert "refresh_cloud_source_route" in content
    assert "accept_cloud_source_version_route" in content
    assert "intake_cloud_source_version_route" in content


def test_frontend_has_version_workflow() -> None:
    content = (
        ROOT
        / "frontend/src/features/cloud/CloudSources.tsx"
    ).read_text(encoding="utf-8")

    assert "تحديث وحفظ نسخة" in content
    assert "سجل النسخ" in content
    assert "اعتماد النسخة" in content
    assert "إدخال إلى المشروع" in content


def test_readme_tracks_phase_9c() -> None:
    content = (ROOT / "README.md").read_text(
        encoding="utf-8"
    )
    assert "Phase 9-C" in content
    assert (
        "Cloud Source Refresh, Version History, and Project Intake"
        in content
    )
