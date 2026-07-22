from datetime import datetime, timezone
from uuid import uuid4

from pydantic import BaseModel, Field

from app.models.project import QuestionItem


class QuestionBankItem(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    source_project_id: str
    source_question_id: str
    owner_account_id: str | None = None
    content_fingerprint: str
    question_snapshot: QuestionItem
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )


class QuestionBankListResponse(BaseModel):
    items: list[QuestionBankItem]
    total: int


class QuestionBankSearchResponse(BaseModel):
    items: list[QuestionBankItem]
    total: int
    query: str | None = None
    grade: int | None = None
    science_domain: str | None = None
    unit_id: str | None = None
    cognitive_category: str | None = None


class QuestionBankReuseResponse(BaseModel):
    target_project_id: str
    source_bank_item_id: str
    reused: bool
    question: QuestionItem
