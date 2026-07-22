from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
APP = ROOT / "frontend/src/app/App.tsx"
UPLOAD = ROOT / "frontend/src/features/file-upload/FileUploadStep.tsx"
TYPES = ROOT / "frontend/src/types/project.ts"
CSS = ROOT / "frontend/src/styles/global.css"


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_initial_extraction_has_explicit_phases() -> None:
    content = read(TYPES)
    for phase in ("uploading", "reading", "ocr", "success", "error"):
        assert f"| '{phase}'" in content


def test_upload_flow_does_not_auto_extract_layout_assets() -> None:
    content = read(APP)
    handler = content.split("function handleFileSelected", 1)[1].split(
        "async function handleLayoutAssetDelete", 1
    )[0]
    assert "extractPdfLayoutAssets" not in handler
    assert "تحليل الرسوم مؤجل للمراجعة" in handler


def test_upload_flow_supports_retry_and_elapsed_feedback() -> None:
    content = read(UPLOAD)
    assert "onRetryInitialExtraction" in content
    assert "الزمن المنقضي" in content
    assert "إعادة المحاولة" in content
    assert "initial-extraction-progress" in content


def test_pdf_ocr_phase_is_reported_before_fallback() -> None:
    content = read(APP)
    assert 'phase: "ocr"' in content
    assert "الملف مصوّر. جارٍ تشغيل OCR" in content


def test_fast_extraction_styles_cover_running_success_and_error() -> None:
    content = read(CSS)
    assert ".initial-extraction-progress.phase-reading" in content
    assert ".initial-extraction-progress.phase-success" in content
    assert ".initial-extraction-progress.phase-error" in content
