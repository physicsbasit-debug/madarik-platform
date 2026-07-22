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


class MarksPolicy(str, Enum):
    unresolved = "unresolved"
    use_question_total = "use_question_total"
    scale_to_declared = "scale_to_declared"


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


class TranslationOutcomeStatus(str, Enum):
    external_success = "external_success"
    corrected_success = "corrected_success"
    local_fallback = "local_fallback"
    skipped = "skipped"
    failed_safely = "failed_safely"


class TranslationItemType(str, Enum):
    question = "question"
    part = "part"


class TranslationBatchStatus(str, Enum):
    completed = "completed"
    completed_with_fallbacks = "completed_with_fallbacks"
    completed_with_failures = "completed_with_failures"


class FullExamIntakeStatus(str, Enum):
    accepted = "accepted"
    needs_review = "needs_review"
    rejected = "rejected"


class FullExamTranslationAcceptanceStatus(str, Enum):
    accepted = "accepted"
    needs_review = "needs_review"
    incomplete = "incomplete"
    failed = "failed"


class FullExamTranslationQuestionStatus(str, Enum):
    accepted = "accepted"
    needs_review = "needs_review"
    untranslated = "untranslated"
    failed = "failed"
    deleted = "deleted"


class FullExamExportAcceptanceStatus(str, Enum):
    accepted = "accepted"
    needs_review = "needs_review"
    incomplete = "incomplete"
    failed = "failed"


class FullExamExportArtifactStatus(str, Enum):
    accepted = "accepted"
    needs_review = "needs_review"
    failed = "failed"


class FullExamEndToEndAcceptanceStatus(str, Enum):
    accepted = "accepted"
    needs_review = "needs_review"
    rejected = "rejected"


class FullExamEndToEndStageStatus(str, Enum):
    accepted = "accepted"
    needs_review = "needs_review"
    pending = "pending"
    failed = "failed"
    skipped = "skipped"


class FullExamEndToEndStageKey(str, Enum):
    intake = "intake"
    layout_assets = "layout_assets"
    glossary = "glossary"
    translation = "translation"
    readiness = "readiness"
    docx_export = "docx_export"
    pdf_export = "pdf_export"
    final_consistency = "final_consistency"


class PdfPageKind(str, Enum):
    cover = "cover"
    question = "question"
    blank = "blank"
    other = "other"


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
    marks_policy: MarksPolicy = MarksPolicy.unresolved
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


