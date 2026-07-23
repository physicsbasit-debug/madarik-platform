from __future__ import annotations

import base64
from urllib.parse import urlparse

from app.models.cloud_source import (
    CloudSourceCreateRequest,
    CloudSourceProvider,
    CloudSourceType,
)


SUPPORTED_ONEDRIVE_HOSTS = {
    "1drv.ms",
    "onedrive.live.com",
    "sharepoint.com",
}


def _host_is_supported(hostname: str) -> bool:
    hostname = hostname.lower()
    return (
        hostname in SUPPORTED_ONEDRIVE_HOSTS
        or hostname.endswith(".sharepoint.com")
    )


def encode_sharing_url(web_url: str) -> str:
    encoded = base64.urlsafe_b64encode(web_url.encode("utf-8")).decode("ascii")
    return "u!" + encoded.rstrip("=")


def parse_onedrive_source_url(
    *,
    web_url: str,
    display_name: str,
    source_project_id: str | None = None,
    source_type: CloudSourceType = CloudSourceType.file,
) -> CloudSourceCreateRequest:
    normalized_url = web_url.strip()
    normalized_name = display_name.strip()
    parsed = urlparse(normalized_url)

    if parsed.scheme not in {"http", "https"}:
        raise ValueError("OneDrive URL must use HTTP or HTTPS")
    if not parsed.hostname or not _host_is_supported(parsed.hostname):
        raise ValueError("Unsupported OneDrive or SharePoint URL")
    if not normalized_name:
        raise ValueError("OneDrive display name is required")

    share_token = encode_sharing_url(normalized_url)
    return CloudSourceCreateRequest(
        source_project_id=source_project_id,
        provider=CloudSourceProvider.onedrive,
        source_type=source_type,
        display_name=normalized_name,
        external_id=share_token,
        web_url=normalized_url,
        metadata={
            "host": parsed.hostname,
            "path": parsed.path,
            "addressing_mode": "share",
            "share_token": share_token,
        },
    )
