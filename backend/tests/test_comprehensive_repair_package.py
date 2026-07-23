from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from types import SimpleNamespace

from fastapi import HTTPException
from fastapi.testclient import TestClient
import pytest

from app.api import projects as projects_api
from app.main import app
from app.models.auth import AccountRole, AuthAccountPublic
from app.models.cloud_source import (
    CloudSourceCreateRequest,
    CloudSourceListResponse,
    CloudSourceProvider,
    CloudSourceRegistryListResponse,
    CloudSourceStatus,
)
from app.models.scientific_diagram import (
    ScientificDiagram,
    ScientificDiagramNode,
    ScientificDiagramType,
)
from app.services.cloud_source_repository import CloudSourceRepository
from app.services.file_names import safe_filename_stem
from app.services.onedrive_graph_adapter import (
    OneDriveGraphError,
    OneDriveToken,
    _drive_item_url,
    synchronize_onedrive_source,
)
from app.services.onedrive_source_parser import parse_onedrive_source_url
from app.services.scientific_diagram_renderer import (
    build_scientific_diagram_preview,
)


ROOT = Path(__file__).resolve().parents[2]
CLIENT = TestClient(app)


def account(
    account_id: str,
    role: AccountRole = AccountRole.teacher,
) -> AuthAccountPublic:
    return AuthAccountPublic(
        id=account_id,
        username=f"user-{account_id}",
        display_name=f"User {account_id}",
        role=role,
        created_at=datetime.now(timezone.utc),
    )


def test_static_project_routes_are_not_shadowed() -> None:
    for path in (
        "/api/projects/cloud-sources",
        "/api/projects/differentiated-activities",
        "/api/projects/scientific-diagrams",
        "/api/projects/assessment-builder",
    ):
        response = CLIENT.get(path)
        assert response.status_code == 200, (path, response.text)


def test_legacy_and_registry_cloud_contracts_coexist() -> None:
    legacy = CloudSourceListResponse(
        status=CloudSourceStatus(
            mode="disabled",
            configured=False,
            ready=False,
            reason="disabled",
        ),
        files=[],
    )
    registry = CloudSourceRegistryListResponse(
        items=[],
        total=0,
    )

    assert legacy.files == []
    assert registry.total == 0
    assert "status" in CloudSourceListResponse.model_fields
    assert "items" in CloudSourceRegistryListResponse.model_fields


def test_cloud_source_upsert_preserves_primary_key(
    tmp_path: Path,
) -> None:
    repository = CloudSourceRepository(
        tmp_path / "cloud.sqlite3"
    )
    payload = CloudSourceCreateRequest(
        provider=CloudSourceProvider.onedrive,
        display_name="First",
        external_id="stable-external-id",
        web_url="https://1drv.ms/u/s!example",
    )

    first = repository.create(payload)
    second = repository.create(
        payload.model_copy(
            update={"display_name": "Updated"}
        )
    )

    assert second.id == first.id
    assert repository.get(first.id) is not None
    assert repository.get(first.id).display_name == "Updated"


def test_onedrive_share_url_uses_shares_api() -> None:
    payload = parse_onedrive_source_url(
        web_url=(
            "https://school.sharepoint.com/:b:/s/science/"
            "ExampleSharingLink"
        ),
        display_name="Science file",
    )
    source = projects_api.CloudSource(
        **payload.model_dump()
    )

    graph_url = _drive_item_url(source)

    assert source.external_id.startswith("u!")
    assert "/shares/" in graph_url
    assert graph_url.endswith("/driveItem")
    assert "/me/" not in graph_url


