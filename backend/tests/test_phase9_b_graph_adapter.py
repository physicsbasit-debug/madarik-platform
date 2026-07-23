from pathlib import Path

import httpx
import pytest

from app.core.config import settings
from app.models.cloud_source import (
    CloudSource,
    CloudSourceProvider,
)
from app.services.cloud_source_repository import (
    CloudSourceRepository,
)
from app.services.onedrive_graph_adapter import (
    OneDriveConfigurationError,
    OneDriveToken,
    acquire_app_token,
    fetch_drive_item_metadata,
    get_onedrive_provider_status,
    synchronize_onedrive_source,
)


ROOT = Path(__file__).resolve().parents[2]


def source() -> CloudSource:
    return CloudSource(
        provider=CloudSourceProvider.onedrive,
        display_name="ملف العلوم",
        external_id="item-1",
        web_url="https://onedrive.live.com/?id=item-1",
        metadata={
            "drive_id": "drive-1",
            "item_id": "item-1",
        },
    )


def configure(monkeypatch) -> None:
    monkeypatch.setattr(settings, "onedrive_provider", "graph")
    monkeypatch.setattr(settings, "onedrive_tenant_id", "tenant")
    monkeypatch.setattr(settings, "onedrive_client_id", "client")
    monkeypatch.setattr(
        settings,
        "onedrive_client_secret",
        "secret",
    )


def test_status_does_not_expose_secret(monkeypatch) -> None:
    configure(monkeypatch)
    status = get_onedrive_provider_status()
    assert status.configured is True
    assert "super-secret-value" not in status.model_dump_json()


def test_token_request_uses_client_credentials(
    monkeypatch,
) -> None:
    configure(monkeypatch)

    def handler(request: httpx.Request) -> httpx.Response:
        body = request.content.decode()
        assert "grant_type=client_credentials" in body
        assert "scope=https%3A%2F%2Fgraph.microsoft.com" in body
        return httpx.Response(
            200,
            json={
                "access_token": "token-value",
                "token_type": "Bearer",
                "expires_in": 3600,
            },
        )

    with httpx.Client(
        transport=httpx.MockTransport(handler)
    ) as client:
        token = acquire_app_token(client=client)

    assert token.access_token == "token-value"


def test_disabled_configuration_blocks_token(
    monkeypatch,
) -> None:
    monkeypatch.setattr(
        settings,
        "onedrive_provider",
        "disabled",
    )
    with pytest.raises(OneDriveConfigurationError):
        acquire_app_token()


def test_metadata_request_uses_drive_item_endpoint(
    monkeypatch,
) -> None:
    configure(monkeypatch)

    def handler(request: httpx.Request) -> httpx.Response:
        assert "/drives/drive-1/items/item-1" in str(request.url)
        assert request.headers["Authorization"] == "Bearer token"
        return httpx.Response(
            200,
            json={
                "id": "item-1",
                "name": "science.pdf",
                "eTag": "etag-2",
                "webUrl": "https://example.invalid/item",
            },
        )

    with httpx.Client(
        transport=httpx.MockTransport(handler)
    ) as client:
        result = fetch_drive_item_metadata(
            source(),
            token=OneDriveToken(access_token="token"),
            client=client,
        )

    assert result["eTag"] == "etag-2"


def test_sync_detects_etag_change(
    tmp_path: Path,
    monkeypatch,
) -> None:
    configure(monkeypatch)
    repository = CloudSourceRepository(
        tmp_path / "db.sqlite"
    )
    item = source()
    item.etag = "etag-1"
    repository.save(item)

    def handler(request: httpx.Request) -> httpx.Response:
        if "oauth2/v2.0/token" in str(request.url):
            return httpx.Response(
                200,
                json={
                    "access_token": "token",
                    "token_type": "Bearer",
                },
            )
        return httpx.Response(
            200,
            json={
                "id": "item-1",
                "name": "science.pdf",
                "eTag": "etag-2",
                "webUrl": "https://example.invalid/item",
                "lastModifiedDateTime": (
                    "2026-07-23T08:00:00Z"
                ),
                "parentReference": {
                    "driveId": "drive-1"
                },
            },
        )

    with httpx.Client(
        transport=httpx.MockTransport(handler)
    ) as client:
        result = synchronize_onedrive_source(
            item,
            repository,
            client=client,
        )

    assert result.changed is True
    assert result.source.etag == "etag-2"
    assert result.source.sync_status.value == "changed"


def test_api_routes_exist() -> None:
    content = (
        ROOT / "backend/app/api/projects.py"
    ).read_text(encoding="utf-8")
    assert "get_onedrive_status" in content
    assert "sync_cloud_source" in content


def test_frontend_has_sync_controls() -> None:
    content = (
        ROOT / "frontend/src/features/cloud/CloudSources.tsx"
    ).read_text(encoding="utf-8")
    assert "Microsoft Graph" in content
    assert "فحص المزامنة" in content
    assert "تنزيل الملف" in content


def test_readme_tracks_phase_9b() -> None:
    content = (ROOT / "README.md").read_text(
        encoding="utf-8"
    )
    assert "Phase 9-B" in content
    assert (
        "OneDrive Authentication and Microsoft Graph Adapter"
        in content
    )
