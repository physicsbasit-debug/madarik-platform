from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import httpx

from app.core.config import settings
from app.models.cloud_source import (
    CloudSource,
    CloudSourceProvider,
    CloudSourceSyncResponse,
    CloudSourceSyncStatus,
    OneDriveProviderStatus,
)
from app.services.cloud_source_repository import (
    CloudSourceRepository,
)


DOWNLOAD_DIR = (
    Path(settings.data_dir)
    / "cloud_sources"
    / "onedrive"
)


class OneDriveConfigurationError(RuntimeError):
    pass


class OneDriveGraphError(RuntimeError):
    pass


@dataclass(slots=True)
class OneDriveToken:
    access_token: str
    token_type: str = "Bearer"
    expires_in: int | None = None


def get_onedrive_provider_status() -> OneDriveProviderStatus:
    enabled = settings.onedrive_provider == "graph"
    tenant_configured = bool(settings.onedrive_tenant_id.strip())
    client_id_configured = bool(settings.onedrive_client_id.strip())
    client_secret_configured = bool(
        settings.onedrive_client_secret.strip()
    )
    configured = (
        enabled
        and tenant_configured
        and client_id_configured
        and client_secret_configured
    )

    if configured:
        message = "OneDrive Microsoft Graph adapter is configured."
    elif enabled:
        message = (
            "OneDrive adapter is enabled but credentials are incomplete."
        )
    else:
        message = "OneDrive Microsoft Graph adapter is disabled."

    return OneDriveProviderStatus(
        enabled=enabled,
        configured=configured,
        tenant_configured=tenant_configured,
        client_id_configured=client_id_configured,
        client_secret_configured=client_secret_configured,
        graph_base_url=settings.onedrive_graph_base_url,
        scope=settings.onedrive_scope,
        message=message,
    )


def _require_configuration() -> None:
    status = get_onedrive_provider_status()
    if not status.configured:
        raise OneDriveConfigurationError(status.message)


def acquire_app_token(
    *,
    client: httpx.Client | None = None,
) -> OneDriveToken:
    _require_configuration()

    token_url = (
        "https://login.microsoftonline.com/"
        f"{settings.onedrive_tenant_id}/oauth2/v2.0/token"
    )
    payload = {
        "client_id": settings.onedrive_client_id,
        "client_secret": settings.onedrive_client_secret,
        "scope": settings.onedrive_scope,
        "grant_type": "client_credentials",
    }

    owns_client = client is None
    active_client = client or httpx.Client(
        timeout=settings.onedrive_timeout_seconds,
        follow_redirects=True,
    )
    try:
        response = active_client.post(
            token_url,
            data=payload,
            headers={
                "Content-Type": (
                    "application/x-www-form-urlencoded"
                )
            },
        )
        response.raise_for_status()
        data = response.json()
    except (httpx.HTTPError, ValueError) as exc:
        raise OneDriveGraphError(
            "Failed to acquire Microsoft Graph token"
        ) from exc
    finally:
        if owns_client:
            active_client.close()

    access_token = str(data.get("access_token", "")).strip()
    if not access_token:
        raise OneDriveGraphError(
            "Microsoft token response did not include an access token"
        )

    return OneDriveToken(
        access_token=access_token,
        token_type=str(data.get("token_type", "Bearer")),
        expires_in=(
            int(data["expires_in"])
            if data.get("expires_in") is not None
            else None
        ),
    )


def _auth_headers(token: OneDriveToken) -> dict[str, str]:
    return {
        "Authorization": (
            f"{token.token_type} {token.access_token}"
        ),
        "Accept": "application/json",
    }


def _drive_item_url(source: CloudSource) -> str:
    drive_id = source.metadata.get("drive_id", "").strip()
    item_id = (
        source.metadata.get("item_id", "").strip()
        or source.external_id.strip()
    )
    if not item_id:
        raise OneDriveGraphError(
            "OneDrive source has no item identifier"
        )

    base = settings.onedrive_graph_base_url.rstrip("/")
    if drive_id:
        return f"{base}/drives/{drive_id}/items/{item_id}"
    return f"{base}/me/drive/items/{item_id}"


