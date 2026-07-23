import base64
from fastapi.responses import FileResponse
from fastapi import APIRouter, Depends, File, Header, HTTPException, UploadFile, status
from fastapi.responses import Response

from app.models.assessment import (
    AssessmentStudentPaperPreview,
    AssessmentExportResponse,
    AssessmentAutoSelectionResponse,
    AssessmentBlueprintValidation,
    AssessmentBlueprint,
    AssessmentDraft,
    AssessmentDraftCreateRequest,
    AssessmentDraftDetail,
    AssessmentLayoutUpdate,
    AssessmentDraftListResponse,
)
from app.services.assessment_export import (
    build_student_paper_preview,
    export_assessment_foundation,
)
from app.services.assessment_builder import (
    auto_select_questions_for_assessment,
    validate_assessment_blueprint,
    AssessmentBlueprintError,
    build_assessment_detail,
    validate_blueprint,
)
from app.services.assessment_repository import assessment_repository
from app.models.auth import AccountRole, AuthAccountPublic
from app.models.question_bank import (
    QuestionBankItem,
    QuestionBankListResponse,
    QuestionBankSearchResponse,
    QuestionBankReuseResponse,
)
from app.services.question_bank_reuse import (
    reuse_question_bank_item,
)
from app.services.question_bank_repository import (
    question_bank_repository,
)
from app.models.differentiated_activity import (
    DifferentiatedActivity,
    DifferentiatedActivityCreateRequest,
    DifferentiatedActivityListResponse,
    DifferentiatedActivityGenerationRequest,
    DifferentiatedActivityGenerationResponse,
    DifferentiatedActivityPreview,
    DifferentiatedActivityExportResponse,
)
from app.services.differentiated_activity_export import (
    build_activity_preview,
    export_activity,
)
from app.services.differentiated_activity_generator import (
    generate_differentiated_activity_set,
)
from app.services.differentiated_activity_repository import (
    differentiated_activity_repository,
)
from app.models.scientific_diagram import (
    ScientificDiagram,
    ScientificDiagramCreateRequest,
    ScientificDiagramListResponse,
    ScientificDiagramPreview,
    ScientificDiagramSvgExportResponse,
    ScientificDiagramBinaryExportResponse,
)
from app.services.scientific_diagram_renderer import (
    build_scientific_diagram_preview,
    export_scientific_diagram_svg,
    export_scientific_diagram_binary,
)
from app.services.scientific_diagram_repository import (
    scientific_diagram_repository,
)
from app.models.cloud_source import (
    CloudSource,
    CloudSourceCreateRequest,
    CloudSourceListResponse,
    OneDriveProviderStatus,
    CloudSourceSyncResponse,
    CloudSourceType,
)
from app.services.cloud_source_repository import (
    cloud_source_repository,
)
from app.services.onedrive_graph_adapter import (
    OneDriveConfigurationError,
    OneDriveGraphError,
    get_onedrive_provider_status,
    synchronize_onedrive_source,
)
from app.services.onedrive_source_parser import (
    parse_onedrive_source_url,
)
from app.models.project import (
    ExportFormat,
    ExtractedPdfPageInfo,
    FullExamEndToEndReport,
    FullExamExportReport,
    ExtractedTextInfo,
    GlossaryTermPatch,
    ProjectMetadata,
    ProjectLogoInfo,
    ProjectReadinessReport,
    ProjectSession,
    QuestionPatch,
    QuestionAssetInfo,
    QuestionStatus,
    QuestionBulkStatusRequest,
    QuestionReorderRequest,
    StepUpdate,
    UploadedFileInfo,
)
from app.services.auth_repository import auth_repository
from app.services.session_store import project_store
from app.services.glossary import extract_glossary_terms_from_questions
from app.services.question_parser import parse_questions_from_text
from app.services.full_exam_intake import (
    build_full_exam_intake_report,
    link_layout_assets_to_page_aware_questions,
    parse_full_exam_questions_from_pages,
)
from app.services.full_exam_translation import (
    build_full_exam_translation_report,
)
from app.services.text_extraction import TextExtractionError, extract_text_from_pdf_bytes
from app.services.ocr import OcrExtractionError, extract_text_from_image_bytes
from app.services.pdf_ocr import PdfOcrExtractionError, extract_text_from_scanned_pdf_bytes
from app.services.pdf_layout_assets import PdfLayoutAssetExtractionError, extract_pdf_layout_assets_from_bytes
from app.services.translation import (
    merge_translation_retry_summary,
    translate_questions_batch_with_glossary,
)
from app.services.readiness import build_project_readiness_report
from app.services.ai_provider import get_ai_provider_status
from app.services.answer_key import build_answer_key_draft
from app.services.educational_analysis import build_educational_analysis
from app.services.quality_tools import build_quality_tools_report
from app.services.full_exam_export import build_full_exam_export_report
from app.services.full_exam_end_to_end import (
    run_full_exam_end_to_end_acceptance,
)
from app.services.export import (
    DOCX_MIME_TYPE,
    PDF_MIME_TYPE,
    build_project_docx_bytes,
    build_project_pdf_bytes,
    safe_docx_filename,
    safe_pdf_filename,
)
from uuid import uuid4
from app.models.project import VisualCropRequest
from app.services.visual_crop import VisualCropError, crop_image_base64

def _extract_bearer_token(authorization: str | None) -> str | None:
    if not authorization:
        return None
    scheme, _, token = authorization.partition(" ")
    if scheme.lower() != "bearer" or not token:
        return None
    return token.strip()


def _resolve_current_account(authorization: str | None = Header(default=None)) -> AuthAccountPublic | None:
    token = _extract_bearer_token(authorization)
    return auth_repository.get_account_by_token(token) if token else None


def _has_project_access(project: ProjectSession, account: AuthAccountPublic | None) -> bool:
    if project.owner_account_id is None:
        return True
    if account is None:
        return False
    if account.role == AccountRole.owner:
        return True
    return project.owner_account_id == account.id


def _require_project_access(project: ProjectSession, account: AuthAccountPublic | None) -> ProjectSession:
    if not _has_project_access(project, account):
        raise HTTPException(status_code=403, detail="لا تملك صلاحية الوصول إلى هذا المشروع.")
    return project


MAX_LAYOUT_ASSET_PAGES_PER_UPLOAD = 24


router = APIRouter(prefix="/projects", tags=["projects"])


@router.get("/translation-provider/status")
def get_translation_provider_status() -> dict[str, object]:
    """Return safe AI provider metadata without exposing secrets."""

    return get_ai_provider_status()


