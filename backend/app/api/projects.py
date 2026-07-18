import base64
from fastapi import APIRouter, Depends, File, Header, HTTPException, UploadFile, status
from fastapi.responses import Response

from app.models.auth import AccountRole, AuthAccountPublic
from app.models.project import (
    ExtractedPdfPageInfo,
    ExtractedTextInfo,
    GlossaryTermPatch,
    ProjectMetadata,
    ProjectLogoInfo,
    ProjectReadinessReport,
    ProjectSession,
    QuestionPatch,
    QuestionAssetInfo,
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
from app.services.text_extraction import TextExtractionError, extract_text_from_pdf_bytes
from app.services.ocr import OcrExtractionError, extract_text_from_image_bytes
from app.services.pdf_ocr import PdfOcrExtractionError, extract_text_from_scanned_pdf_bytes
from app.services.pdf_layout_assets import PdfLayoutAssetExtractionError, extract_pdf_layout_assets_from_bytes
from app.services.translation import translate_questions_batch_with_glossary
from app.services.readiness import build_project_readiness_report
from app.services.ai_provider import get_ai_provider_status
from app.services.answer_key import build_answer_key_draft
from app.services.educational_analysis import build_educational_analysis
from app.services.quality_tools import build_quality_tools_report
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
    """Translate a complete paper with Phase 4-A5 batch isolation and summary."""

    project = _get_or_404(project_id, account)
    if not project.questions:
        raise HTTPException(status_code=400, detail="لا توجد أسئلة قابلة للترجمة.")

    batch_result = translate_questions_batch_with_glossary(
        project.questions,
        project.glossary,
        project.metadata,
    )
    updated_project = project_store.set_translated_questions(
        project_id,
        batch_result.questions,
        batch_result.summary,
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


@router.post("/{project_id}/export/docx")
def export_project_docx(project_id: str, account: AuthAccountPublic | None = Depends(_resolve_current_account)) -> Response:
    """Generate a real RTL DOCX file for Phase 1-F1."""

    project = _get_or_404(project_id, account)
    try:
        docx_bytes = build_project_docx_bytes(project)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    filename = safe_docx_filename(project)
    headers = {
        "Content-Disposition": f'attachment; filename="{filename}"',
        "Cache-Control": "no-store",
    }
    return Response(content=docx_bytes, media_type=DOCX_MIME_TYPE, headers=headers)



@router.post("/{project_id}/export/pdf")
def export_project_pdf(project_id: str, account: AuthAccountPublic | None = Depends(_resolve_current_account)) -> Response:
    """Generate a real RTL PDF file for Phase 1-F2."""

    project = _get_or_404(project_id, account)
    try:
        pdf_bytes = build_project_pdf_bytes(project)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    filename = safe_pdf_filename(project)
    headers = {
        "Content-Disposition": f'attachment; filename="{filename}"',
        "Cache-Control": "no-store",
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
