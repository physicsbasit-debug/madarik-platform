from __future__ import annotations
from hashlib import sha256
from urllib.parse import parse_qs, urlparse
from app.models.cloud_source import CloudSourceCreateRequest, CloudSourceProvider, CloudSourceType

SUPPORTED_ONEDRIVE_HOSTS = {"1drv.ms", "onedrive.live.com", "sharepoint.com"}

def _host_is_supported(hostname: str) -> bool:
    hostname = hostname.lower()
    return hostname in SUPPORTED_ONEDRIVE_HOSTS or hostname.endswith('.sharepoint.com')

def parse_onedrive_source_url(*, web_url: str, display_name: str, source_project_id: str | None = None, source_type: CloudSourceType = CloudSourceType.file) -> CloudSourceCreateRequest:
    normalized_url = web_url.strip()
    parsed = urlparse(normalized_url)
    if parsed.scheme not in {'http', 'https'}:
        raise ValueError('OneDrive URL must use HTTP or HTTPS')
    if not parsed.hostname or not _host_is_supported(parsed.hostname):
        raise ValueError('Unsupported OneDrive or SharePoint URL')
    query = parse_qs(parsed.query)
    external_id = query.get('id', [None])[0] or query.get('resid', [None])[0] or query.get('sourcedoc', [None])[0]
    if not external_id:
        external_id = sha256(normalized_url.encode('utf-8')).hexdigest()
    return CloudSourceCreateRequest(
        source_project_id=source_project_id,
        provider=CloudSourceProvider.onedrive,
        source_type=source_type,
        display_name=display_name.strip(),
        external_id=external_id,
        web_url=normalized_url,
        metadata={'host': parsed.hostname, 'path': parsed.path},
    )