class PdfLayoutAssetInfo(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    name: str
    size: int = Field(ge=0)
    type: str = "image/png"
    data_base64: str
    page_number: int = Field(ge=1)
    source: str = "page_snapshot"
    note: str = ""


class ExtractedPdfPageInfo(BaseModel):
    """Selectable text retained for one PDF page."""

    page_number: int = Field(ge=1)
    text: str = ""
    character_count: int = Field(default=0, ge=0)
    is_text_empty: bool = False


class ExtractedTextInfo(BaseModel):
    text: str = ""
    preview: str = ""
    page_count: int = Field(default=0, ge=0)
    character_count: int = Field(default=0, ge=0)
    is_text_based: bool = False
    message: str = ""
    pages: list[ExtractedPdfPageInfo] = Field(default_factory=list)


class QuestionOption(BaseModel):
    label: str
    text: str


class QuestionPart(BaseModel):
    """One structured part of a multipart exam question."""

    id: str = Field(default_factory=lambda: str(uuid4()))
    label: str
    original_text: str
    translated_text: str = ""
    marks: int | None = None
    parent_id: str | None = None
    order_index: int = Field(ge=1)


class QuestionItem(BaseModel):
    id: str
    original_number: str
    original_text: str
    translated_text: str
    raw_text: str | None = None
    marks: int | None = None
    detected_marks: int | None = None
    status: QuestionStatus = QuestionStatus.approved
    order_index: int
    attachment_note: str | None = None
    attachments: list[QuestionAssetInfo] = Field(default_factory=list)
    linked_layout_asset_ids: list[str] = Field(default_factory=list)
    options: list[QuestionOption] = Field(default_factory=list)
    parts: list[QuestionPart] = Field(default_factory=list)
    source_page_numbers: list[int] = Field(default_factory=list)
    source_page_start: int | None = Field(default=None, ge=1)
    source_page_end: int | None = Field(default=None, ge=1)
    review_notes: str | None = None


class GlossaryTerm(BaseModel):
    id: str
    english_term: str
    arabic_term: str
    subject: str = ""
    status: GlossaryTermStatus = GlossaryTermStatus.approved
    source: GlossaryTermSource = GlossaryTermSource.mock
    notes: str | None = None


class TranslationItemOutcome(BaseModel):
    question_id: str
    question_number: str = ""
    item_type: TranslationItemType = TranslationItemType.question
    part_id: str | None = None
    part_label: str | None = None
    status: TranslationOutcomeStatus
    provider: str = "mock"
    used_external_provider: bool = False
    urgent_review: bool = False
    message: str = ""


class TranslationBatchSummary(BaseModel):
    status: TranslationBatchStatus
    total_questions: int = Field(default=0, ge=0)
    active_questions: int = Field(default=0, ge=0)
    deleted_questions: int = Field(default=0, ge=0)
    total_items: int = Field(default=0, ge=0)
    external_success_count: int = Field(default=0, ge=0)
    corrected_success_count: int = Field(default=0, ge=0)
    local_fallback_count: int = Field(default=0, ge=0)
    skipped_count: int = Field(default=0, ge=0)
    failed_safely_count: int = Field(default=0, ge=0)
    urgent_review_count: int = Field(default=0, ge=0)
    items: list[TranslationItemOutcome] = Field(default_factory=list)


class FullExamTranslationQuestionSummary(BaseModel):
    question_id: str
    question_number: str
    status: FullExamTranslationQuestionStatus
    total_items: int = Field(default=0, ge=0)
    translated_items: int = Field(default=0, ge=0)
    urgent_review_items: int = Field(default=0, ge=0)
    failed_items: int = Field(default=0, ge=0)
    glossary_violation_count: int = Field(default=0, ge=0)
    fidelity_violation_count: int = Field(default=0, ge=0)
    language_quality_violation_count: int = Field(default=0, ge=0)
    source_page_numbers: list[int] = Field(default_factory=list)
    linked_layout_asset_count: int = Field(default=0, ge=0)
    message: str = ""


class FullExamTranslationCheck(BaseModel):
    code: str
    passed: bool
    message: str


class FullExamTranslationReport(BaseModel):
    status: FullExamTranslationAcceptanceStatus
    total_questions: int = Field(default=0, ge=0)
    active_questions: int = Field(default=0, ge=0)
    deleted_questions: int = Field(default=0, ge=0)
    translated_questions: int = Field(default=0, ge=0)
    accepted_questions: int = Field(default=0, ge=0)
    needs_review_questions: int = Field(default=0, ge=0)
    untranslated_questions: int = Field(default=0, ge=0)
    failed_questions: int = Field(default=0, ge=0)
    completion_percent: float = Field(default=0, ge=0, le=100)
    total_items: int = Field(default=0, ge=0)
    translated_items: int = Field(default=0, ge=0)
    urgent_review_items: int = Field(default=0, ge=0)
    glossary_violation_count: int = Field(default=0, ge=0)
    fidelity_violation_count: int = Field(default=0, ge=0)
    language_quality_violation_count: int = Field(default=0, ge=0)
    source_page_linked_questions: int = Field(default=0, ge=0)
    multi_page_questions: int = Field(default=0, ge=0)
    questions: list[FullExamTranslationQuestionSummary] = Field(default_factory=list)
    checks: list[FullExamTranslationCheck] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)


class FullExamExportCheck(BaseModel):
    code: str
    passed: bool
    message: str


class FullExamExportFormatSummary(BaseModel):
    format: ExportFormat
    status: FullExamExportArtifactStatus
    byte_size: int = Field(default=0, ge=0)
    page_count: int | None = Field(default=None, ge=1)
    exported_question_count: int = Field(default=0, ge=0)
    exported_part_count: int = Field(default=0, ge=0)
    exported_attachment_count: int = Field(default=0, ge=0)
    detected_total_marks: int = Field(default=0, ge=0)
    question_order: list[str] = Field(default_factory=list)
    checks: list[FullExamExportCheck] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)


