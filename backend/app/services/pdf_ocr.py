from __future__ import annotations

from dataclasses import dataclass

import fitz  # PyMuPDF

from app.services.ocr import OcrExtractionError, extract_text_from_image_bytes


class PdfOcrExtractionError(ValueError):
    """Raised when a scanned PDF cannot be rasterised for OCR."""


@dataclass(frozen=True)
class PdfOcrExtractionResult:
    text: str
    page_count: int
    processed_pages: int

    @property
    def character_count(self) -> int:
        return len(self.text)

    @property
    def is_text_based(self) -> bool:
        return bool(self.text.strip())

    @property
    def preview(self) -> str:
        normalized = " ".join(self.text.split())
        return normalized[:500]


def _normalise_pages_text(page_texts: list[str]) -> str:
    compact = []
    for index, text in enumerate(page_texts, start=1):
        cleaned = "\n".join(line.strip() for line in text.splitlines() if line.strip())
        if cleaned:
            compact.append(f"[صفحة {index}]\n{cleaned}")
    return "\n\n".join(compact).strip()


def extract_text_from_scanned_pdf_bytes(file_bytes: bytes, max_pages: int = 3) -> PdfOcrExtractionResult:
    """Rasterise the first pages of a scanned PDF and run English OCR.

    Phase 1-I2 intentionally keeps this conservative:
    - English OCR only.
    - Limited number of pages to avoid slow CI/runtime.
    - No layout reconstruction.
    - No automatic extraction of diagrams as separate question assets yet.

    The goal is intake, not pretending the PDF layout problem has been solved by
    optimism and three function calls. That lie has already harmed enough codebases.
    """

    if not file_bytes:
        raise PdfOcrExtractionError("ملف PDF فارغ ولا يمكن تشغيل OCR عليه.")

    try:
        document = fitz.open(stream=file_bytes, filetype="pdf")
    except Exception as exc:  # pragma: no cover - PyMuPDF raises varied errors
        raise PdfOcrExtractionError("تعذر فتح PDF لتشغيل OCR.") from exc

    try:
        page_count = document.page_count
        if page_count == 0:
            raise PdfOcrExtractionError("ملف PDF لا يحتوي على صفحات قابلة للمعالجة.")

        processed_pages = min(page_count, max(max_pages, 1))
        page_texts: list[str] = []

        for page_index in range(processed_pages):
            page = document.load_page(page_index)
            pixmap = page.get_pixmap(matrix=fitz.Matrix(2, 2), alpha=False)
            image_bytes = pixmap.tobytes("png")
            try:
                ocr_result = extract_text_from_image_bytes(image_bytes)
            except OcrExtractionError:
                page_texts.append("")
                continue
            page_texts.append(ocr_result.text)

        text = _normalise_pages_text(page_texts)
        return PdfOcrExtractionResult(text=text, page_count=page_count, processed_pages=processed_pages)
    finally:
        document.close()