def _get_or_404(project_id: str, account: AuthAccountPublic | None) -> ProjectSession:
    project = project_store.get(project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    return _require_project_access(project, account)



@router.get("")
def list_projects(limit: int = 50, account: AuthAccountPublic | None = Depends(_resolve_current_account)) -> list[ProjectSession]:
    """List accessible persisted projects for Phase 2-B2."""

    account = account
    include_all = account is not None and account.role == AccountRole.owner
    account_id = account.id if account is not None else None
    return project_store.list_recent(limit, account_id=account_id, include_all=include_all)


@router.post("", status_code=status.HTTP_201_CREATED)
def create_project(metadata: ProjectMetadata | None = None, account: AuthAccountPublic | None = Depends(_resolve_current_account)) -> ProjectSession:
    """Create a project and attach ownership when an account session is present."""

    account = account
    return project_store.create(metadata, owner_account_id=account.id if account else None)


@router.get("/{project_id}")
def get_project(project_id: str, account: AuthAccountPublic | None = Depends(_resolve_current_account)) -> ProjectSession:
    """Return a temporary project session."""

    return _get_or_404(project_id, account)



@router.get("/{project_id}/snapshot")
def export_project_snapshot(project_id: str, account: AuthAccountPublic | None = Depends(_resolve_current_account)) -> ProjectSession:
    """Return the current temporary project as a JSON snapshot for Phase 1-M1."""

    return _get_or_404(project_id, account)


@router.post("/import-snapshot", status_code=status.HTTP_201_CREATED)
def import_project_snapshot(snapshot: ProjectSession, account: AuthAccountPublic | None = Depends(_resolve_current_account)) -> ProjectSession:
    """Import a JSON snapshot as a new project owned by the current account when present."""

    account = account
    return project_store.import_snapshot(snapshot, owner_account_id=account.id if account else None)


@router.patch("/{project_id}/metadata")
def update_project_metadata(project_id: str, metadata: ProjectMetadata, account: AuthAccountPublic | None = Depends(_resolve_current_account)) -> ProjectSession:
    """Update project metadata from the frontend setup step."""

    _get_or_404(project_id, account)
    project = project_store.update_metadata(project_id, metadata)
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


@router.patch("/{project_id}/step")
def update_project_step(project_id: str, payload: StepUpdate, account: AuthAccountPublic | None = Depends(_resolve_current_account)) -> ProjectSession:
    """Remember the current frontend step in the temporary session."""

    project = _get_or_404(project_id, account)
    project.current_step = payload.current_step
    return project_store.touch(project_id) or project


@router.put("/{project_id}/upload-info")
def set_upload_info(project_id: str, uploaded_file: UploadedFileInfo | None = None, account: AuthAccountPublic | None = Depends(_resolve_current_account)) -> ProjectSession:
    """Store file metadata only. No real file upload is performed in Phase 1-B."""

    _get_or_404(project_id, account)
    project = project_store.set_uploaded_file(project_id, uploaded_file)
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    return project




@router.post("/{project_id}/school-logo")
async def upload_school_logo(project_id: str, file: UploadFile = File(...), account: AuthAccountPublic | None = Depends(_resolve_current_account)) -> ProjectSession:
    """Store an optional school logo in the temporary project session for Phase 1-F3."""

    _get_or_404(project_id, account)

    filename = file.filename or "school-logo"
    content_type = file.content_type or "application/octet-stream"
    allowed_types = {"image/png", "image/jpeg", "image/jpg"}
    if content_type not in allowed_types:
        raise HTTPException(status_code=400, detail="يدعم شعار المدرسة ملفات PNG وJPG فقط في هذه المرحلة.")

    file_bytes = await file.read()
    max_size = 1_500_000
    if len(file_bytes) > max_size:
        raise HTTPException(status_code=400, detail="حجم الشعار كبير. الحد الأقصى المؤقت هو 1.5MB.")

    logo = ProjectLogoInfo(
        name=filename,
        size=len(file_bytes),
        type=content_type,
        data_base64=base64.b64encode(file_bytes).decode("ascii"),
    )
    project = project_store.set_school_logo(project_id, logo)
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


@router.delete("/{project_id}/school-logo")
def delete_school_logo(project_id: str, account: AuthAccountPublic | None = Depends(_resolve_current_account)) -> ProjectSession:
    """Remove the optional school logo from the temporary project session."""

    _get_or_404(project_id, account)
    project = project_store.set_school_logo(project_id, None)
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


@router.post("/{project_id}/upload-pdf")
async def upload_pdf_and_extract_text(project_id: str, file: UploadFile = File(...), account: AuthAccountPublic | None = Depends(_resolve_current_account)) -> ProjectSession:
    """Upload a real text-based PDF and extract selectable text for Phase 1-C."""

    _get_or_404(project_id, account)

    filename = file.filename or "uploaded.pdf"
    if not filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="يدعم هذا المسار ملفات PDF فقط في Phase 1-C.")

    file_bytes = await file.read()
    uploaded_file = UploadedFileInfo(name=filename, size=len(file_bytes), type=file.content_type or "application/pdf")

    try:
        result = extract_text_from_pdf_bytes(file_bytes)
    except TextExtractionError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    extracted_pages = [
        ExtractedPdfPageInfo(
            page_number=page.page_number,
            text=page.text,
            character_count=page.character_count,
            is_text_empty=page.is_text_empty,
        )
        for page in result.pages
    ]
    intake_report = build_full_exam_intake_report(extracted_pages)

    if not result.is_text_based:
        extracted_text = ExtractedTextInfo(
            text="",
            preview="",
            page_count=result.page_count,
            character_count=0,
            is_text_based=False,
            message="لم يتم العثور على نص قابل للاستخراج. يبدو أن الملف PDF مصوّر أو ممسوح ضوئيًا، وسيحتاج OCR في مرحلة لاحقة.",
            pages=extracted_pages,
        )
    else:
        extracted_text = ExtractedTextInfo(
            text=result.text,
            preview=result.preview,
            page_count=result.page_count,
            character_count=result.character_count,
            is_text_based=True,
            message=(
                "تم استخراج النص من PDF نصي مع الاحتفاظ بحدود الصفحات "
                "لبناء تقرير قبول الورقة الكاملة."
            ),
            pages=extracted_pages,
        )

    project = project_store.set_extracted_text(
        project_id,
        uploaded_file,
        extracted_text,
        full_exam_intake_report=intake_report,
    )
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


@router.post("/{project_id}/upload-pdf-ocr")
async def upload_scanned_pdf_and_extract_text(project_id: str, file: UploadFile = File(...), account: AuthAccountPublic | None = Depends(_resolve_current_account)) -> ProjectSession:
    """Upload a PDF and try OCR on its rendered pages for Phase 1-I2."""

    _get_or_404(project_id, account)

    filename = file.filename or "uploaded.pdf"
    if not filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="يدعم مسار OCR لملفات PDF فقط.")

    file_bytes = await file.read()
    max_size = 8_000_000
    if len(file_bytes) > max_size:
        raise HTTPException(status_code=400, detail="حجم PDF كبير. الحد الأقصى المؤقت لمسار OCR هو 8MB.")

    uploaded_file = UploadedFileInfo(name=filename, size=len(file_bytes), type=file.content_type or "application/pdf")

    try:
        result = extract_text_from_scanned_pdf_bytes(file_bytes)
    except PdfOcrExtractionError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    if not result.is_text_based:
        extracted_text = ExtractedTextInfo(
            text="",
            preview="",
            page_count=result.page_count,
            character_count=0,
            is_text_based=False,
            message=f"تم تشغيل OCR على {result.processed_pages} صفحة من PDF، لكن لم يظهر نص واضح. جرّب صورة أوضح أو PDF أعلى جودة.",
        )
    else:
        extracted_text = ExtractedTextInfo(
            text=result.text,
            preview=result.preview,
            page_count=result.page_count,
            character_count=result.character_count,
            is_text_based=True,
            message=f"تم استخراج النص من PDF مصوّر باستخدام OCR مبدئي على {result.processed_pages} صفحة.",
        )

    project = project_store.set_extracted_text(project_id, uploaded_file, extracted_text)
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


