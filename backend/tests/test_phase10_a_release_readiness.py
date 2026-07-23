from pathlib import Path

from fastapi.testclient import TestClient

from app.core.config import settings
from app.core.release import APP_VERSION, RELEASE_PHASE
from app.main import app
from app.models.release_readiness import ReleaseReadinessState
from app.services.assessment_repository import AssessmentRepository
from app.services.auth_repository import AuthRepository
from app.services.cloud_source_repository import CloudSourceRepository
from app.services.cloud_source_version_repository import (
    CloudSourceVersionRepository,
)
from app.services.differentiated_activity_repository import (
    DifferentiatedActivityRepository,
)
from app.services.project_repository import ProjectRepository
from app.services.question_bank_repository import QuestionBankRepository
from app.services.release_readiness import build_release_readiness_report
from app.services.scientific_diagram_repository import (
    ScientificDiagramRepository,
)


client = TestClient(app)


def _initialize_schema(db_path: Path) -> None:
    for repository in (
        ProjectRepository,
        AuthRepository,
        QuestionBankRepository,
        AssessmentRepository,
        DifferentiatedActivityRepository,
        ScientificDiagramRepository,
        CloudSourceRepository,
        CloudSourceVersionRepository,
    ):
        repository(db_path)


def test_release_readiness_passes_local_technical_gate(
    tmp_path: Path,
) -> None:
    db_path = tmp_path / "data" / "madarik.sqlite3"
    _initialize_schema(db_path)
    runtime = settings.model_copy(
        update={
            "db_path": str(db_path),
            "data_dir": str(tmp_path / "data"),
            "ai_provider": "mock",
            "ai_external_enabled": False,
            "google_drive_provider": "disabled",
            "onedrive_provider": "disabled",
        }
    )

    report = build_release_readiness_report(runtime)

    assert report.technical_ready is True
    assert report.state is ReleaseReadinessState.degraded
    assert report.blocking_count == 0
    assert {item.key for item in report.checks} >= {
        "database_connection",
        "database_schema",
        "data_directory",
        "export_directory",
        "translation_provider",
        "google_drive_provider",
        "onedrive_provider",
    }


def test_release_readiness_blocks_incomplete_enabled_provider(
    tmp_path: Path,
) -> None:
    db_path = tmp_path / "data" / "madarik.sqlite3"
    _initialize_schema(db_path)
    runtime = settings.model_copy(
        update={
            "db_path": str(db_path),
            "data_dir": str(tmp_path / "data"),
            "ai_provider": "openai",
            "ai_external_enabled": True,
            "ai_api_key": "",
            "ai_model": "",
            "onedrive_provider": "graph",
            "onedrive_tenant_id": "",
            "onedrive_client_id": "",
            "onedrive_client_secret": "",
        }
    )

    report = build_release_readiness_report(runtime)

    assert report.technical_ready is False
    assert report.state is ReleaseReadinessState.blocked
    assert report.blocking_count >= 2


def test_readiness_endpoint_exposes_no_secret_or_runtime_path(
    monkeypatch,
    tmp_path: Path,
) -> None:
    import app.services.release_readiness as module

    db_path = tmp_path / "private" / "madarik.sqlite3"
    _initialize_schema(db_path)
    fake_secret = "release-readiness-secret-value"
    runtime = settings.model_copy(
        update={
            "db_path": str(db_path),
            "data_dir": str(tmp_path / "private"),
            "ai_provider": "openai",
            "ai_external_enabled": True,
            "ai_api_key": fake_secret,
            "ai_model": "test-model",
            "onedrive_provider": "graph",
            "onedrive_tenant_id": "tenant-secret-value",
            "onedrive_client_id": "client-secret-value",
            "onedrive_client_secret": "onedrive-secret-value",
        }
    )
    monkeypatch.setattr(module, "settings", runtime)

    response = client.get("/api/health/readiness")
    serialized = response.text

    assert response.status_code == 200
    assert response.json()["version"] == APP_VERSION
    assert response.json()["phase"] == RELEASE_PHASE
    for forbidden in (
        fake_secret,
        "tenant-secret-value",
        "client-secret-value",
        "onedrive-secret-value",
        str(tmp_path),
    ):
        assert forbidden not in serialized


def test_fastapi_release_metadata_is_current() -> None:
    assert app.version == APP_VERSION
    assert RELEASE_PHASE in app.description
