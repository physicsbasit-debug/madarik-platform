from datetime import datetime, timezone
from enum import Enum
from uuid import uuid4

from pydantic import BaseModel, Field

from app.models.cloud_source import CloudSource
from app.models.project import ProjectSession


class CloudSourceVersionState(str, Enum):
    detected = "detected"
    accepted = "accepted"
    superseded = "superseded"


class CloudSourceVersion(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    source_id: str
    fingerprint: str
    state: CloudSourceVersionState = CloudSourceVersionState.detected
    display_name: str
    external_id: str
    web_url: str
    mime_type: str | None = None
    etag: str | None = None
    checksum_sha256: str | None = None
    size_bytes: int | None = Field(default=None, ge=0)
    local_path: str | None = None
    modified_at_external: datetime | None = None
    detected_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    accepted_at: datetime | None = None
    intake_project_id: str | None = None
    intake_at: datetime | None = None
    metadata: dict[str, str] = Field(default_factory=dict)


class CloudSourceVersionListResponse(BaseModel):
    items: list[CloudSourceVersion]
    total: int
    accepted_version_id: str | None = None
    pending_version_id: str | None = None


class CloudSourceRefreshResponse(BaseModel):
    source: CloudSource
    version: CloudSourceVersion
    changed: bool
    duplicate: bool
    downloaded: bool
    message: str


class CloudSourceAcceptVersionResponse(BaseModel):
    source: CloudSource
    version: CloudSourceVersion
    message: str


class CloudSourceProjectIntakeRequest(BaseModel):
    target_project_id: str | None = None


class CloudSourceProjectIntakeResponse(BaseModel):
    source: CloudSource
    version: CloudSourceVersion
    project: ProjectSession
    created_project: bool
    message: str
