from io import BytesIO

from docx import Document
from fastapi.testclient import TestClient

from app.main import app
from app.models.project import OutputMode, ProjectMetadata, ProjectSession, QuestionItem, QuestionStatus
from app.services.export import build_project_docx_bytes

client = TestClient(app)


def _read_docx_text(docx_bytes: bytes) -> str:
    document = Document(BytesIO(docx_bytes))
    parts: list[str] = []
    parts.extend(paragraph.text for paragraph in document.paragraphs)
    for table in document.tables:
        for row in table.rows:
            for cell in row.cells:
                parts.extend(paragraph.text for paragraph in cell.paragraphs)
    return "\n".join(parts)


def test_build_project_docx_arabic_export_filters_deleted_questions():
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

    docx_bytes = build_project_docx_bytes(project)

    assert docx_bytes.startswith(b"PK")
    text = _read_docx_text(docx_bytes)
    assert "تدريب القوى" in text
    assert "مدرسة الباسط" in text
    assert "فسّر لماذا يتسارع الجسم" in text
    assert "اذكر وحدة القوة" in text
    assert "سؤال محذوف" not in text
    assert "السؤال 1 [2]" in text
    assert "السؤال 2 [1]" in text


def test_build_project_docx_bilingual_export_includes_original_and_translation():
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

    text = _read_docx_text(build_project_docx_bytes(project))

    assert "State the function of the cell membrane" in text
    assert "اذكر وظيفة غشاء الخلية" in text
    assert "ثنائية اللغة" in text


def test_export_docx_endpoint_returns_downloadable_word_file():
    create_response = client.post("/api/projects")
    project_id = create_response.json()["id"]

    demo_response = client.post(f"/api/projects/{project_id}/demo-content")
    assert demo_response.status_code == 200

    translate_response = client.post(f"/api/projects/{project_id}/translate-questions")
    assert translate_response.status_code == 200

    response = client.post(f"/api/projects/{project_id}/export/docx")

    assert response.status_code == 200
    assert response.headers["content-type"] == "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    assert "attachment" in response.headers["content-disposition"]
    assert response.content.startswith(b"PK")
    assert "منصة مدارك" in _read_docx_text(response.content)


def test_export_docx_endpoint_rejects_empty_active_questions():
    create_response = client.post("/api/projects")
    project_id = create_response.json()["id"]

    response = client.post(f"/api/projects/{project_id}/export/docx")

    assert response.status_code == 400
    assert "لا توجد أسئلة" in response.json()["detail"]
