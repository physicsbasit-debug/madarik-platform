from datetime import datetime, timezone
from enum import Enum
from uuid import uuid4

from pydantic import BaseModel, Field


class DifferentiationLevel(str, Enum):
    support = "support"
    core = "core"
    extension = "extension"


class DifferentiatedActivity(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    owner_account_id: str | None = None
    source_project_id: str | None = None
    title: str
    grade: int = Field(ge=1, le=12)
    science_domain: str
    subject_id: str
    unit_id: str | None = None
    lesson_id: str | None = None
    learning_outcome_ids: list[str] = Field(default_factory=list)
    level: DifferentiationLevel
    objective: str
    instructions: str
    success_criteria: list[str] = Field(default_factory=list)
    estimated_minutes: int = Field(default=20, ge=5, le=180)
    materials: list[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class DifferentiatedActivityCreateRequest(BaseModel):
    source_project_id: str | None = None
    title: str
    grade: int = Field(ge=1, le=12)
    science_domain: str
    subject_id: str
    unit_id: str | None = None
    lesson_id: str | None = None
    learning_outcome_ids: list[str] = Field(default_factory=list)
    level: DifferentiationLevel
    objective: str
    instructions: str
    success_criteria: list[str] = Field(default_factory=list)
    estimated_minutes: int = Field(default=20, ge=5, le=180)
    materials: list[str] = Field(default_factory=list)


class DifferentiatedActivityListResponse(BaseModel):
    items: list[DifferentiatedActivity]
    total: int