@router.post("/{project_id}/upload-image-ocr")
async def upload_image_and_extract_text(project_id: str, file: UploadFile = File(...), account: AuthAccountPublic | None = Depends(_resolve_current_account)) -> ProjectSession:
    """Upload an image and run English OCR for Phase 1-I2."""

    _get_or_404(project_id, account)

    filename = file.filename or "uploaded-image"
    content_type = file.content_type or "application/octet-stream"
    allowed_types = {"image/png", "image/jpeg", "image/jpg", "image/webp"}
    allowed_extensions = (".png", ".jpg", ".jpeg", ".webp")
    if content_type not in allowed_types and not filename.lower().endswith(allowed_extensions):
        raise HTTPException(status_code=400, detail="يدعم OCR في Phase 1-I2 صور PNG وJPG وWEBP فقط.")

    file_bytes = await file.read()
    max_size = 4_000_000
    if len(file_bytes) > max_size:
        raise HTTPException(status_code=400, detail="حجم الصورة كبير. الحد الأقصى المؤقت هو 4MB.")

    uploaded_file = UploadedFileInfo(name=filename, size=len(file_bytes), type=content_type)

    try:
        result = extract_text_from_image_bytes(file_bytes)
    except OcrExtractionError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    if not result.is_text_based:
        extracted_text = ExtractedTextInfo(
            text="",
            preview="",
            page_count=result.image_count,
            character_count=0,
            is_text_based=False,
            message="لم يتمكن OCR من العثور على نص واضح في الصورة. جرّب صورة أوضح أو قصّ السؤال فقط.",
        )
    else:
        extracted_text = ExtractedTextInfo(
            text=result.text,
            preview=result.preview,
            page_count=result.image_count,
            character_count=result.character_count,
            is_text_based=True,
            message="تم استخراج النص من الصورة باستخدام OCR إنجليزي مبدئي.",
        )

    project = project_store.set_extracted_text(project_id, uploaded_file, extracted_text)
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


@router.post("/{project_id}/layout-assets/pdf")
async def extract_pdf_layout_assets(project_id: str, file: UploadFile = File(...), account: AuthAccountPublic | None = Depends(_resolve_current_account)) -> ProjectSession:
    """Extract low-resolution PDF page layout snapshots for Phase 2-D1."""

    _get_or_404(project_id, account)

    filename = file.filename or "uploaded.pdf"
    if not filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="يدعم استخراج التخطيط ملفات PDF فقط.")

    file_bytes = await file.read()
    max_size = 8_000_000
    if len(file_bytes) > max_size:
        raise HTTPException(status_code=400, detail="حجم PDF كبير. الحد الأقصى المؤقت لاستخراج التخطيط هو 8MB.")

    try:
        result = extract_pdf_layout_assets_from_bytes(
            file_bytes,
            max_pages=MAX_LAYOUT_ASSET_PAGES_PER_UPLOAD,
        )
    except PdfLayoutAssetExtractionError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    project = project_store.set_layout_assets(project_id, result.assets)
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


@router.delete("/{project_id}/layout-assets/{asset_id}")
def delete_pdf_layout_asset(project_id: str, asset_id: str, account: AuthAccountPublic | None = Depends(_resolve_current_account)) -> ProjectSession:
    """Remove one PDF layout asset from the project."""

    _get_or_404(project_id, account)
    project = project_store.remove_layout_asset(project_id, asset_id)
    if project is None:
        raise HTTPException(status_code=404, detail="Project or layout asset not found")
    return project


@router.post(
    "/{project_id}/questions/{question_id}/layout-assets/{asset_id}"
)
def link_question_layout_asset(
    project_id: str,
    question_id: str,
    asset_id: str,
    account: AuthAccountPublic | None = Depends(_resolve_current_account),
) -> ProjectSession:
    """Link an existing PDF layout snapshot to one question."""

    _get_or_404(project_id, account)
    project = project_store.link_layout_asset_to_question(
        project_id,
        question_id,
        asset_id,
    )
    if project is None:
        raise HTTPException(
            status_code=404,
            detail="Project, question, or layout asset not found",
        )
    return project


@router.delete(
    "/{project_id}/questions/{question_id}/layout-assets/{asset_id}"
)
def unlink_question_layout_asset(
    project_id: str,
    question_id: str,
    asset_id: str,
    account: AuthAccountPublic | None = Depends(_resolve_current_account),
) -> ProjectSession:
    """Remove the link between one question and one layout snapshot."""

    _get_or_404(project_id, account)
    project = project_store.unlink_layout_asset_from_question(
        project_id,
        question_id,
        asset_id,
    )
    if project is None:
        raise HTTPException(
            status_code=404,
            detail="Project, question, or linked layout asset not found",
        )
    return project



@router.post(
    "/{project_id}/questions/{question_id}/layout-assets/{asset_id}/crop"
)
def crop_question_layout_asset(
    project_id: str,
    question_id: str,
    asset_id: str,
    payload: VisualCropRequest,
    account: AuthAccountPublic | None = Depends(_resolve_current_account),
) -> ProjectSession:
    """Crop one linked PDF page snapshot and save it as a question asset."""

    project = _get_or_404(project_id, account)

    question = next(
        (
            item
            for item in project.questions
            if item.id == question_id
        ),
        None,
    )
    if question is None:
        raise HTTPException(
            status_code=404,
            detail="Project or question not found",
        )

    source_asset = next(
        (
            item
            for item in project.layout_assets
            if item.id == asset_id
        ),
        None,
    )
    if source_asset is None:
        raise HTTPException(
            status_code=404,
            detail="PDF layout asset not found",
        )

    if asset_id not in question.linked_layout_asset_ids:
        raise HTTPException(
            status_code=400,
            detail="يجب ربط لقطة PDF بالسؤال قبل قص عنصر منها.",
        )

    try:
        crop_result = crop_image_base64(
            source_asset.data_base64,
            x=payload.x,
            y=payload.y,
            width=payload.width,
            height=payload.height,
        )
    except VisualCropError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    requested_name = (payload.name or "").strip()
    asset_name = (
        requested_name
        or f"pdf-crop-page-{source_asset.page_number}.png"
    )

    if not asset_name.lower().endswith(".png"):
        asset_name = f"{asset_name}.png"

    cropped_asset = QuestionAssetInfo(
        id=f"pdf-crop-{uuid4()}",
        name=asset_name,
        size=crop_result.size,
        type=crop_result.mime_type,
        data_base64=crop_result.data_base64,
    )

    updated_project = project_store.add_question_asset(
        project_id,
        question_id,
        cropped_asset,
    )
    if updated_project is None:
        raise HTTPException(
            status_code=404,
            detail="Project or question not found",
        )

    return updated_project