def fetch_drive_item_metadata(
    source: CloudSource,
    *,
    token: OneDriveToken | None = None,
    client: httpx.Client | None = None,
) -> dict[str, Any]:
    if source.provider is not CloudSourceProvider.onedrive:
        raise OneDriveGraphError(
            "Cloud source is not a OneDrive source"
        )

    active_token = token or acquire_app_token()
    owns_client = client is None
    active_client = client or httpx.Client(
        timeout=settings.onedrive_timeout_seconds,
        follow_redirects=True,
    )
    try:
        response = active_client.get(
            _drive_item_url(source),
            headers=_auth_headers(active_token),
            params={
                "$select": (
                    "id,name,eTag,lastModifiedDateTime,"
                    "webUrl,file,folder,parentReference,"
                    "@microsoft.graph.downloadUrl"
                )
            },
        )
        response.raise_for_status()
        data = response.json()
    except (httpx.HTTPError, ValueError) as exc:
        raise OneDriveGraphError(
            "Failed to fetch OneDrive item metadata"
        ) from exc
    finally:
        if owns_client:
            active_client.close()

    if not isinstance(data, dict):
        raise OneDriveGraphError(
            "Unexpected OneDrive metadata response"
        )
    return data


def _parse_datetime(value: Any) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(
            str(value).replace("Z", "+00:00")
        )
    except ValueError:
        return None


def synchronize_onedrive_source(
    source: CloudSource,
    repository: CloudSourceRepository,
    *,
    download: bool = False,
    client: httpx.Client | None = None,
) -> CloudSourceSyncResponse:
    checked_at = datetime.now(timezone.utc)
    previous_etag = source.etag

    try:
        token = acquire_app_token(client=client)
        metadata = fetch_drive_item_metadata(
            source,
            token=token,
            client=client,
        )
    except (
        OneDriveConfigurationError,
        OneDriveGraphError,
    ) as exc:
        source.sync_status = CloudSourceSyncStatus.error
        source.last_checked_at = checked_at
        source.last_error = str(exc)
        repository.save(source)
        raise

    current_etag = str(metadata.get("eTag", "")).strip() or None
    changed = bool(
        previous_etag
        and current_etag
        and previous_etag != current_etag
    )

    source.display_name = (
        str(metadata.get("name", "")).strip()
        or source.display_name
    )
    source.external_id = (
        str(metadata.get("id", "")).strip()
        or source.external_id
    )
    source.web_url = (
        str(metadata.get("webUrl", "")).strip()
        or source.web_url
    )
    source.etag = current_etag
    source.modified_at_external = _parse_datetime(
        metadata.get("lastModifiedDateTime")
    )
    source.last_checked_at = checked_at
    source.last_error = None
    source.sync_status = (
        CloudSourceSyncStatus.changed
        if changed
        else CloudSourceSyncStatus.ready
    )

    parent = metadata.get("parentReference")
    if isinstance(parent, dict):
        drive_id = str(parent.get("driveId", "")).strip()
        if drive_id:
            source.metadata["drive_id"] = drive_id

    source.metadata["item_id"] = source.external_id
    download_url = str(
        metadata.get("@microsoft.graph.downloadUrl", "")
    ).strip()

    local_path: str | None = None
    downloaded = False

    if download:
        if not download_url:
            raise OneDriveGraphError(
                "OneDrive item did not provide a download URL"
            )

        DOWNLOAD_DIR.mkdir(parents=True, exist_ok=True)
        safe_name = (
            source.display_name.replace("/", "-")
            or source.external_id
        )
        target = DOWNLOAD_DIR / f"{source.id}-{safe_name}"

        owns_client = client is None
        active_client = client or httpx.Client(
            timeout=settings.onedrive_timeout_seconds,
            follow_redirects=True,
        )
        try:
            response = active_client.get(download_url)
            response.raise_for_status()
            target.write_bytes(response.content)
        except httpx.HTTPError as exc:
            source.sync_status = CloudSourceSyncStatus.error
            source.last_error = (
                "Failed to download OneDrive file"
            )
            repository.save(source)
            raise OneDriveGraphError(
                source.last_error
            ) from exc
        finally:
            if owns_client:
                active_client.close()

        local_path = str(target)
        downloaded = True
        source.metadata["local_path"] = local_path

    repository.save(source)

    return CloudSourceSyncResponse(
        source=source,
        changed=changed,
        downloaded=downloaded,
        local_path=local_path,
        message=(
            "OneDrive source changed since the previous check."
            if changed
            else "OneDrive source synchronized."
        ),
    )
