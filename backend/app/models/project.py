from datetime import datetime, timezone
from enum import Enum
from uuid import uuid4

from pydantic import BaseModel, Field


class OutputMode(str, Enum):
    arabic = "arabic"
    bilingual = "bilingual"


class ExportFormat(str, Enum):
    docx = "docx"
    pdf = "pdf"


class QuestionStatus(str, Enum):
    approved = "approved"
    needs_review = "needs_review"
    deleted = "deleted"


class GlossaryTermStatus(str, Enum):
    approved = "approved"
    needs_review = "needs_review"


class GlossaryTermSource(str, Enum):
    mock = "mock"
    manual = "manual"
    detected = "detected"


class StepKey(str, Enum):
    setup = "setup"
    upload = "upload"
    extract = "extract"
    glossary = "glossary"
    review = "review"
    export = "export"


class ProjectMetadata(BaseModel):
    school_name: str = ""
    directorate: str = ""
    subject: str = ""
    grade: str = ""
    semester: str = ""
    paper_title: str = ""
    duration: str = ""
    total_marks: str = ""
    teacher_name: str = ""
    date: str = ""
    output_mode: OutputMode = OutputMode.arabic
    export_formats: list[ExportFormat] = Field(default_factory=lambda: [ExportFormat.docx, ExportFormat.pdf])


class UploadedFileInfo(BaseModel):
    name: str
    size: int = Field(ge=0)
    type: str = "غير معروف"


class ProjectLogoInfo(BaseModel):
    name: str
    size: int = Field(ge=0)
    type: str
    data_base64: str


class QuestionAssetInfo(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    name: str
    size: int = Field(ge=0)
    type: str
    data_base64: str


class ExtractedTextInfo(BaseModel):
    text: str = ""
    preview: str = ""
    page_count: int = Field(default=0, ge=0)
    character_count: int = Field(default=0, ge=0)
    is_text_based: bool = False
    message: str = ""


class QuestionItem(BaseModel):
    id: str
    original_number: str
    original_text: str
    translated_text: str
    marks: int | None = None
    detected_marks: int | None = None
    status: QuestionStatus = QuestionStatus.approved
    order_index: int
    attachment_note: str | None = None
    attachments: list[QuestionAssetInfo] = Field(default_factory=list)
    review_notes: str | None = None


class GlossaryTerm(BaseModel):
    id: str
    english_term: str
    arabic_term: str
    subject: str = ""
    status: GlossaryTermStatus = GlossaryTermStatus.approved
    source: GlossaryTermSource = GlossaryTermSource.mock
    notes: str | None = None


class ProjectSession(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    metadata: ProjectMetadata = Field(default_factory=ProjectMetadata)
    uploaded_file: UploadedFileInfo | None = None
    school_logo: ProjectLogoInfo | None = None
    extracted_text: ExtractedTextInfo | None = None
    questions: list[QuestionItem] = Field(default_factory=list)
    glossary: list[GlossaryTerm] = Field(default_factory=list)
    current_step: StepKey = StepKey.setup
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class StepUpdate(BaseModel):
    current_step: StepKey


class QuestionPatch(BaseModel):
    translated_text: str | None = None
    marks: int | None = None
    status: QuestionStatus | None = None
    review_notes: str | None = None


class QuestionReorderRequest(BaseModel):
    ordered_question_ids: list[str]


class GlossaryTermPatch(BaseModel):
    arabic_term: str | None = None
    status: GlossaryTermStatus | None = None
    notes: str | None = None
