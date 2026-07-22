from pydantic import BaseModel, Field

from app.models.project import CurriculumSourceAttachment


class AttachCurriculumSourceRequest(BaseModel):
    source_file_id: str = Field(min_length=1, max_length=256)
    grade: int = Field(ge=1, le=12)
    science_domain: str = Field(min_length=1, max_length=64)
    semester_id: str = Field(min_length=1, max_length=128)
    subject_id: str = Field(min_length=1, max_length=128)
    unit_id: str | None = Field(default=None, max_length=128)
    source_document_type: str = Field(
        default="other",
        min_length=1,
        max_length=64,
    )


class CurriculumSourceListResponse(BaseModel):
    items: list[CurriculumSourceAttachment]


class RefreshCurriculumSourcesResponse(BaseModel):
    items: list[CurriculumSourceAttachment]
    checked_count: int
    changed_count: int
    missing_count: int
    unverifiable_count: int
