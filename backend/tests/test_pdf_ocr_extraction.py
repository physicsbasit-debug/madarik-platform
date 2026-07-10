from io import BytesIO

import fitz
from fastapi.testclient import TestClient

from app.main import app
from app.services.pdf_ocr import PdfOcrExtractionResult

client = TestClient(app)


def _build_image_only_pdf_bytes() -> bytes:
    document = fitz.open()
    page = document.new_page(width=595, height=842)
    # The actual OCR result is monkeypatched in endpoint tests. This PDF only
    # proves that the upload path accepts a valid PDF container.
    page.draw_rect(fitz.Rect(80, 100, 520, 200), color=(0, 0, 0), width=1)
    page.insert_text((95, 150), "1. State the function of the cell membrane. [1]", fontsize=18)
    data = document.tobytes()
    document.close()
    return data


def test_upload_pdf_ocr_endpoint_stores_extracted_text(monkeypatch) -> None:
    project_id = client.post("/api/projects", json={}).json()["id"]
    pdf_bytes = _build_image_only_pdf_bytes()

    monkeypatch.setattr(
        "app.api.projects.extract_text_from_scanned_pdf_bytes",
        lambda _bytes: PdfOcrExtractionResult(
            text="[صفحة 1]\n1. State the function of the cell membrane. [1]",
            page_count=1,
            processed_pages=1,
        ),
    )

    response = client.post(
        f"/api/projects/{project_id}/upload-pdf-ocr",
        files={"file": ("scanned.pdf", pdf_bytes, "application/pdf")},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["uploaded_file"]["name"] == "scanned.pdf"
    assert body["extracted_text"]["is_text_based"] is True
    assert "cell membrane" in body["extracted_text"]["text"]
    assert "OCR" in body["extracted_text"]["message"]


def test_upload_pdf_ocr_accepts_pdf_with_no_readable_text(monkeypatch) -> None:
    project_id = client.post("/api/projects", json={}).json()["id"]
    pdf_bytes = _build_image_only_pdf_bytes()

    monkeypatch.setattr(
        "app.api.projects.extract_text_from_scanned_pdf_bytes",
        lambda _bytes: PdfOcrExtractionResult(text="", page_count=1, processed_pages=1),
    )

    response = client.post(
        f"/api/projects/{project_id}/upload-pdf-ocr",
        files={"file": ("blank-scan.pdf", pdf_bytes, "application/pdf")},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["extracted_text"]["is_text_based"] is False
    assert "OCR" in body["extracted_text"]["message"]


def test_upload_pdf_ocr_rejects_non_pdf() -> None:
    project_id = client.post("/api/projects", json={}).json()["id"]

    response = client.post(
        f"/api/projects/{project_id}/upload-pdf-ocr",
        files={"file": ("scan.png", b"not a pdf", "image/png")},
    )

    assert response.status_code == 400
    assert "PDF" in response.json()["detail"]
