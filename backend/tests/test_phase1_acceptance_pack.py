from io import BytesIO
from zipfile import ZipFile

from fastapi.testclient import TestClient
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

from app.main import app

client = TestClient(app)


def _build_acceptance_pdf_bytes() -> bytes:
    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=A4)
    pdf.setFont("Helvetica", 12)
    lines = [
        "1. State the function of the cell membrane. [1]",
        "2. Describe how temperature affects the rate of reaction. [2]",
        "3. Explain why current decreases when resistance increases. [2]",
        "4. Calculate the speed of a wave. [3]",
    ]
    y = 780
    for line in lines:
        pdf.drawString(72, y, line)
        y -= 30
    pdf.save()
    return buffer.getvalue()


def test_phase1_acceptance_flow_with_snapshot_round_trip() -> None:
    project_id = client.post("/api/projects", json={}).json()["id"]
    pdf_bytes = _build_acceptance_pdf_bytes()

    upload = client.post(
        f"/api/projects/{project_id}/upload-pdf",
        files={"file": ("acceptance-paper.pdf", pdf_bytes, "application/pdf")},
    )
    assert upload.status_code == 200
    assert upload.json()["extracted_text"]["is_text_based"] is True

    parsed = client.post(f"/api/projects/{project_id}/parse-questions")
    assert parsed.status_code == 200
    assert len(parsed.json()["questions"]) >= 4

    glossary = client.post(f"/api/projects/{project_id}/glossary/generate")
    assert glossary.status_code == 200

    translated = client.post(f"/api/projects/{project_id}/translate-questions")
    assert translated.status_code == 200

    bulk = client.post(
        f"/api/projects/{project_id}/questions/bulk-status",
        json={"status": "approved", "include_deleted": False},
    )
    assert bulk.status_code == 200

    readiness = client.get(f"/api/projects/{project_id}/readiness")
    assert readiness.status_code == 200
    assert readiness.json()["ready"] is True

    snapshot = client.get(f"/api/projects/{project_id}/snapshot")
    assert snapshot.status_code == 200

    imported = client.post("/api/projects/import-snapshot", json=snapshot.json())
    assert imported.status_code == 201
    imported_id = imported.json()["id"]
    assert imported_id != project_id

    imported_readiness = client.get(f"/api/projects/{imported_id}/readiness")
    assert imported_readiness.status_code == 200
    assert imported_readiness.json()["ready"] is True

    docx = client.post(f"/api/projects/{imported_id}/export/docx")
    assert docx.status_code == 200
    assert docx.content[:2] == b"PK"
    with ZipFile(BytesIO(docx.content)) as archive:
        assert "word/document.xml" in archive.namelist()

    pdf = client.post(f"/api/projects/{imported_id}/export/pdf")
    assert pdf.status_code == 200
    assert pdf.content[:4] == b"%PDF"


def test_phase1_acceptance_readiness_reports_warnings_not_blocking() -> None:
    project_id = client.post("/api/projects", json={}).json()["id"]
    client.post(f"/api/projects/{project_id}/demo-content")

    readiness = client.get(f"/api/projects/{project_id}/readiness")

    assert readiness.status_code == 200
    body = readiness.json()
    assert body["ready"] is True
    assert isinstance(body["issues"], list)