class FullExamExportReport(BaseModel):
    status: FullExamExportAcceptanceStatus
    requested_formats: list[ExportFormat] = Field(default_factory=list)
    generated_formats: list[ExportFormat] = Field(default_factory=list)
    accepted_formats: list[ExportFormat] = Field(default_factory=list)
    needs_review_formats: list[ExportFormat] = Field(default_factory=list)
    failed_formats: list[ExportFormat] = Field(default_factory=list)
    active_question_count: int = Field(default=0, ge=0)
    expected_total_marks: int = Field(default=0, ge=0)
    expected_part_count: int = Field(default=0, ge=0)
    expected_attachment_count: int = Field(default=0, ge=0)
    source_page_linked_questions: int = Field(default=0, ge=0)
    multi_page_questions: int = Field(default=0, ge=0)
    formats: list[FullExamExportFormatSummary] = Field(default_factory=list)
    checks: list[FullExamExportCheck] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)


class FullExamEndToEndCheck(BaseModel):
    code: str
    passed: bool
    message: str


class FullExamEndToEndStageSummary(BaseModel):
    stage: FullExamEndToEndStageKey
    status: FullExamEndToEndStageStatus
    duration_ms: float = Field(default=0, ge=0)
    message: str = ""
    checks: list[FullExamEndToEndCheck] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    errors: list[str] = Field(default_factory=list)


class FullExamEndToEndReport(BaseModel):
    status: FullExamEndToEndAcceptanceStatus
    run_id: str = Field(default_factory=lambda: str(uuid4()))
    generated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    total_duration_ms: float = Field(default=0, ge=0)
    page_count: int = Field(default=0, ge=0)
    active_question_count: int = Field(default=0, ge=0)
    total_marks: int = Field(default=0, ge=0)
    translation_completion_percent: float = Field(
        default=0,
        ge=0,
        le=100,
    )
    requested_formats: list[ExportFormat] = Field(default_factory=list)
    generated_formats: list[ExportFormat] = Field(default_factory=list)
    accepted_formats: list[ExportFormat] = Field(default_factory=list)
    stages: list[FullExamEndToEndStageSummary] = Field(default_factory=list)
    checks: list[FullExamEndToEndCheck] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    errors: list[str] = Field(default_factory=list)


class FullExamPageSummary(BaseModel):
    page_number: int = Field(ge=1)
    kind: PdfPageKind
    character_count: int = Field(default=0, ge=0)
    question_numbers: list[str] = Field(default_factory=list)
    visual_reference_count: int = Field(default=0, ge=0)


class FullExamQuestionSpan(BaseModel):
    question_number: str
    page_numbers: list[int] = Field(default_factory=list)
    page_start: int = Field(ge=1)
    page_end: int = Field(ge=1)
    detected_total_marks: int | None = Field(default=None, ge=0)
    visual_reference_count: int = Field(default=0, ge=0)
    linked_layout_asset_count: int = Field(default=0, ge=0)


class FullExamIntakeCheck(BaseModel):
    code: str
    passed: bool
    message: str


class FullExamIntakeReport(BaseModel):
    status: FullExamIntakeStatus
    page_count: int = Field(default=0, ge=0)
    content_page_count: int = Field(default=0, ge=0)
    blank_page_count: int = Field(default=0, ge=0)
    cover_page_count: int = Field(default=0, ge=0)
    question_page_count: int = Field(default=0, ge=0)
    detected_question_count: int = Field(default=0, ge=0)
    detected_question_numbers: list[str] = Field(default_factory=list)
    reported_total_marks: int | None = Field(default=None, ge=0)
    detected_total_marks: int | None = Field(default=None, ge=0)
    multi_page_question_count: int = Field(default=0, ge=0)
    visual_reference_count: int = Field(default=0, ge=0)
    auto_linked_layout_asset_count: int = Field(default=0, ge=0)
    pages: list[FullExamPageSummary] = Field(default_factory=list)
    question_spans: list[FullExamQuestionSpan] = Field(default_factory=list)
    checks: list[FullExamIntakeCheck] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)


