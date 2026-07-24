from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
QUICK = ROOT / "frontend/src/features/workflow/QuickTranslationWorkspace.tsx"
CSS = ROOT / "frontend/src/styles/simplified-platform.css"


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_batch_6_uses_one_visible_journey_state() -> None:
    source = read(QUICK)
    assert 'type JourneyView = "upload" | "processing" | "error" | "decision"' in source
    assert 'const viewStage: JourneyView' in source
    assert 'viewStage === "upload"' in source
    assert 'viewStage === "processing"' in source
    assert 'viewStage === "error"' in source
    assert 'viewStage === "decision"' in source


def test_batch_6_keeps_automatic_processing_and_single_decision() -> None:
    source = read(QUICK)
    assert "autoStartedFileRef" in source
    assert "onRunQuickTranslation();" in source
    assert "مدارك يجهّز الورقة" in source
    assert "مراجعة الملاحظات" in source
    assert "تصدير الآن" in source


def test_batch_6_exposes_clear_file_replacement_and_progress() -> None:
    source = read(QUICK)
    assert "رحلة من شاشة واحدة" in source
    assert "تغيير الملف" in source
    assert 'aria-label="تقدم معالجة الورقة"' in source
    assert "عرض ملخص المعالجة" in source


def test_batch_6_has_responsive_single_stage_styles() -> None:
    css = read(CSS)
    assert ".mdk-simple-process--single-stage" in css
    assert ".mdk-simple-journey-nav" in css
    assert ".mdk-simple-single-stage" in css
    assert ".mdk-simple-file-ribbon" in css
    assert "@media (max-width: 640px)" in css
