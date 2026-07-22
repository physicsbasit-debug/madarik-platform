from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

import httpx

from app.core.config import settings
from app.models.cloud_source import (
    CloudSourceFile,
    CloudSourceImportResult,
    CloudSourceListResponse,
    CloudSourceStatus,
)


GOOGLE_DRIVE_API_BASE = "https://www.googleapis.com/drive/v3"
SUPPORTED_MIME_TYPES = [
    "application/pdf",
    "image/png",
    "image/jpeg",
    "image/webp",
    "application/vnd.google-apps.document",
]


class GoogleDriveSourceError(RuntimeError):
    pass


def _mode() -> str:
    value = settings.google_drive_provider.strip().lower()
    return value if value in {"disabled", "mock", "google_api"} else "disabled"


def get_google_drive_status() -> CloudSourceStatus:
    mode = _mode()
    token_configured = bool(settings.google_drive_access_token.strip())
    folder_configured = bool(settings.google_drive_folder_id.strip())

    if mode == "mock":
        return CloudSourceStatus(
            mode=mode,
            configured=True,
            ready=True,
            reason="Mock provider is ready.",
            folder_configured=True,
            token_configured=False,
            supported_mime_types=SUPPORTED_MIME_TYPES,
        )

    if mode == "google_api":
        ready = token_configured and folder_configured
        return CloudSourceStatus(
            mode=mode,
            configured=token_configured or folder_configured,
            ready=ready,
            reason=(
                "Google Drive API configuration is ready."
                if ready
                else "Access token and folder ID are required."
            ),
            folder_configured=folder_configured,
            token_configured=token_configured,
            supported_mime_types=SUPPORTED_MIME_TYPES,
        )

    return CloudSourceStatus(
        mode="disabled",
        configured=False,
        ready=False,
        reason="Google Drive integration is disabled.",
        folder_configured=folder_configured,
        token_configured=token_configured,
        supported_mime_types=SUPPORTED_MIME_TYPES,
    )


def _mock_files() -> list[CloudSourceFile]:
    now = datetime.now(timezone.utc)
    return [
        CloudSourceFile(
            id="mock-grade10-physics-waves",
            file_name="الصف العاشر - الفيزياء - وحدة الموجات.pdf",
            mime_type="application/pdf",
            size_bytes=842_000,
            folder_id="mock-curriculum-folder",
            modified_at=now,
            checksum="mock-waves-v1",
        ),
        CloudSourceFile(
            id="mock-grade5-science-matter",
            file_name="الصف الخامس - العلوم - المادة وتغيراتها.pdf",
            mime_type="application/pdf",
            size_bytes=615_000,
            folder_id="mock-curriculum-folder",
            modified_at=now,
            checksum="mock-matter-v1",
        ),
    ]


def _parse_datetime(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None


def _from_google_file(payload: dict[str, Any]) -> CloudSourceFile:
    size_raw = payload.get("size")
    size_bytes = (
        int(size_raw)
        if isinstance(size_raw, str) and size_raw.isdigit()
        else None
    )
    return CloudSourceFile(
        id=str(payload["id"]),
        file_name=str(payload.get("name") or "Untitled"),
        mime_type=str(
            payload.get("mimeType") or "application/octet-stream"
        ),
        size_bytes=size_bytes,
        web_url=payload.get("webViewLink"),
        folder_id=settings.google_drive_folder_id or None,
        modified_at=_parse_datetime(payload.get("modifiedTime")),
        checksum=payload.get("md5Checksum"),
    )


def list_google_drive_files() -> CloudSourceListResponse:
    status = get_google_drive_status()

    if status.mode == "mock":
        return CloudSourceListResponse(status=status, files=_mock_files())

    if not status.ready:
        return CloudSourceListResponse(status=status, files=[])

    params = {
        "q": (
            f"'{settings.google_drive_folder_id}' in parents "
            "and trashed = false"
        ),
        "fields": (
            "files(id,name,mimeType,size,webViewLink,"
            "modifiedTime,md5Checksum)"
        ),
        "orderBy": "modifiedTime desc",
        "pageSize": 100,
    }
    headers = {
        "Authorization": f"Bearer {settings.google_drive_access_token}",
    }

    try:
        with httpx.Client(
            timeout=settings.google_drive_timeout_seconds
        ) as client:
            response = client.get(
                f"{GOOGLE_DRIVE_API_BASE}/files",
                params=params,
                headers=headers,
            )
            response.raise_for_status()
    except httpx.HTTPError as exc:
        raise GoogleDriveSourceError(
            "تعذر قراءة مجلد Google Drive."
        ) from exc

    payload = response.json()
    files = [
        _from_google_file(item)
        for item in payload.get("files", [])
        if item.get("mimeType") in SUPPORTED_MIME_TYPES
    ]
    return CloudSourceListResponse(status=status, files=files)


def _get_file_metadata(file_id: str) -> CloudSourceFile:
    listing = list_google_drive_files()
    source = next(
        (item for item in listing.files if item.id == file_id),
        None,
    )
    if source is None:
        raise GoogleDriveSourceError(
            "الملف غير موجود داخل المجلد المسموح."
        )
    return source


def import_google_drive_file(file_id: str) -> CloudSourceImportResult:
    status = get_google_drive_status()
    source = _get_file_metadata(file_id)

    if status.mode == "mock":
        content = (
            f"Mock Google Drive content for {source.file_name}"
        ).encode("utf-8")
        return CloudSourceImportResult(
            source=source,
            downloaded=True,
            byte_count=len(content),
            message="Mock file imported successfully.",
        )

    if source.mime_type == "application/vnd.google-apps.document":
        endpoint = f"{GOOGLE_DRIVE_API_BASE}/files/{file_id}/export"
        params = {"mimeType": "application/pdf"}
    else:
        endpoint = f"{GOOGLE_DRIVE_API_BASE}/files/{file_id}"
        params = {"alt": "media"}

    headers = {
        "Authorization": f"Bearer {settings.google_drive_access_token}",
    }

    try:
        with httpx.Client(
            timeout=settings.google_drive_timeout_seconds
        ) as client:
            response = client.get(
                endpoint,
                params=params,
                headers=headers,
            )
            response.raise_for_status()
    except httpx.HTTPError as exc:
        raise GoogleDriveSourceError(
            "تعذر تنزيل الملف من Google Drive."
        ) from exc

    return CloudSourceImportResult(
        source=source,
        downloaded=True,
        byte_count=len(response.content),
        message="Google Drive file downloaded successfully.",
    )
