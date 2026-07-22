from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field


class CloudProvider(str, Enum):
    google_drive = "google_drive"


class CloudSourceAccessScope(str, Enum):
    read_only = "read_only"


class CloudSourceFile(BaseModel):
    id: str
    provider: CloudProvider = CloudProvider.google_drive
    file_name: str
    mime_type: str
    size_bytes: int | None = None
    web_url: str | None = None
    folder_id: str | None = None
    modified_at: datetime | None = None
    checksum: str | None = None
    access_scope: CloudSourceAccessScope = CloudSourceAccessScope.read_only


class CloudSourceStatus(BaseModel):
    provider: CloudProvider = CloudProvider.google_drive
    mode: str
    configured: bool
    ready: bool
    reason: str
    folder_configured: bool
    token_configured: bool
    supported_mime_types: list[str]
    read_only: bool = True


class CloudSourceListResponse(BaseModel):
    status: CloudSourceStatus
    files: list[CloudSourceFile] = Field(default_factory=list)


class CloudSourceImportRequest(BaseModel):
    file_id: str = Field(min_length=1, max_length=256)


class CloudSourceImportResult(BaseModel):
    source: CloudSourceFile
    downloaded: bool
    byte_count: int
    message: str