def test_onedrive_download_requires_https_url(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    import app.services.onedrive_graph_adapter as graph_module

    repository = CloudSourceRepository(
        tmp_path / "cloud.sqlite3"
    )
    payload = parse_onedrive_source_url(
        web_url="https://1drv.ms/u/s!unsafe-download",
        display_name="Unsafe download",
    )
    source = repository.create(payload)

    monkeypatch.setattr(
        graph_module,
        "acquire_app_token",
        lambda **_: OneDriveToken(access_token="token"),
    )
    monkeypatch.setattr(
        graph_module,
        "fetch_drive_item_metadata",
        lambda *_, **__: {
            "id": "item-1",
            "name": "science.pdf",
            "eTag": "etag-1",
            "webUrl": "https://example.invalid/item",
            "@microsoft.graph.downloadUrl": (
                "http://untrusted.invalid/file"
            ),
        },
    )

    with pytest.raises(OneDriveGraphError):
        synchronize_onedrive_source(
            source,
            repository,
            download=True,
        )

    stored = repository.get(source.id)
    assert stored is not None
    assert stored.sync_status.value == "error"
    assert "HTTPS" in (stored.last_error or "")


def test_safe_filename_stem_handles_windows_names() -> None:
    assert safe_filename_stem("CON") == "_CON"
    assert safe_filename_stem('exam<>:"/\\|?*.pdf') == "exam-.pdf"
    assert safe_filename_stem("   ...   ", fallback="export") == "export"


def test_svg_ids_cannot_break_out_of_attributes() -> None:
    malicious_id = 'node" onload="alert(1)'
    diagram = ScientificDiagram(
        title="Safe diagram",
        diagram_type=ScientificDiagramType.process,
        grade=10,
        science_domain="physics",
        subject_id="g10-physics",
        nodes=[
            ScientificDiagramNode(
                id=malicious_id,
                label="Node",
                order_index=1,
            )
        ],
    )

    preview = build_scientific_diagram_preview(diagram)

    assert 'data-node-id="node" onload=' not in preview.svg
    assert "&quot;" in preview.svg

    frontend = (
        ROOT
        / "frontend/src/features/diagrams/ScientificDiagramPreview.tsx"
    ).read_text(encoding="utf-8")
    assert "dangerouslySetInnerHTML" not in frontend
    assert "data:image/svg+xml" in frontend


def test_unauthorized_delete_checks_access_before_mutation(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    class FakeRepository:
        deleted = False

        def get(self, activity_id: str):
            return SimpleNamespace(
                id=activity_id,
                owner_account_id="owner-account",
            )

        def delete(self, activity_id: str):
            self.deleted = True
            return None

    repository = FakeRepository()
    monkeypatch.setattr(
        projects_api,
        "differentiated_activity_repository",
        repository,
    )

    with pytest.raises(HTTPException) as exc_info:
        projects_api.delete_differentiated_activity(
            "activity-1",
            account("other-account"),
        )

    assert exc_info.value.status_code == 403
    assert repository.deleted is False


def test_frontend_import_blocks_are_well_formed() -> None:
    for relative in (
        "frontend/src/app/App.tsx",
        "frontend/src/features/assessment/AssessmentBuilder.tsx",
        "frontend/src/features/activities/DifferentiatedActivities.tsx",
        "frontend/src/features/diagrams/ScientificDiagrams.tsx",
    ):
        content = (ROOT / relative).read_text(encoding="utf-8")
        assert "import type {\nimport " not in content


def test_requirement_pins_are_unique() -> None:
    requirements = (
        ROOT / "backend/requirements.txt"
    ).read_text(encoding="utf-8")
    names: list[str] = []

    for line in requirements.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        name = line.split("==", 1)[0].lower()
        names.append(name)

    assert len(names) == len(set(names))


def test_package_lock_version_matches_package_json() -> None:
    import json

    package = json.loads(
        (ROOT / "frontend/package.json").read_text(encoding="utf-8")
    )
    lock = json.loads(
        (ROOT / "frontend/package-lock.json").read_text(
            encoding="utf-8"
        )
    )

    assert lock["version"] == package["version"]
    assert lock["packages"][""]["version"] == package["version"]
