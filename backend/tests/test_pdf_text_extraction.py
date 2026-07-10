from fastapi.testclient import TestClient

from app.main import app
from app.services.text_extraction import extract_text_from_pdf_bytes


SAMPLE_TEXT_PDF = b'''%PDF-1.4
1 0 obj
<< /Type /Catalog /Pages 2 0 R >>
endobj
2 0 obj
<< /Type /Pages /Kids [3 0 R] /Count 1 >>
endobj
3 0 obj
<< /Type /Page /Parent 2 0 R /Resources << /Font << /F1 4 0 R >> >> /MediaBox [0 0 612 792] /Contents 5 0 R >>
endobj
4 0 obj
<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>
endobj
5 0 obj
<< /Length 79 >>
stream
BT
/F1 24 Tf
100 700 Td
(Question 1: State the function of the cell membrane.) Tj
ET
endstream
endobj
xref
0 6
0000000000 65535 f 
0000000009 00000 n 
0000000058 00000 n 
0000000115 00000 n 
0000000241 00000 n 
0000000311 00000 n 
trailer
<< /Size 6 /Root 1 0 R >>
startxref
440
%%EOF
'''

BLANK_PDF = b'''%PDF-1.4
1 0 obj
<< /Type /Catalog /Pages 2 0 R >>
endobj
2 0 obj
<< /Type /Pages /Kids [3 0 R] /Count 1 >>
endobj
3 0 obj
<< /Type /Page /Parent 2 0 R /Resources << >> /MediaBox [0 0 612 792] >>
endobj
xref
0 4
0000000000 65535 f 
0000000009 00000 n 
0000000058 00000 n 
0000000115 00000 n 
trailer
<< /Size 4 /Root 1 0 R >>
startxref
199
%%EOF
'''


def test_extract_text_from_text_based_pdf_bytes() -> None:
    result = extract_text_from_pdf_bytes(SAMPLE_TEXT_PDF)
    assert result.page_count == 1
    assert result.is_text_based is True
    assert "cell membrane" in result.text
    assert result.character_count > 20


def test_upload_pdf_endpoint_extracts_text_into_project_session() -> None:
    client = TestClient(app)
    project_id = client.post("/api/projects", json={}).json()["id"]

    response = client.post(
        f"/api/projects/{project_id}/upload-pdf",
        files={"file": ("sample.pdf", SAMPLE_TEXT_PDF, "application/pdf")},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["uploaded_file"]["name"] == "sample.pdf"
    assert body["current_step"] == "extract"
    assert body["extracted_text"]["is_text_based"] is True
    assert "Question 1" in body["extracted_text"]["text"]


def test_upload_blank_pdf_returns_clear_no_text_message() -> None:
    client = TestClient(app)
    project_id = client.post("/api/projects", json={}).json()["id"]

    response = client.post(
        f"/api/projects/{project_id}/upload-pdf",
        files={"file": ("blank.pdf", BLANK_PDF, "application/pdf")},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["extracted_text"]["is_text_based"] is False
    assert "OCR" in body["extracted_text"]["message"]


def test_upload_non_pdf_is_rejected() -> None:
    client = TestClient(app)
    project_id = client.post("/api/projects", json={}).json()["id"]

    response = client.post(
        f"/api/projects/{project_id}/upload-pdf",
        files={"file": ("notes.txt", b"not a pdf", "text/plain")},
    )

    assert response.status_code == 400
