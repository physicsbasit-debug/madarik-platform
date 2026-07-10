from fastapi import APIRouter, File, HTTPException, UploadFile, status

from app.models.project import (
    ExtractedTextInfo,
    GlossaryTermPatch,
    ProjectMetadata,
    ProjectSession,
    QuestionPatch,
    QuestionReorderRequest,
    StepUpdate,
    UploadedFileInfo,
)
from app.services.session_store import project_store
from app.services.question_parser import parse_questions_from_text
from app.services.text_extraction import TextExtractionError, extract_text_from_pdf_bytes

router = APIRouter(prefix="/projects", tags=["projects"])


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
