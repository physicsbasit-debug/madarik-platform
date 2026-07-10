from io import BytesIO
from pathlib import Path

from fastapi.testclient import TestClient
from PIL import Image, ImageDraw, ImageFont

from app.main import app
from app.services.ocr import extract_text_from_image_bytes

client = TestClient(app)


def _build_text_image_bytes(text: str = "1. State the function of the cell membrane. [1]") -> bytes:
    image = Image.new("RGB", (1200, 220), "white")
    draw = ImageDraw.Draw(image)
    font_path = Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf")
    font = ImageFont.truetype(str(font_path), 34) if font_path.exists() else ImageFont.load_default()
    draw.text((30, 70), text, fill="black", font=font)
    buffer = BytesIO()
    image.save(buffer, format="PNG")
    return buffer.getvalue()


def test_extract_text_from_image_bytes_reads_clear_english_text() -> None:
    image_bytes = _build_text_image_bytes()

    result = extract_text_from_image_bytes(image_bytes)

    normalized = result.text.lower()
    assert result.is_text_based is True
    assert "state" in normalized
    assert "cell membrane" in normalized
    assert result.character_count > 10


def test_upload_image_ocr_endpoint_stores_extracted_text() -> None:
    project_id = client.post("/api/projects", json={}).json()["id"]
    image_bytes = _build_text_image_bytes("1. Explain why the current decreases. [2]")

    response = client.post(
        f"/api/projects/{project_id}/upload-image-ocr",
        files={"file": ("question.png", image_bytes, "image/png")},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["uploaded_file"]["name"] == "question.png"
    assert body["extracted_text"]["is_text_based"] is True
    assert "current" in body["extracted_text"]["text"].lower()
    assert "OCR" in body["extracted_text"]["message"]


def test_upload_image_ocr_rejects_non_image() -> None:
    project_id = client.post("/api/projects", json={}).json()["id"]

    response = client.post(
        f"/api/projects/{project_id}/upload-image-ocr",
        files={"file": ("notes.txt", b"hello", "text/plain")},
    )

    assert response.status_code == 400
    assert "PNG" in response.json()["detail"]
