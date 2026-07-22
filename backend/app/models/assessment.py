from datetime import datetime, timezone
from enum import Enum
from uuid import uuid4

from pydantic import BaseModel, Field

from app.models.project import CognitiveCategory


class AssessmentStatus(str, Enum):
    draft = "draft"
    ready = "ready"


class AssessmentBlueprint(BaseModel):
    title: str = "اختبار جديد"
    grade: int = Field(default=10, ge=1, le=12)
    science_domain: str = "physics"
    subject_id: str = "g10-physics"
    semester_id: str | None = None
    unit_id: str | None = None
    duration_minutes: int = Field(default=40, ge=5, le=240)
    total_marks: int = Field(default=20, ge=1, le=200)
    target_question_count: int = Field(default=10, ge=1, le=100)
    knowledge_percent: int = Field(default=30, ge=0, le=100)
    application_percent: int = Field(default=40, ge=0, le=100)
    reasoning_percent: int = Field(default=30, ge=0, le=100)

    def cognitive_percent_total(self) -> int:
        return (
            self.knowledge_percent
            + self.application_percent
            + self.reasoning_percent
        )


class AssessmentSection(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    title: str = "القسم الأول"
    instructions: str | None = None
    order_index: int = Field(default=1, ge=1)


class AssessmentItemConfiguration(BaseModel):
    bank_item_id: str
    section_id: str | None = None
    order_index: int = Field(default=1, ge=1)
    marks_override: int | None = Field(
        default=None,
        ge=0,
        le=200,
    )


class AssessmentLayoutUpdate(BaseModel):
    sections: list[AssessmentSection] = Field(
        default_factory=list
    )
    item_configurations: list[
        AssessmentItemConfiguration
    ] = Field(default_factory=list)


class AssessmentDraft(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    owner_account_id: str | None = None
    source_project_id: str | None = None
    blueprint: AssessmentBlueprint = Field(
        default_factory=AssessmentBlueprint
    )
    question_bank_item_ids: list[str] = Field(default_factory=list)
    sections: list[AssessmentSection] = Field(
        default_factory=lambda: [AssessmentSection()]
    )
    item_configurations: list[
        AssessmentItemConfiguration
    ] = Field(default_factory=list)
    status: AssessmentStatus = AssessmentStatus.draft
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )


class AssessmentDraftCreateRequest(BaseModel):
    source_project_id: str | None = None
    blueprint: AssessmentBlueprint = Field(
        default_factory=AssessmentBlueprint
    )


class AssessmentDraftListResponse(BaseModel):
    items: list[AssessmentDraft]
    total: int


class AssessmentQuestionSummary(BaseModel):
    section_id: str | None = None
    order_index: int = 1
    source_marks: int = 0
    marks_override: int | None = None
    bank_item_id: str
    question_number: str
    text: str
    marks: int
    cognitive_category: CognitiveCategory
    grade: int | None = None
    unit_id: str | None = None


class AssessmentBalanceSummary(BaseModel):
    selected_question_count: int
    selected_marks: int
    remaining_question_count: int
    remaining_marks: int
    knowledge_count: int
    application_count: int
    reasoning_count: int
    unclassified_count: int
    knowledge_percent: float
    application_percent: float
    reasoning_percent: float
    question_target_met: bool
    marks_target_met: bool
    cognitive_targets_valid: bool


class AssessmentDraftDetail(BaseModel):
    draft: AssessmentDraft
    questions: list[AssessmentQuestionSummary]
    balance: AssessmentBalanceSummary


class AssessmentBlueprintValidation(BaseModel):
    ready: bool
    total_selected_questions: int
    target_questions: int
    total_selected_marks: int
    target_marks: int
    knowledge_selected: int
    knowledge_target: int
    application_selected: int
    application_target: int
    reasoning_selected: int
    reasoning_target: int
    unclassified_selected: int
    issues: list[str] = Field(default_factory=list)


class AssessmentAutoSelectionResponse(BaseModel):
    detail: AssessmentDraftDetail
    validation: AssessmentBlueprintValidation
    selected_item_ids: list[str]
    skipped_item_ids: list[str]
    shortages: list[str] = Field(default_factory=list)