class AnswerKeyItem(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    question_id: str
    question_number: str
    draft_answer: str
    marks: int | None = None
    confidence: str = "low"
    source: str = "draft"
    needs_review: bool = True
    notes: str = "مسودة نموذج إجابة آلية تحتاج مراجعة المعلم."


class EducationalAnalysisReport(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    question_count: int = Field(default=0, ge=0)
    total_marks: int = Field(default=0, ge=0)
    average_marks: float = Field(default=0, ge=0)
    translated_question_count: int = Field(default=0, ge=0)
    answer_key_items_count: int = Field(default=0, ge=0)
    layout_assets_count: int = Field(default=0, ge=0)
    command_distribution: dict[str, int] = Field(default_factory=dict)
    marks_distribution: dict[str, int] = Field(default_factory=dict)
    review_load: str = "low"
    educational_summary: str = ""
    recommendations: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    needs_review: bool = True


class EducationalQualityToolsReport(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    pareto_items: list[dict[str, float | int | str]] = Field(default_factory=list)
    radar_axes: dict[str, float] = Field(default_factory=dict)
    fishbone_causes: dict[str, list[str]] = Field(default_factory=dict)
    quality_summary: str = ""
    priority_actions: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    needs_review: bool = True



class CurriculumSourceAttachment(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    provider: str
    source_file_id: str
    file_name: str
    mime_type: str
    size_bytes: int | None = None
    checksum: str | None = None
    grade: int = Field(ge=1, le=12)
    science_domain: str
    semester_id: str
    subject_id: str
    unit_id: str | None = None
    source_document_type: str = "other"
    imported_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    source_modified_at: datetime | None = None
    source_refresh_status: str = "unknown"
    last_checked_at: datetime | None = None
    refresh_message: str | None = None


class ProjectSession(BaseModel):
    curriculum_sources: list[CurriculumSourceAttachment] = Field(default_factory=list)
    id: str = Field(default_factory=lambda: str(uuid4()))
    owner_account_id: str | None = None
    metadata: ProjectMetadata = Field(default_factory=ProjectMetadata)
    uploaded_file: UploadedFileInfo | None = None
    school_logo: ProjectLogoInfo | None = None
    extracted_text: ExtractedTextInfo | None = None
    questions: list[QuestionItem] = Field(default_factory=list)
    glossary: list[GlossaryTerm] = Field(default_factory=list)
    layout_assets: list[PdfLayoutAssetInfo] = Field(default_factory=list)
    answer_key: list[AnswerKeyItem] = Field(default_factory=list)
    educational_analysis: EducationalAnalysisReport | None = None
    quality_tools: EducationalQualityToolsReport | None = None
    translation_batch_summary: TranslationBatchSummary | None = None
    full_exam_intake_report: FullExamIntakeReport | None = None
    full_exam_translation_report: FullExamTranslationReport | None = None
    full_exam_export_report: FullExamExportReport | None = None
    full_exam_end_to_end_report: FullExamEndToEndReport | None = None
    current_step: StepKey = StepKey.setup
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class StepUpdate(BaseModel):
    current_step: StepKey


class QuestionPatch(BaseModel):
    translated_text: str | None = None
    marks: int | None = None
    status: QuestionStatus | None = None
    parts: list[QuestionPart] | None = None
    review_notes: str | None = None


class QuestionReorderRequest(BaseModel):
    ordered_question_ids: list[str]


class QuestionBulkStatusRequest(BaseModel):
    status: QuestionStatus
    include_deleted: bool = False


class GlossaryTermPatch(BaseModel):
    arabic_term: str | None = None
    status: GlossaryTermStatus | None = None
    notes: str | None = None


class ReadinessSeverity(str, Enum):
    error = "error"
    warning = "warning"


class ProjectReadinessIssue(BaseModel):
    code: str
    severity: ReadinessSeverity
    message: str


class ProjectReadinessReport(BaseModel):
    ready: bool
    exportable_question_count: int = Field(default=0, ge=0)
    translated_question_count: int = Field(default=0, ge=0)
    deleted_question_count: int = Field(default=0, ge=0)
    total_marks: int = Field(default=0, ge=0)
    issues: list[ProjectReadinessIssue] = Field(default_factory=list)


class VisualCropRequest(BaseModel):
    """Normalized crop coordinates for one PDF layout snapshot."""

    x: float = Field(ge=0, lt=1)
    y: float = Field(ge=0, lt=1)
    width: float = Field(gt=0, le=1)
    height: float = Field(gt=0, le=1)
    name: str | None = Field(default=None, max_length=120)
