from __future__ import annotations

from dataclasses import dataclass
from io import BytesIO

from pypdf import PdfReader


class TextExtractionError(ValueError):
    """Raised when a file cannot be processed as a text-based PDF."""


@dataclass(frozen=True)
class PdfTextExtractionResult:
    """Raw PDF text extraction result used by the API and tests."""

    text: str
    page_count: int

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


def _normalize_page_text(page_text: str | None) -> str:
    if not page_text:
        return ""
    # Keep line breaks useful for later question parsing, but remove excessive empty lines.
    lines = [line.strip() for line in page_text.splitlines()]
    compact_lines = [line for line in lines if line]
    return "\n".join(compact_lines)


def extract_text_from_pdf_bytes(file_bytes: bytes) -> PdfTextExtractionResult:
    """Extract selectable text from a PDF file.

    Phase 1-C intentionally supports text-based PDFs only. Scanned/image PDFs
    should return a clear no-text result instead of pretending OCR exists.
    """

    if not file_bytes:
        raise TextExtractionError("الملف فارغ ولا يمكن استخراج نص منه.")

    try:
        reader = PdfReader(BytesIO(file_bytes))
    except Exception as exc:  # pragma: no cover - pypdf exception classes vary by version
        raise TextExtractionError("تعذر فتح الملف كملف PDF صالح.") from exc

    page_texts: list[str] = []
    for page in reader.pages:
        page_texts.append(_normalize_page_text(page.extract_text()))

    text = "\n\n".join(page_text for page_text in page_texts if page_text).strip()
    return PdfTextExtractionResult(text=text, page_count=len(reader.pages))
