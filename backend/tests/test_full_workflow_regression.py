from io import BytesIO

from fastapi.testclient import TestClient
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

from app.main import app

client = TestClient(app)


def _build_text_pdf_bytes() -> bytes:
    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=A4)
    pdf.setFont("Helvetica", 12)
    pdf.drawString(72, 780, "1. State the function of the cell membrane. [1]")
    pdf.drawString(72, 750, "2. Explain why current decreases when resistance increases. [2]")
    pdf.drawString(72, 720, "3. Calculate the speed of a wave. [3]")
    pdf.save()
    return buffer.getvalue()


def test_full_text_pdf_to_docx_and_pdf_workflow() -> None:
    project_id = client.post("/api/projects", json={}).json()["id"]
    pdf_bytes = _build_text_pdf_bytes()

    upload_response = client.post(
        f"/api/projects/{project_id}/upload-pdf",
        files={"file": ("science-paper.pdf", pdf_bytes, "application/pdf")},
    )
    assert upload_response.status_code == 200
    upload_body = upload_response.json()
    assert upload_body["extracted_text"]["is_text_based"] is True
    assert "cell membrane" in upload_body["extracted_text"]["text"]

    parse_response = client.post(f"/api/projects/{project_id}/parse-questions")
    assert parse_response.status_code == 200
    parsed_body = parse_response.json()
    assert len(parsed_body["questions"]) >= 3
    assert parsed_body["questions"][0]["marks"] == 1

    glossary_response = client.post(f"/api/projects/{project_id}/glossary/generate")
    assert glossary_response.status_code == 200
    glossary_body = glossary_response.json()
    assert len(glossary_body["glossary"]) >= 1

    translate_response = client.post(f"/api/projects/{project_id}/translate-questions")
    assert translate_response.status_code == 200
    translated_body = translate_response.json()
    active_questions = [q for q in translated_body["questions"] if q["status"] != "deleted"]
    assert active_questions
    assert all(q["translated_text"].strip() for q in active_questions)

    readiness_response = client.get(f"/api/projects/{project_id}/readiness")
    assert readiness_response.status_code == 200
    readiness_body = readiness_response.json()
    assert readiness_body["ready"] is True
    assert readiness_body["exportable_question_count"] >= 3
    assert readiness_body["total_marks"] >= 6

    docx_response = client.post(f"/api/projects/{project_id}/export/docx")
    assert docx_response.status_code == 200
    assert docx_response.headers["content-type"].startswith(
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    )
    assert docx_response.content[:2] == b"PK"

    pdf_response = client.post(f"/api/projects/{project_id}/export/pdf")
    assert pdf_response.status_code == 200
    assert pdf_response.headers["content-type"].startswith("application/pdf")
    assert pdf_response.content[:4] == b"%PDF"


def test_full_workflow_blocks_export_when_questions_deleted() -> None:
    project_id = client.post("/api/projects", json={}).json()["id"]
    client.post(f"/api/projects/{project_id}/demo-content")
    project = client.get(f"/api/projects/{project_id}").json()

    for question in project["questions"]:
        response = client.patch(
            f"/api/projects/{project_id}/questions/{question['id']}",
            json={"status": "deleted"},
        )
        assert response.status_code == 200

    readiness_response = client.get(f"/api/projects/{project_id}/readiness")
    assert readiness_response.status_code == 200
    readiness_body = readiness_response.json()
    assert readiness_body["ready"] is False
    assert any(issue["code"] == "all_questions_deleted" for issue in readiness_body["issues"])
