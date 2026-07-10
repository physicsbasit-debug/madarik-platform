import base64

from fastapi import APIRouter, File, HTTPException, UploadFile, status
from fastapi.responses import Response

from app.models.project import (
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
from app.services.session_store import project_store
from app.services.glossary import extract_glossary_terms_from_questions
from app.services.question_parser import parse_questions_from_text
from app.services.text_extraction import TextExtractionError, extract_text_from_pdf_bytes
from app.services.ocr import OcrExtractionError, extract_text_from_image_bytes
from app.services.pdf_ocr import PdfOcrExtractionError, extract_text_from_scanned_pdf_bytes
from app.services.translation import translate_questions_with_glossary
from app.services.readiness import build_project_readiness_report
from app.services.ai_provider import get_ai_provider_status
from app.services.export import (
    DOCX_MIME_TYPE,
    PDF_MIME_TYPE,
    build_project_docx_bytes,
    build_project_pdf_bytes,
    safe_docx_filename,
    safe_pdf_filename,
)

router = APIRouter(prefix="/projects", tags=["projects"])


@router.get("/translation-provider/status")
def get_translation_provider_status() -> dict[str, object]:
    """Return safe AI provider metadata without exposing secrets."""

    return get_ai_provider_status()


def _get_or_404(project_id: str) -> ProjectSession:
    project = project_store.get(project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


@router.post("", status_code=status.HTTP_201_CREATED)
def create_project(metadata: ProjectMetadata | None = None) -> ProjectSession:
    """Create a temporary project session."""

    return project_store.create(metadata)


@router.get("/{project_id}")
def get_project(project_id: str) -> ProjectSession:
    """Return a temporary project session."""

    return _get_or_404(project_id)



@router.get("/{project_id}/snapshot")
def export_project_snapshot(project_id: str) -> ProjectSession:
    """Return the current temporary project as a JSON snapshot for Phase 1-M1."""

    return _get_or_404(project_id)


@router.post("/import-snapshot", status_code=status.HTTP_201_CREATED)
def import_project_snapshot(snapshot: ProjectSession) -> ProjectSession:
    """Import a JSON snapshot as a new temporary project session."""

    return project_store.import_snapshot(snapshot)


@router.patch("/{project_id}/metadata")
def update_project_metadata(project_id: str, metadata: ProjectMetadata) -> ProjectSession:
    """Update project metadata from the frontend setup step."""

    project = project_store.update_metadata(project_id, metadata)
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


@router.patch("/{project_id}/step")
def update_project_step(project_id: str, payload: StepUpdate) -> ProjectSession:
    """Remember the current frontend step in the temporary session."""

    project = _get_or_404(project_id)
    project.current_step = payload.current_step
    return project_store.touch(project_id) or project


@router.put("/{project_id}/upload-info")
def set_upload_info(project_id: str, uploaded_file: UploadedFileInfo | None = None) -> ProjectSession:
    """Store file metadata only. No real file upload is performed in Phase 1-B."""

    project = project_store.set_uploaded_file(project_id, uploaded_file)
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    return project




@router.post("/{project_id}/school-logo")
async def upload_school_logo(project_id: str, file: UploadFile = File(...)) -> ProjectSession:
    """Store an optional school logo in the temporary project session for Phase 1-F3."""

    _get_or_404(project_id)

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
def delete_school_logo(project_id: str) -> ProjectSession:
    """Remove the optional school logo from the temporary project session."""

    project = project_store.set_school_logo(project_id, None)
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


@router.post("/{project_id}/upload-pdf")
async def upload_pdf_and_extract_text(project_id: str, file: UploadFile = File(...)) -> ProjectSession:
    """Upload a real text-based PDF and extract selectable text for Phase 1-C."""

    _get_or_404(project_id)

    filename = file.filename or "uploaded.pdf"
    if not filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="يدعم هذا المسار ملفات PDF فقط في Phase 1-C.")

    file_bytes = await file.read()
    uploaded_file = UploadedFileInfo(name=filename, size=len(file_bytes), type=file.content_type or "application/pdf")

    try:
        result = extract_text_from_pdf_bytes(file_bytes)
    except TextExtractionError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    if not result.is_text_based:
        extracted_text = ExtractedTextInfo(
            text="",
            preview="",
            page_count=result.page_count,
            character_count=0,
            is_text_based=False,
            message="لم يتم العثور على نص قابل للاستخراج. يبدو أن الملف PDF مصوّر أو ممسوح ضوئيًا، وسيحتاج OCR في مرحلة لاحقة.",
        )
    else:
        extracted_text = ExtractedTextInfo(
            text=result.text,
            preview=result.preview,
            page_count=result.page_count,
            character_count=result.character_count,
            is_text_based=True,
            message="تم استخراج النص من PDF نصي بنجاح.",
        )

    project = project_store.set_extracted_text(project_id, uploaded_file, extracted_text)
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


@router.post("/{project_id}/upload-pdf-ocr")
async def upload_scanned_pdf_and_extract_text(project_id: str, file: UploadFile = File(...)) -> ProjectSession:
    """Upload a PDF and try OCR on its rendered pages for Phase 1-I2."""

    _get_or_404(project_id)

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
async def upload_image_and_extract_text(project_id: str, file: UploadFile = File(...)) -> ProjectSession:
    """Upload an image and run English OCR for Phase 1-I2."""

    _get_or_404(project_id)

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


@router.post("/{project_id}/parse-questions")
def parse_extracted_questions(project_id: str) -> ProjectSession:
    """Convert extracted text into reviewable question cards for Phase 1-D."""

    project = _get_or_404(project_id)
    if project.extracted_text is None or not project.extracted_text.text.strip():
        raise HTTPException(status_code=400, detail="لا يوجد نص مستخرج يمكن تقسيمه إلى أسئلة.")
    if not project.extracted_text.is_text_based:
        raise HTTPException(status_code=400, detail="لا يمكن تقسيم PDF غير نصي في Phase 1-D. سيحتاج OCR لاحقًا.")

    questions = parse_questions_from_text(project.extracted_text.text)
    if not questions:
        raise HTTPException(status_code=400, detail="لم يتم العثور على أسئلة قابلة للتقسيم في النص المستخرج.")

    updated_project = project_store.set_parsed_questions(project_id, questions)
    if updated_project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    return updated_project



@router.post("/{project_id}/glossary/generate")
def generate_project_glossary(project_id: str) -> ProjectSession:
    """Generate a teacher-review glossary from parsed question cards for Phase 1-E1."""

    project = _get_or_404(project_id)
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
def translate_project_questions(project_id: str) -> ProjectSession:
    """Translate parsed question cards using the reviewed glossary for Phase 1-E2."""

    project = _get_or_404(project_id)
    if not project.questions:
        raise HTTPException(status_code=400, detail="لا توجد أسئلة قابلة للترجمة.")

    translated_questions = translate_questions_with_glossary(project.questions, project.glossary)
    updated_project = project_store.set_translated_questions(project_id, translated_questions)
    if updated_project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    return updated_project




@router.get("/{project_id}/readiness")
def get_project_readiness(project_id: str) -> ProjectReadinessReport:
    """Return a conservative readiness report before export for Phase 1-J1."""

    project = _get_or_404(project_id)
    return build_project_readiness_report(project)


@router.post("/{project_id}/export/docx")
def export_project_docx(project_id: str) -> Response:
    """Generate a real RTL DOCX file for Phase 1-F1."""

    project = _get_or_404(project_id)
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
def export_project_pdf(project_id: str) -> Response:
    """Generate a real RTL PDF file for Phase 1-F2."""

    project = _get_or_404(project_id)
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
def load_demo_content(project_id: str) -> ProjectSession:
    """Load backend-owned demo questions and glossary for Phase 1-B."""

    project = project_store.load_demo_content(project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


@router.patch("/{project_id}/questions/{question_id}")
def update_question(project_id: str, question_id: str, patch: QuestionPatch) -> ProjectSession:
    """Update a question card from the review step."""

    project = project_store.update_question(project_id, question_id, patch)
    if project is None:
        raise HTTPException(status_code=404, detail="Project or question not found")
    return project


@router.post("/{project_id}/questions/{question_id}/assets")
async def upload_question_asset(project_id: str, question_id: str, file: UploadFile = File(...)) -> ProjectSession:
    """Attach an optional question image/table snapshot for Phase 1-H1."""

    _get_or_404(project_id)

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
def delete_question_asset(project_id: str, question_id: str, asset_id: str) -> ProjectSession:
    """Remove a question attachment from the temporary session."""

    project = project_store.remove_question_asset(project_id, question_id, asset_id)
    if project is None:
        raise HTTPException(status_code=404, detail="Project, question, or asset not found")
    return project



@router.post("/{project_id}/questions/bulk-status")
def bulk_update_question_status(project_id: str, payload: QuestionBulkStatusRequest) -> ProjectSession:
    """Apply one review status to many questions for Phase 1-L1."""

    project = project_store.bulk_update_question_status(
        project_id,
        status=payload.status,
        include_deleted=payload.include_deleted,
    )
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


@router.post("/{project_id}/questions/reorder")
def reorder_questions(project_id: str, payload: QuestionReorderRequest) -> ProjectSession:
    """Update question order indices from the frontend."""

    project = project_store.reorder_questions(project_id, payload.ordered_question_ids)
    if project is None:
        raise HTTPException(status_code=400, detail="Invalid question order or project not found")
    return project


@router.patch("/{project_id}/glossary/{term_id}")
def update_glossary_term(project_id: str, term_id: str, patch: GlossaryTermPatch) -> ProjectSession:
    """Update one glossary term from the glossary review step."""

    project = project_store.update_glossary_term(project_id, term_id, patch)
    if project is None:
        raise HTTPException(status_code=404, detail="Project or glossary term not found")
    return project


@router.delete("/{project_id}")
def delete_project(project_id: str) -> dict[str, bool]:
    """Delete the temporary project session."""

    deleted = project_store.delete(project_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Project not found")
    return {"deleted": True}
