from io import BytesIO

from fastapi.testclient import TestClient
from pypdf import PdfReader

from app.main import app
from app.models.project import OutputMode, ProjectMetadata, ProjectSession, QuestionItem, QuestionStatus
from app.services.export import build_project_pdf_bytes

client = TestClient(app)


def _pdf_page_count(pdf_bytes: bytes) -> int:
    reader = PdfReader(BytesIO(pdf_bytes))
    return len(reader.pages)


def test_build_project_pdf_arabic_export_filters_deleted_questions():
    project = ProjectSession(
        metadata=ProjectMetadata(
            school_name="مدرسة الباسط للتعليم الأساسي",
            subject="الفيزياء",
            grade="العاشر",
            paper_title="تدريب القوى",
            teacher_name="أ. وليد الهنائي",
            output_mode=OutputMode.arabic,
        ),
        questions=[
            QuestionItem(
                id="q-1",
                original_number="1",
                original_text="State the unit of force. [1]",
                translated_text="اذكر وحدة القوة. [1]",
                marks=1,
                detected_marks=1,
                order_index=2,
            ),
            QuestionItem(
                id="q-2",
                original_number="2",
                original_text="Explain why the object accelerates. [2]",
                translated_text="فسّر لماذا يتسارع الجسم. [2]",
                marks=2,
                detected_marks=2,
                order_index=1,
            ),
            QuestionItem(
                id="q-3",
                original_number="3",
                original_text="Deleted question",
                translated_text="سؤال محذوف",
                marks=1,
                detected_marks=1,
                order_index=3,
                status=QuestionStatus.deleted,
            ),
        ],
    )

    pdf_bytes = build_project_pdf_bytes(project)

    assert pdf_bytes.startswith(b"%PDF")
    assert _pdf_page_count(pdf_bytes) >= 1
    assert len(pdf_bytes) > 5000


def test_build_project_pdf_bilingual_export_builds_valid_pdf():
    project = ProjectSession(
        metadata=ProjectMetadata(
            paper_title="Cells practice",
            subject="الأحياء",
            output_mode=OutputMode.bilingual,
        ),
        questions=[
            QuestionItem(
                id="q-1",
                original_number="1",
                original_text="State the function of the cell membrane. [1]",
                translated_text="اذكر وظيفة غشاء الخلية. [1]",
                marks=1,
                detected_marks=1,
                order_index=1,
            )
        ],
    )

    pdf_bytes = build_project_pdf_bytes(project)

    assert pdf_bytes.startswith(b"%PDF")
    assert _pdf_page_count(pdf_bytes) == 1


def test_export_pdf_endpoint_returns_downloadable_pdf_file():
    create_response = client.post("/api/projects")
    project_id = create_response.json()["id"]

    demo_response = client.post(f"/api/projects/{project_id}/demo-content")
    assert demo_response.status_code == 200

    translate_response = client.post(f"/api/projects/{project_id}/translate-questions")
    assert translate_response.status_code == 200

    response = client.post(f"/api/projects/{project_id}/export/pdf")

    assert response.status_code == 200
    assert response.headers["content-type"] == "application/pdf"
    assert "attachment" in response.headers["content-disposition"]
    assert response.content.startswith(b"%PDF")
    assert _pdf_page_count(response.content) >= 1


def test_export_pdf_endpoint_rejects_empty_active_questions():
    create_response = client.post("/api/projects")
    project_id = create_response.json()["id"]

    response = client.post(f"/api/projects/{project_id}/export/pdf")

    assert response.status_code == 400
    assert "لا توجد أسئلة" in response.json()["detail"]
