from datetime import datetime, timezone
from enum import Enum
from uuid import uuid4
from pydantic import BaseModel, Field

class CloudSourceProvider(str, Enum):
    google_drive = "google_drive"
    onedrive = "onedrive"

class CloudSourceType(str, Enum):
    file = "file"
    folder = "folder"

class CloudSourceSyncStatus(str, Enum):
    pending = "pending"
    ready = "ready"
    changed = "changed"
    error = "error"

class CloudSource(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    owner_account_id: str | None = None
    source_project_id: str | None = None
    provider: CloudSourceProvider
    source_type: CloudSourceType = CloudSourceType.file
    display_name: str
    external_id: str
    web_url: str
    parent_external_id: str | None = None
    mime_type: str | None = None
    etag: str | None = None
    modified_at_external: datetime | None = None
    sync_status: CloudSourceSyncStatus = CloudSourceSyncStatus.pending
    last_checked_at: datetime | None = None
    last_error: str | None = None
    metadata: dict[str, str] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class CloudSourceCreateRequest(BaseModel):
    source_project_id: str | None = None
    provider: CloudSourceProvider
    source_type: CloudSourceType = CloudSourceType.file
    display_name: str
    external_id: str
    web_url: str
    parent_external_id: str | None = None
    mime_type: str | None = None
    etag: str | None = None
    modified_at_external: datetime | None = None
    metadata: dict[str, str] = Field(default_factory=dict)

class CloudSourceListResponse(BaseModel):
    items: list[CloudSource]
    total: int


class OneDriveProviderStatus(BaseModel):
    enabled: bool
    configured: bool
    tenant_configured: bool
    client_id_configured: bool
    client_secret_configured: bool
    graph_base_url: str
    scope: str
    live_request_attempted: bool = False
    message: str


class CloudSourceSyncResponse(BaseModel):
    source: CloudSource
    changed: bool
    downloaded: bool = False
    local_path: str | None = None
    message: str