@router.post("/{project_id}/parse-questions")
def parse_extracted_questions(project_id: str, account: AuthAccountPublic | None = Depends(_resolve_current_account)) -> ProjectSession:
    """Convert extracted text into reviewable question cards for Phase 1-D."""

    project = _get_or_404(project_id, account)
    if project.extracted_text is None or not project.extracted_text.text.strip():
        raise HTTPException(status_code=400, detail="لا يوجد نص مستخرج يمكن تقسيمه إلى أسئلة.")
    if not project.extracted_text.is_text_based:
        raise HTTPException(status_code=400, detail="لا يمكن تقسيم PDF غير نصي في Phase 1-D. سيحتاج OCR لاحقًا.")

    used_page_aware_parser = False
    if project.extracted_text.pages:
        questions = parse_full_exam_questions_from_pages(project.extracted_text.pages)
        if questions:
            used_page_aware_parser = True
        else:
            # A text-based PDF can preserve page boundaries without being a full
            # exam paper. Keep the established Phase 1-D parser as a compatibility
            # fallback instead of rejecting simple one-page and synthetic test PDFs.
            questions = parse_questions_from_text(project.extracted_text.text)
            project.full_exam_intake_report = None
    else:
        questions = parse_questions_from_text(project.extracted_text.text)

    if not questions:
        raise HTTPException(status_code=400, detail="لم يتم العثور على أسئلة قابلة للتقسيم في النص المستخرج.")

    intake_report = None
    if used_page_aware_parser:
        questions = link_layout_assets_to_page_aware_questions(
            questions,
            project.layout_assets,
        )
        intake_report = build_full_exam_intake_report(
            project.extracted_text.pages,
            questions=questions,
        )

    updated_project = project_store.set_parsed_questions(
        project_id,
        questions,
        full_exam_intake_report=intake_report,
    )
    if updated_project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    return updated_project



@router.post("/{project_id}/glossary/generate")
def generate_project_glossary(project_id: str, account: AuthAccountPublic | None = Depends(_resolve_current_account)) -> ProjectSession:
    """Generate a teacher-review glossary from parsed question cards for Phase 1-E1."""

    project = _get_or_404(project_id, account)
    if not project.questions:
        raise HTTPException(status_code=400, detail="لا توجد بطاقات أسئلة يمكن استخراج مصطلحات منها.")

    detected_terms = extract_glossary_terms_from_questions(
        project.questions,
        default_subject=project.metadata.subject,
    )
    if not detected_terms:
        raise HTTPException(status_code=400, detail="لم يتم العثور على مصطلحات علمية ضمن قاموس Phase 1-E1 الأولي.")

    updated_project = project_store.set_glossary(project_id, detected_terms)
    if updated_project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    return updated_project


@router.post("/{project_id}/translate-questions")
def translate_project_questions(project_id: str, account: AuthAccountPublic | None = Depends(_resolve_current_account)) -> ProjectSession:
    """Translate a complete paper and build Phase 4-A6b acceptance."""

    project = _get_or_404(project_id, account)
    if not project.questions:
        raise HTTPException(status_code=400, detail="لا توجد أسئلة قابلة للترجمة.")

    batch_result = translate_questions_batch_with_glossary(
        project.questions,
        project.glossary,
        project.metadata,
    )
    translation_report = build_full_exam_translation_report(
        batch_result.questions,
        project.glossary,
        batch_result.summary,
        project.full_exam_intake_report,
    )
    updated_project = project_store.set_translated_questions(
        project_id,
        batch_result.questions,
        batch_result.summary,
        translation_report,
    )
    if updated_project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    return updated_project


@router.post("/{project_id}/questions/{question_id}/retry-translation")
def retry_project_question_translation(
    project_id: str,
    question_id: str,
    account: AuthAccountPublic | None = Depends(_resolve_current_account),
) -> ProjectSession:
    """Retry one active question without retranslating the whole paper."""

    project = _get_or_404(project_id, account)
    question = next(
        (
            item
            for item in project.questions
            if item.id == question_id
        ),
        None,
    )
    if question is None:
        raise HTTPException(
            status_code=404,
            detail="Project or question not found",
        )
    if question.status == QuestionStatus.deleted:
        raise HTTPException(
            status_code=400,
            detail="لا يمكن إعادة ترجمة سؤال محذوف.",
        )

    retry_result = translate_questions_batch_with_glossary(
        [question],
        project.glossary,
        project.metadata,
    )
    retried_question = retry_result.questions[0]
    updated_questions = [
        (
            retried_question
            if item.id == question_id
            else item
        )
        for item in project.questions
    ]
    merged_summary = merge_translation_retry_summary(
        updated_questions,
        project.translation_batch_summary,
        retry_result,
        question_id,
    )
    translation_report = build_full_exam_translation_report(
        updated_questions,
        project.glossary,
        merged_summary,
        project.full_exam_intake_report,
    )
    updated_project = project_store.set_translated_questions(
        project_id,
        updated_questions,
        merged_summary,
        translation_report,
    )
    if updated_project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    return updated_project




@router.post("/{project_id}/answer-key/draft")
def generate_answer_key_draft(project_id: str, account: AuthAccountPublic | None = Depends(_resolve_current_account)) -> ProjectSession:
    """Generate a teacher-review draft answer key for Phase 2-E1."""

    project = _get_or_404(project_id, account)
    if not project.questions:
        raise HTTPException(status_code=400, detail="لا توجد أسئلة لبناء مسودة نموذج إجابة.")
    answer_key = build_answer_key_draft(project.questions)
    if not answer_key:
        raise HTTPException(status_code=400, detail="لا توجد أسئلة نشطة لبناء نموذج إجابة.")
    updated_project = project_store.set_answer_key(project_id, answer_key)
    if updated_project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    return updated_project


