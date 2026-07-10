import base64
from io import BytesIO
from zipfile import ZipFile

from fastapi.testclient import TestClient
from pypdf import PdfReader

from app.main import app
from app.models.project import OutputMode, ProjectLogoInfo, ProjectMetadata, ProjectSession, QuestionItem
from app.services.export import build_project_docx_bytes, build_project_pdf_bytes

client = TestClient(app)

TINY_PNG_BASE64 = (
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+/p9sAAAAASUVORK5CYII="
)


def _project_with_logo() -> ProjectSession:
    return ProjectSession(
        metadata=ProjectMetadata(
            school_name="مدرسة الباسط للتعليم الأساسي",
            subject="الفيزياء",
            paper_title="تدريب بالشعار",
            output_mode=OutputMode.bilingual,
        ),
        school_logo=ProjectLogoInfo(
            name="logo.png",
            size=len(base64.b64decode(TINY_PNG_BASE64)),
            type="image/png",
            data_base64=TINY_PNG_BASE64,
        ),
        questions=[
            QuestionItem(
                id="q-1",
                original_number="1",
                original_text="State the unit of force. [1]",
                translated_text="اذكر وحدة القوة. [1]",
                marks=1,
                detected_marks=1,
                order_index=1,
            )
        ],
    )


def test_docx_export_embeds_school_logo_media():
    docx_bytes = build_project_docx_bytes(_project_with_logo())

    with ZipFile(BytesIO(docx_bytes)) as archive:
        media_files = [name for name in archive.namelist() if name.startswith("word/media/")]

    assert media_files


def test_pdf_export_with_school_logo_builds_valid_pdf():
    pdf_bytes = build_project_pdf_bytes(_project_with_logo())

    assert pdf_bytes.startswith(b"%PDF")
    assert len(PdfReader(BytesIO(pdf_bytes)).pages) >= 1


def test_upload_and_delete_school_logo_endpoint():
    project_id = client.post("/api/projects").json()["id"]
    logo_bytes = base64.b64decode(TINY_PNG_BASE64)

    upload_response = client.post(
        f"/api/projects/{project_id}/school-logo",
        files={"file": ("logo.png", logo_bytes, "image/png")},
    )
    assert upload_response.status_code == 200
    assert upload_response.json()["school_logo"]["name"] == "logo.png"

    delete_response = client.delete(f"/api/projects/{project_id}/school-logo")
    assert delete_response.status_code == 200
    assert delete_response.json()["school_logo"] is None


def test_upload_school_logo_rejects_non_image_file():
    project_id = client.post("/api/projects").json()["id"]

    response = client.post(
        f"/api/projects/{project_id}/school-logo",
        files={"file": ("not-logo.txt", b"not an image", "text/plain")},
    )

    assert response.status_code == 400
    assert "PNG" in response.json()["detail"]
