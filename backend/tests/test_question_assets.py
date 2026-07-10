import base64
from io import BytesIO
from zipfile import ZipFile

from fastapi.testclient import TestClient
from pypdf import PdfReader

from app.main import app
from app.models.project import ProjectMetadata, ProjectSession, QuestionAssetInfo, QuestionItem
from app.services.export import build_project_docx_bytes, build_project_pdf_bytes

client = TestClient(app)

TINY_PNG_BASE64 = (
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+/p9sAAAAASUVORK5CYII="
)


def _project_with_question_asset() -> ProjectSession:
    asset_bytes = base64.b64decode(TINY_PNG_BASE64)
    return ProjectSession(
        metadata=ProjectMetadata(
            school_name="مدرسة الباسط للتعليم الأساسي",
            subject="الفيزياء",
            paper_title="تدريب بالمرفقات",
        ),
        questions=[
            QuestionItem(
                id="q-asset",
                original_number="1",
                original_text="Use the diagram to explain the result. [2]",
                translated_text="استخدم الشكل لتفسير النتيجة. [2]",
                marks=2,
                detected_marks=2,
                order_index=1,
                attachments=[
                    QuestionAssetInfo(
                        name="diagram.png",
                        size=len(asset_bytes),
                        type="image/png",
                        data_base64=TINY_PNG_BASE64,
                    )
                ],
            )
        ],
    )


def test_upload_and_delete_question_asset_endpoint():
    project_id = client.post("/api/projects").json()["id"]
    client.post(f"/api/projects/{project_id}/demo-content")
    question_id = client.get(f"/api/projects/{project_id}").json()["questions"][0]["id"]
    image_bytes = base64.b64decode(TINY_PNG_BASE64)

    upload_response = client.post(
        f"/api/projects/{project_id}/questions/{question_id}/assets",
        files={"file": ("diagram.png", image_bytes, "image/png")},
    )

    assert upload_response.status_code == 200
    question = upload_response.json()["questions"][0]
    assert question["attachments"][0]["name"] == "diagram.png"
    asset_id = question["attachments"][0]["id"]

    delete_response = client.delete(f"/api/projects/{project_id}/questions/{question_id}/assets/{asset_id}")
    assert delete_response.status_code == 200
    assert delete_response.json()["questions"][0]["attachments"] == []


def test_question_asset_endpoint_rejects_non_image_file():
    project_id = client.post("/api/projects").json()["id"]
    client.post(f"/api/projects/{project_id}/demo-content")
    question_id = client.get(f"/api/projects/{project_id}").json()["questions"][0]["id"]

    response = client.post(
        f"/api/projects/{project_id}/questions/{question_id}/assets",
        files={"file": ("asset.txt", b"not an image", "text/plain")},
    )

    assert response.status_code == 400
    assert "PNG" in response.json()["detail"]


def test_docx_export_embeds_question_asset_media():
    docx_bytes = build_project_docx_bytes(_project_with_question_asset())

    with ZipFile(BytesIO(docx_bytes)) as archive:
        media_files = [name for name in archive.namelist() if name.startswith("word/media/")]

    assert media_files


def test_pdf_export_with_question_asset_builds_valid_pdf():
    pdf_bytes = build_project_pdf_bytes(_project_with_question_asset())

    assert pdf_bytes.startswith(b"%PDF")
    assert len(PdfReader(BytesIO(pdf_bytes)).pages) >= 1