@router.delete("/{project_id}/answer-key")
def clear_answer_key(project_id: str, account: AuthAccountPublic | None = Depends(_resolve_current_account)) -> ProjectSession:
    """Clear the draft answer key."""

    _get_or_404(project_id, account)
    project = project_store.clear_answer_key(project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


@router.post("/{project_id}/educational-analysis")
def generate_educational_analysis(project_id: str, account: AuthAccountPublic | None = Depends(_resolve_current_account)) -> ProjectSession:
    """Generate a foundational educational analysis for Phase 2-F1."""

    project = _get_or_404(project_id, account)
    analysis = build_educational_analysis(project)
    updated_project = project_store.set_educational_analysis(project_id, analysis)
    if updated_project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    return updated_project


@router.delete("/{project_id}/educational-analysis")
def clear_educational_analysis(project_id: str, account: AuthAccountPublic | None = Depends(_resolve_current_account)) -> ProjectSession:
    """Clear the generated educational analysis."""

    _get_or_404(project_id, account)
    project = project_store.clear_educational_analysis(project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


@router.post("/{project_id}/quality-tools")
def generate_quality_tools(project_id: str, account: AuthAccountPublic | None = Depends(_resolve_current_account)) -> ProjectSession:
    """Generate foundational quality tools for Phase 2-F2."""

    project = _get_or_404(project_id, account)
    quality_tools = build_quality_tools_report(project)
    updated_project = project_store.set_quality_tools(project_id, quality_tools)
    if updated_project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    return updated_project


@router.delete("/{project_id}/quality-tools")
def clear_quality_tools(project_id: str, account: AuthAccountPublic | None = Depends(_resolve_current_account)) -> ProjectSession:
    """Clear the generated quality tools report."""

    _get_or_404(project_id, account)
    project = project_store.clear_quality_tools(project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


@router.get("/{project_id}/readiness")
def get_project_readiness(project_id: str, account: AuthAccountPublic | None = Depends(_resolve_current_account)) -> ProjectReadinessReport:
    """Return a conservative readiness report before export for Phase 1-J1."""

    project = _get_or_404(project_id, account)
    return build_project_readiness_report(project)


@router.get("/{project_id}/full-exam/acceptance")
def get_full_exam_end_to_end_acceptance(
    project_id: str,
    account: AuthAccountPublic | None = Depends(_resolve_current_account),
) -> FullExamEndToEndReport | None:
    """Return the persisted Phase 4-A6d end-to-end acceptance report."""

    project = _get_or_404(project_id, account)
    return project.full_exam_end_to_end_report


@router.post("/{project_id}/full-exam/acceptance/run")
def run_full_exam_end_to_end_gate(
    project_id: str,
    account: AuthAccountPublic | None = Depends(_resolve_current_account),
) -> ProjectSession:
    """Run the non-destructive Phase 4-A6d acceptance gate."""

    project = _get_or_404(project_id, account)
    result = run_full_exam_end_to_end_acceptance(project)
    updated_project = project_store.set_full_exam_end_to_end_result(
        project_id,
        intake_report=result.intake_report,
        translation_report=result.translation_report,
        export_report=result.export_report,
        end_to_end_report=result.report,
    )
    if updated_project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    return updated_project


@router.get("/{project_id}/export/acceptance")
def get_full_exam_export_acceptance(
    project_id: str,
    account: AuthAccountPublic | None = Depends(_resolve_current_account),
) -> FullExamExportReport | None:
    """Return the persisted Phase 4-A6c artifact acceptance report."""

    project = _get_or_404(project_id, account)
    return project.full_exam_export_report


@router.post("/{project_id}/export/docx")
def export_project_docx(project_id: str, account: AuthAccountPublic | None = Depends(_resolve_current_account)) -> Response:
    """Generate a real RTL DOCX and persist its Phase 4-A6c acceptance result."""

    project = _get_or_404(project_id, account)
    try:
        docx_bytes = build_project_docx_bytes(project)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    export_report = build_full_exam_export_report(
        project,
        ExportFormat.docx,
        docx_bytes,
        project.full_exam_export_report,
    )
    updated_project = project_store.set_full_exam_export_report(
        project_id,
        export_report,
    )
    if updated_project is None:
        raise HTTPException(status_code=404, detail="Project not found")

    filename = safe_docx_filename(updated_project)
    headers = {
        "Content-Disposition": f'attachment; filename="{filename}"',
        "Cache-Control": "no-store",
        "X-Madarik-Export-Acceptance": export_report.status.value,
    }
    return Response(content=docx_bytes, media_type=DOCX_MIME_TYPE, headers=headers)


@router.post("/{project_id}/export/pdf")
def export_project_pdf(project_id: str, account: AuthAccountPublic | None = Depends(_resolve_current_account)) -> Response:
    """Generate a real RTL PDF and persist its Phase 4-A6c acceptance result."""

    project = _get_or_404(project_id, account)
    try:
        pdf_bytes = build_project_pdf_bytes(project)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    export_report = build_full_exam_export_report(
        project,
        ExportFormat.pdf,
        pdf_bytes,
        project.full_exam_export_report,
    )
    updated_project = project_store.set_full_exam_export_report(
        project_id,
        export_report,
    )
    if updated_project is None:
        raise HTTPException(status_code=404, detail="Project not found")

    filename = safe_pdf_filename(updated_project)
    headers = {
        "Content-Disposition": f'attachment; filename="{filename}"',
        "Cache-Control": "no-store",
        "X-Madarik-Export-Acceptance": export_report.status.value,
    }
    return Response(content=pdf_bytes, media_type=PDF_MIME_TYPE, headers=headers)

@router.post("/{project_id}/demo-content")
def load_demo_content(project_id: str, account: AuthAccountPublic | None = Depends(_resolve_current_account)) -> ProjectSession:
    """Load backend-owned demo questions and glossary for Phase 1-B."""

    _get_or_404(project_id, account)
    project = project_store.load_demo_content(project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


@router.patch("/{project_id}/questions/{question_id}")
def update_question(project_id: str, question_id: str, patch: QuestionPatch, account: AuthAccountPublic | None = Depends(_resolve_current_account)) -> ProjectSession:
    """Update a question card from the review step."""

    _get_or_404(project_id, account)
    project = project_store.update_question(project_id, question_id, patch)
    if project is None:
        raise HTTPException(status_code=404, detail="Project or question not found")
    return project


@router.post("/{project_id}/questions/{question_id}/assets")
async def upload_question_asset(project_id: str, question_id: str, file: UploadFile = File(...), account: AuthAccountPublic | None = Depends(_resolve_current_account)) -> ProjectSession:
    """Attach an optional question image/table snapshot for Phase 1-H1."""

    _get_or_404(project_id, account)

    filename = file.filename or "question-asset"
    content_type = file.content_type or "application/octet-stream"
    allowed_types = {"image/png", "image/jpeg", "image/jpg"}
    if content_type not in allowed_types:
        raise HTTPException(status_code=400, detail="يدعم مرفق السؤال صور PNG وJPG فقط في Phase 1-H1.")

    file_bytes = await file.read()
    max_size = 2_000_000
    if len(file_bytes) > max_size:
        raise HTTPException(status_code=400, detail="حجم مرفق السؤال كبير. الحد الأقصى المؤقت هو 2MB.")

    asset = QuestionAssetInfo(
        name=filename,
        size=len(file_bytes),
        type=content_type,
        data_base64=base64.b64encode(file_bytes).decode("ascii"),
    )
    project = project_store.add_question_asset(project_id, question_id, asset)
    if project is None:
        raise HTTPException(status_code=404, detail="Project or question not found")
    return project


@router.delete("/{project_id}/questions/{question_id}/assets/{asset_id}")
def delete_question_asset(project_id: str, question_id: str, asset_id: str, account: AuthAccountPublic | None = Depends(_resolve_current_account)) -> ProjectSession:
    """Remove a question attachment from the temporary session."""

    project = project_store.remove_question_asset(project_id, question_id, asset_id)
    if project is None:
        raise HTTPException(status_code=404, detail="Project, question, or asset not found")
    return project



@router.post("/{project_id}/questions/bulk-status")
def bulk_update_question_status(project_id: str, payload: QuestionBulkStatusRequest, account: AuthAccountPublic | None = Depends(_resolve_current_account)) -> ProjectSession:
    """Apply one review status to many questions for Phase 1-L1."""

    _get_or_404(project_id, account)
    project = project_store.bulk_update_question_status(
        project_id,
        status=payload.status,
        include_deleted=payload.include_deleted,
    )
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


@router.post("/{project_id}/questions/reorder")
def reorder_questions(project_id: str, payload: QuestionReorderRequest, account: AuthAccountPublic | None = Depends(_resolve_current_account)) -> ProjectSession:
    """Update question order indices from the frontend."""

    _get_or_404(project_id, account)
    project = project_store.reorder_questions(project_id, payload.ordered_question_ids)
    if project is None:
        raise HTTPException(status_code=400, detail="Invalid question order or project not found")
    return project


@router.patch("/{project_id}/glossary/{term_id}")
def update_glossary_term(project_id: str, term_id: str, patch: GlossaryTermPatch, account: AuthAccountPublic | None = Depends(_resolve_current_account)) -> ProjectSession:
    """Update one glossary term from the glossary review step."""

    _get_or_404(project_id, account)
    project = project_store.update_glossary_term(project_id, term_id, patch)
    if project is None:
        raise HTTPException(status_code=404, detail="Project or glossary term not found")
    return project


@router.delete("/{project_id}")
def delete_project(project_id: str, account: AuthAccountPublic | None = Depends(_resolve_current_account)) -> dict[str, bool]:
    """Delete the temporary project session."""

    _get_or_404(project_id, account)
    deleted = project_store.delete(project_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Project not found")
    return {"deleted": True}


@router.get(
    "/{project_id}/question-bank",
    response_model=QuestionBankListResponse,
)
def list_project_question_bank(
    project_id: str,
    account: AuthAccountPublic | None = Depends(
        _resolve_current_account
    ),
) -> QuestionBankListResponse:
    _get_or_404(project_id, account)
    items = question_bank_repository.list_for_project(
        project_id
    )
    return QuestionBankListResponse(
        items=items,
        total=len(items),
    )


@router.post(
    "/{project_id}/questions/{question_id}/question-bank",
    response_model=QuestionBankItem,
)
def save_question_to_bank(
    project_id: str,
    question_id: str,
    account: AuthAccountPublic | None = Depends(
        _resolve_current_account
    ),
) -> QuestionBankItem:
    project = _get_or_404(project_id, account)
    question = next(
        (
            item
            for item in project.questions
            if item.id == question_id
        ),
        None,
    )
    if question is None:
        raise HTTPException(
            status_code=404,
            detail="Question not found",
        )
    if question.status == QuestionStatus.deleted:
        raise HTTPException(
            status_code=400,
            detail="Deleted questions cannot be saved.",
        )

    return question_bank_repository.save_from_project_question(
        project,
        question,
    )


@router.delete(
    "/{project_id}/question-bank/{item_id}",
    response_model=QuestionBankItem,
)
def delete_question_bank_item(
    project_id: str,
    item_id: str,
    account: AuthAccountPublic | None = Depends(
        _resolve_current_account
    ),
) -> QuestionBankItem:
    _get_or_404(project_id, account)
    removed = question_bank_repository.delete(
        project_id,
        item_id,
    )
    if removed is None:
        raise HTTPException(
            status_code=404,
            detail="Question bank item not found",
        )
    return removed


@router.get(
    "/question-bank/library",
    response_model=QuestionBankSearchResponse,
)
def search_question_bank_library(
    query: str | None = None,
    grade: int | None = None,
    science_domain: str | None = None,
    unit_id: str | None = None,
    cognitive_category: str | None = None,
    account: AuthAccountPublic | None = Depends(
        _resolve_current_account
    ),
) -> QuestionBankSearchResponse:
    owner_account_id = account.id if account else None
    items = question_bank_repository.search(
        query=query,
        grade=grade,
        science_domain=science_domain,
        unit_id=unit_id,
        cognitive_category=cognitive_category,
        owner_account_id=owner_account_id,
    )
    return QuestionBankSearchResponse(
        items=items,
        total=len(items),
        query=query,
        grade=grade,
        science_domain=science_domain,
        unit_id=unit_id,
        cognitive_category=cognitive_category,
    )


@router.get(
    "/question-bank/library/{item_id}",
    response_model=QuestionBankItem,
)
def get_question_bank_library_item(
    item_id: str,
    account: AuthAccountPublic | None = Depends(
        _resolve_current_account
    ),
) -> QuestionBankItem:
    item = question_bank_repository.get(item_id)
    if item is None:
        raise HTTPException(
            status_code=404,
            detail="Question bank item not found",
        )

    if (
        account is not None
        and item.owner_account_id is not None
        and item.owner_account_id != account.id
    ):
        raise HTTPException(
            status_code=403,
            detail="Question bank item access denied",
        )

    return item


@router.post(
    "/question-bank/library/{item_id}/reuse/{target_project_id}",
    response_model=QuestionBankReuseResponse,
)
def reuse_question_bank_library_item(
    item_id: str,
    target_project_id: str,
    account: AuthAccountPublic | None = Depends(
        _resolve_current_account
    ),
) -> QuestionBankReuseResponse:
    target_project = _get_or_404(
        target_project_id,
        account,
    )
    bank_item = question_bank_repository.get(item_id)

    if bank_item is None:
        raise HTTPException(
            status_code=404,
            detail="Question bank item not found",
        )

    if (
        account is not None
        and bank_item.owner_account_id is not None
        and bank_item.owner_account_id != account.id
    ):
        raise HTTPException(
            status_code=403,
            detail="Question bank item access denied",
        )

    question, reused = reuse_question_bank_item(
        target_project,
        bank_item,
    )
    if reused:
        project_store.touch(target_project_id)

    return QuestionBankReuseResponse(
        target_project_id=target_project_id,
        source_bank_item_id=item_id,
        reused=reused,
        question=question,
    )



@router.post(
    "/assessment-builder",
    response_model=AssessmentDraftDetail,
    status_code=status.HTTP_201_CREATED,
)
def create_assessment_draft(
    request: AssessmentDraftCreateRequest,
    account: AuthAccountPublic | None = Depends(
        _resolve_current_account
    ),
) -> AssessmentDraftDetail:
    if request.source_project_id:
        _get_or_404(request.source_project_id, account)

    draft = assessment_repository.create(
        blueprint=request.blueprint,
        owner_account_id=account.id if account else None,
        source_project_id=request.source_project_id,
    )
    try:
        return build_assessment_detail(
            draft,
            question_bank_repository,
        )
    except AssessmentBlueprintError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc


@router.get(
    "/assessment-builder",
    response_model=AssessmentDraftListResponse,
)
def list_assessment_drafts(
    account: AuthAccountPublic | None = Depends(
        _resolve_current_account
    ),
) -> AssessmentDraftListResponse:
    items = assessment_repository.list(
        owner_account_id=account.id if account else None,
    )
    return AssessmentDraftListResponse(
        items=items,
        total=len(items),
    )


def _get_assessment_or_404(
    draft_id: str,
    account: AuthAccountPublic | None,
) -> AssessmentDraft:
    draft = assessment_repository.get(draft_id)
    if draft is None:
        raise HTTPException(
            status_code=404,
            detail="Assessment draft not found",
        )
    if (
        account is not None
        and draft.owner_account_id is not None
        and draft.owner_account_id != account.id
        and account.role != AccountRole.owner
    ):
        raise HTTPException(
            status_code=403,
            detail="Assessment draft access denied",
        )
    return draft


@router.get(
    "/assessment-builder/{draft_id}",
    response_model=AssessmentDraftDetail,
)
def get_assessment_draft(
    draft_id: str,
    account: AuthAccountPublic | None = Depends(
        _resolve_current_account
    ),
) -> AssessmentDraftDetail:
    draft = _get_assessment_or_404(draft_id, account)
    return build_assessment_detail(
        draft,
        question_bank_repository,
    )


@router.put(
    "/assessment-builder/{draft_id}/blueprint",
    response_model=AssessmentDraftDetail,
)
def update_assessment_blueprint(
    draft_id: str,
    blueprint: AssessmentBlueprint,
    account: AuthAccountPublic | None = Depends(
        _resolve_current_account
    ),
) -> AssessmentDraftDetail:
    draft = _get_assessment_or_404(draft_id, account)
    draft.blueprint = blueprint
    try:
        validate_blueprint(draft)
    except AssessmentBlueprintError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc
    assessment_repository.save(draft)
    return build_assessment_detail(
        draft,
        question_bank_repository,
    )


@router.post(
    "/assessment-builder/{draft_id}/items/{bank_item_id}",
    response_model=AssessmentDraftDetail,
)
def add_assessment_bank_item(
    draft_id: str,
    bank_item_id: str,
    account: AuthAccountPublic | None = Depends(
        _resolve_current_account
    ),
) -> AssessmentDraftDetail:
    draft = _get_assessment_or_404(draft_id, account)
    bank_item = question_bank_repository.get(bank_item_id)
    if bank_item is None:
        raise HTTPException(
            status_code=404,
            detail="Question bank item not found",
        )
    if (
        account is not None
        and bank_item.owner_account_id is not None
        and bank_item.owner_account_id != account.id
        and account.role != AccountRole.owner
    ):
        raise HTTPException(
            status_code=403,
            detail="Question bank item access denied",
        )
    assessment_repository.add_bank_item(
        draft,
        bank_item,
    )
    return build_assessment_detail(
        draft,
        question_bank_repository,
    )


@router.delete(
    "/assessment-builder/{draft_id}/items/{bank_item_id}",
    response_model=AssessmentDraftDetail,
)
def remove_assessment_bank_item(
    draft_id: str,
    bank_item_id: str,
    account: AuthAccountPublic | None = Depends(
        _resolve_current_account
    ),
) -> AssessmentDraftDetail:
    draft = _get_assessment_or_404(draft_id, account)
    assessment_repository.remove_bank_item(
        draft,
        bank_item_id,
    )
    return build_assessment_detail(
        draft,
        question_bank_repository,
    )



@router.post(
    "/assessment-builder/{draft_id}/auto-select",
    response_model=AssessmentAutoSelectionResponse,
)
def auto_select_assessment_questions(
    draft_id: str,
    account: AuthAccountPublic | None = Depends(_resolve_current_account),
) -> AssessmentAutoSelectionResponse:
    draft = _get_assessment_or_404(draft_id, account)
    items = question_bank_repository.search(
        grade=draft.blueprint.grade,
        science_domain=draft.blueprint.science_domain,
        unit_id=draft.blueprint.unit_id,
        owner_account_id=account.id if account else None,
    )
    result = auto_select_questions_for_assessment(
        draft,
        items,
        question_bank_repository,
    )
    assessment_repository.save(draft)
    return result


@router.get(
    "/assessment-builder/{draft_id}/validate",
    response_model=AssessmentBlueprintValidation,
)
def validate_assessment_draft(
    draft_id: str,
    account: AuthAccountPublic | None = Depends(_resolve_current_account),
) -> AssessmentBlueprintValidation:
    draft = _get_assessment_or_404(draft_id, account)
    return validate_assessment_blueprint(
        draft,
        question_bank_repository,
    )


@router.put(
    "/assessment-builder/{draft_id}/layout",
    response_model=AssessmentDraftDetail,
)
def update_assessment_layout(
    draft_id: str,
    layout: AssessmentLayoutUpdate,
    account: AuthAccountPublic | None = Depends(
        _resolve_current_account
    ),
) -> AssessmentDraftDetail:
    draft = _get_assessment_or_404(
        draft_id,
        account,
    )
    assessment_repository.update_layout(
        draft,
        layout,
    )
    return build_assessment_detail(
        draft,
        question_bank_repository,
    )


@router.get(
    "/assessment-builder/{draft_id}/student-preview",
    response_model=AssessmentStudentPaperPreview,
)
def get_assessment_student_preview(
    draft_id: str,
    account: AuthAccountPublic | None = Depends(
        _resolve_current_account
    ),
) -> AssessmentStudentPaperPreview:
    draft = _get_assessment_or_404(
        draft_id,
        account,
    )
    return build_student_paper_preview(
        draft,
        question_bank_repository,
    )


@router.post(
    "/assessment-builder/{draft_id}/export/{output_format}",
)
def export_assessment_draft(
    draft_id: str,
    output_format: str,
    account: AuthAccountPublic | None = Depends(
        _resolve_current_account
    ),
):
    if output_format not in {"docx", "pdf"}:
        raise HTTPException(
            status_code=400,
            detail="Unsupported assessment export format",
        )

    draft = _get_assessment_or_404(
        draft_id,
        account,
    )
    result = export_assessment_foundation(
        draft,
        question_bank_repository,
        output_format,
    )

    if not result.export_ready:
        raise HTTPException(
            status_code=409,
            detail={
                "message": "Assessment is not export ready",
                "issues": result.issues,
            },
        )

    media_type = (
        "application/vnd.openxmlformats-officedocument."
        "wordprocessingml.document"
        if output_format == "docx"
        else "application/pdf"
    )
    return FileResponse(
        path=result.path,
        media_type=media_type,
        filename=result.filename,
    )

@router.get("/differentiated-activities", response_model=DifferentiatedActivityListResponse)
def list_differentiated_activities(
    grade: int | None = None,
    level: str | None = None,
    account: AuthAccountPublic | None = Depends(_resolve_current_account),
) -> DifferentiatedActivityListResponse:
    items = differentiated_activity_repository.list(
        owner_account_id=account.id if account else None,
        grade=grade,
        level=level,
    )
    return DifferentiatedActivityListResponse(items=items, total=len(items))


@router.post("/differentiated-activities", response_model=DifferentiatedActivity)
def create_differentiated_activity(
    payload: DifferentiatedActivityCreateRequest,
    account: AuthAccountPublic | None = Depends(_resolve_current_account),
) -> DifferentiatedActivity:
    return differentiated_activity_repository.create(
        payload,
        owner_account_id=account.id if account else None,
    )


@router.delete("/differentiated-activities/{activity_id}", response_model=DifferentiatedActivity)
def delete_differentiated_activity(
    activity_id: str,
    account: AuthAccountPublic | None = Depends(_resolve_current_account),
) -> DifferentiatedActivity:
    activity = differentiated_activity_repository.delete(activity_id)
    if activity is None:
        raise HTTPException(status_code=404, detail="Differentiated activity not found")
    if (
        account is not None
        and activity.owner_account_id is not None
        and activity.owner_account_id != account.id
    ):
        raise HTTPException(status_code=403, detail="Differentiated activity access denied")
    return activity



@router.post(
    "/differentiated-activities/generate",
    response_model=DifferentiatedActivityGenerationResponse,
)
def generate_differentiated_activities(
    payload: DifferentiatedActivityGenerationRequest,
    account: AuthAccountPublic | None = Depends(
        _resolve_current_account
    ),
) -> DifferentiatedActivityGenerationResponse:
    bank_item = None
    if payload.source_question_bank_item_id:
        bank_item = question_bank_repository.get(
            payload.source_question_bank_item_id
        )
        if bank_item is None:
            raise HTTPException(
                status_code=404,
                detail="Question bank item not found",
            )

    return generate_differentiated_activity_set(
        payload,
        differentiated_activity_repository,
        owner_account_id=account.id if account else None,
        bank_item=bank_item,
    )


@router.get(
    "/differentiated-activities/{activity_id}/preview",
    response_model=DifferentiatedActivityPreview,
)
def get_differentiated_activity_preview(
    activity_id: str,
    account: AuthAccountPublic | None = Depends(
        _resolve_current_account
    ),
) -> DifferentiatedActivityPreview:
    activity = differentiated_activity_repository.get(activity_id)
    if activity is None:
        raise HTTPException(
            status_code=404,
            detail="Differentiated activity not found",
        )
    return build_activity_preview(activity)


@router.post(
    "/differentiated-activities/{activity_id}/export/{output_format}",
)
def export_differentiated_activity(
    activity_id: str,
    output_format: str,
    account: AuthAccountPublic | None = Depends(
        _resolve_current_account
    ),
):
    if output_format not in {"docx", "pdf"}:
        raise HTTPException(
            status_code=400,
            detail="Unsupported activity export format",
        )

    activity = differentiated_activity_repository.get(activity_id)
    if activity is None:
        raise HTTPException(
            status_code=404,
            detail="Differentiated activity not found",
        )

    result = export_activity(activity, output_format)
    if not result.export_ready:
        raise HTTPException(
            status_code=409,
            detail={
                "message": "Activity is not export ready",
                "issues": result.issues,
            },
        )

    media_type = (
        "application/vnd.openxmlformats-officedocument."
        "wordprocessingml.document"
        if output_format == "docx"
        else "application/pdf"
    )
    return FileResponse(
        path=result.path,
        media_type=media_type,
        filename=result.filename,
    )


@router.get(
    "/scientific-diagrams",
    response_model=ScientificDiagramListResponse,
)
def list_scientific_diagrams(
    grade: int | None = None,
    science_domain: str | None = None,
    unit_id: str | None = None,
    diagram_type: str | None = None,
    account: AuthAccountPublic | None = Depends(
        _resolve_current_account
    ),
) -> ScientificDiagramListResponse:
    items = scientific_diagram_repository.list(
        owner_account_id=account.id if account else None,
        grade=grade,
        science_domain=science_domain,
        unit_id=unit_id,
        diagram_type=diagram_type,
    )
    return ScientificDiagramListResponse(
        items=items,
        total=len(items),
    )


@router.post(
    "/scientific-diagrams",
    response_model=ScientificDiagram,
)
def create_scientific_diagram(
    payload: ScientificDiagramCreateRequest,
    account: AuthAccountPublic | None = Depends(
        _resolve_current_account
    ),
) -> ScientificDiagram:
    return scientific_diagram_repository.create(
        payload,
        owner_account_id=account.id if account else None,
    )


@router.delete(
    "/scientific-diagrams/{diagram_id}",
    response_model=ScientificDiagram,
)
def delete_scientific_diagram(
    diagram_id: str,
    account: AuthAccountPublic | None = Depends(
        _resolve_current_account
    ),
) -> ScientificDiagram:
    diagram = scientific_diagram_repository.delete(
        diagram_id
    )
    if diagram is None:
        raise HTTPException(
            status_code=404,
            detail="Scientific diagram not found",
        )
    return diagram


@router.get(
    "/scientific-diagrams/{diagram_id}/preview",
    response_model=ScientificDiagramPreview,
)
def get_scientific_diagram_preview(
    diagram_id: str,
    account: AuthAccountPublic | None = Depends(
        _resolve_current_account
    ),
) -> ScientificDiagramPreview:
    diagram = scientific_diagram_repository.get(
        diagram_id
    )
    if diagram is None:
        raise HTTPException(
            status_code=404,
            detail="Scientific diagram not found",
        )
    return build_scientific_diagram_preview(
        diagram
    )


@router.get(
    "/scientific-diagrams/{diagram_id}/svg",
    response_model=ScientificDiagramSvgExportResponse,
)
def export_scientific_diagram_as_svg(
    diagram_id: str,
    account: AuthAccountPublic | None = Depends(
        _resolve_current_account
    ),
) -> ScientificDiagramSvgExportResponse:
    diagram = scientific_diagram_repository.get(
        diagram_id
    )
    if diagram is None:
        raise HTTPException(
            status_code=404,
            detail="Scientific diagram not found",
        )
    return export_scientific_diagram_svg(
        diagram
    )


@router.get(
    "/scientific-diagrams/{diagram_id}/export/{output_format}",
)
def export_scientific_diagram_file(
    diagram_id: str,
    output_format: str,
    account: AuthAccountPublic | None = Depends(
        _resolve_current_account
    ),
):
    if output_format not in {"png", "pdf"}:
        raise HTTPException(
            status_code=400,
            detail="Unsupported scientific diagram format",
        )

    diagram = scientific_diagram_repository.get(
        diagram_id
    )
    if diagram is None:
        raise HTTPException(
            status_code=404,
            detail="Scientific diagram not found",
        )

    result = export_scientific_diagram_binary(
        diagram,
        output_format,
    )
    if not result.export_ready:
        raise HTTPException(
            status_code=409,
            detail={
                "message": (
                    "Scientific diagram is not export ready"
                ),
                "issues": result.issues,
            },
        )

    media_type = (
        "image/png"
        if output_format == "png"
        else "application/pdf"
    )
    return FileResponse(
        path=result.path,
        media_type=media_type,
        filename=result.filename,
    )


@router.get("/cloud-sources", response_model=CloudSourceListResponse)
def list_cloud_sources(provider: str | None = None, source_project_id: str | None = None, account: AuthAccountPublic | None = Depends(_resolve_current_account)) -> CloudSourceListResponse:
    items = cloud_source_repository.list(owner_account_id=account.id if account else None, provider=provider, source_project_id=source_project_id)
    return CloudSourceListResponse(items=items, total=len(items))

@router.post("/cloud-sources", response_model=CloudSource)
def create_cloud_source(payload: CloudSourceCreateRequest, account: AuthAccountPublic | None = Depends(_resolve_current_account)) -> CloudSource:
    return cloud_source_repository.create(payload, owner_account_id=account.id if account else None)

@router.post("/cloud-sources/onedrive/from-url", response_model=CloudSource)
def create_onedrive_source_from_url(web_url: str, display_name: str, source_project_id: str | None = None, source_type: CloudSourceType = CloudSourceType.file, account: AuthAccountPublic | None = Depends(_resolve_current_account)) -> CloudSource:
    try:
        payload = parse_onedrive_source_url(web_url=web_url, display_name=display_name, source_project_id=source_project_id, source_type=source_type)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return cloud_source_repository.create(payload, owner_account_id=account.id if account else None)

@router.delete("/cloud-sources/{source_id}", response_model=CloudSource)
def delete_cloud_source(source_id: str, account: AuthAccountPublic | None = Depends(_resolve_current_account)) -> CloudSource:
    source = cloud_source_repository.delete(source_id)
    if source is None:
        raise HTTPException(status_code=404, detail="Cloud source not found")
    return source


@router.get(
    "/cloud-sources/onedrive/status",
    response_model=OneDriveProviderStatus,
)
def get_onedrive_status(
    account: AuthAccountPublic | None = Depends(
        _resolve_current_account
    ),
) -> OneDriveProviderStatus:
    return get_onedrive_provider_status()


@router.post(
    "/cloud-sources/{source_id}/sync",
    response_model=CloudSourceSyncResponse,
)
def sync_cloud_source(
    source_id: str,
    download: bool = False,
    account: AuthAccountPublic | None = Depends(
        _resolve_current_account
    ),
) -> CloudSourceSyncResponse:
    source = cloud_source_repository.get(source_id)
    if source is None:
        raise HTTPException(
            status_code=404,
            detail="Cloud source not found",
        )
    if source.provider.value != "onedrive":
        raise HTTPException(
            status_code=400,
            detail=(
                "Only OneDrive synchronization is "
                "implemented in this phase"
            ),
        )

    try:
        return synchronize_onedrive_source(
            source,
            cloud_source_repository,
            download=download,
        )
    except OneDriveConfigurationError as exc:
        raise HTTPException(
            status_code=503,
            detail=str(exc),
        ) from exc
    except OneDriveGraphError as exc:
        raise HTTPException(
            status_code=502,
            detail=str(exc),
        ) from exc
