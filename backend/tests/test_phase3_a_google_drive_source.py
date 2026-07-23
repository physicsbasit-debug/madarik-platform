import importlib
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[2]


def test_google_drive_models_and_service_exist() -> None:
    assert (ROOT / "backend/app/models/cloud_source.py").exists()
    assert (ROOT / "backend/app/services/google_drive.py").exists()
    assert (ROOT / "backend/app/api/cloud_sources.py").exists()


def test_default_provider_is_disabled(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("MADARIK_GOOGLE_DRIVE_PROVIDER", "disabled")

    import app.core.config as config_module
    import app.services.google_drive as drive_module

    importlib.reload(config_module)
    importlib.reload(drive_module)

    status = drive_module.get_google_drive_status()
    assert status.mode == "disabled"
    assert status.ready is False
    assert status.token_configured is False


def test_mock_provider_lists_and_imports_files(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("MADARIK_GOOGLE_DRIVE_PROVIDER", "mock")

    import app.core.config as config_module
    import app.services.google_drive as drive_module

    importlib.reload(config_module)
    importlib.reload(drive_module)

    listing = drive_module.list_google_drive_files()
    assert listing.status.ready is True
    assert len(listing.files) == 2
    assert all(
        item.access_scope.value == "read_only"
        for item in listing.files
    )

    result = drive_module.import_google_drive_file(
        listing.files[0].id
    )
    assert result.downloaded is True
    assert result.byte_count > 0


def test_google_api_requires_token_and_folder(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv(
        "MADARIK_GOOGLE_DRIVE_PROVIDER",
        "google_api",
    )
    monkeypatch.delenv(
        "MADARIK_GOOGLE_DRIVE_ACCESS_TOKEN",
        raising=False,
    )
    monkeypatch.delenv(
        "MADARIK_GOOGLE_DRIVE_FOLDER_ID",
        raising=False,
    )

    import app.core.config as config_module
    import app.services.google_drive as drive_module

    importlib.reload(config_module)
    importlib.reload(drive_module)

    status = drive_module.get_google_drive_status()
    assert status.mode == "google_api"
    assert status.ready is False


def test_api_router_is_registered() -> None:
    content = (ROOT / "backend/app/main.py").read_text(
        encoding="utf-8"
    )
    assert "cloud_sources_router" in content
    assert "app.include_router(cloud_sources_router" in content


def test_frontend_cloud_source_panel_exists() -> None:
    content = (
        ROOT
        / "frontend/src/features/curriculum/GoogleDriveSourcePanel.tsx"
    ).read_text(encoding="utf-8")

    assert "Google Drive" in content
    assert "listGoogleDriveSourceFiles" in content
    assert "attachGoogleDriveCurriculumSource" in content


def test_app_curriculum_import_is_not_inside_type_import() -> None:
    content = (ROOT / "frontend/src/app/App.tsx").read_text(
        encoding="utf-8"
    )
    assert (
        'import CurriculumBrowser from '
        '"../features/curriculum/CurriculumBrowser";'
    ) in content
    assert "import type {\nimport CurriculumBrowser" not in content


def test_cloud_source_api_does_not_expose_token() -> None:
    model = (ROOT / "backend/app/models/cloud_source.py").read_text(
        encoding="utf-8"
    )
    assert "access_token" not in model
    assert "token_configured" in model
