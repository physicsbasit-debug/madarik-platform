from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
FRONTEND = ROOT / "frontend" / "src"


def read(relative_path: str) -> str:
    return (FRONTEND / relative_path).read_text(encoding="utf-8")


def test_home_keeps_only_primary_tasks_visible_by_default() -> None:
    source = read("features/workflow/ScienceTaskHome.tsx")

    assert "ابدأ من النتيجة التي تريدها" in source
    assert "معالجة ورقة اختبار" in source
    assert "إنشاء اختبار جديد" in source
    assert "إنشاء نشاط متمايز" in source
    assert '<details className="mdk-simple-tools-drawer">' in source
    assert "أدوات إضافية" in source


def test_current_work_summary_is_reduced_to_actionable_counts() -> None:
    source = read("features/workflow/ScienceTaskHome.tsx")

    assert "mdk-simple-resume-card--focused" in source
    assert "أعمال محفوظة" in source
    assert "تحتاج مراجعة" in source
    assert "mdk-simple-resume-summary" in source
    assert "mdk-simple-resume-metrics" not in source


def test_processing_ends_with_one_review_or_export_decision() -> None:
    source = read("features/workflow/QuickTranslationWorkspace.tsx")

    assert "الخطوة التالية" in source
    assert "الورقة جاهزة للتصدير" in source
    assert "راجع الملاحظات قبل التصدير" in source
    assert "تصدير الآن" in source
    assert "مراجعة الملاحظات" in source
    assert "readyToExport ? onOpenExport : onOpenProfessionalReview" in source
    assert '<details className="mdk-simple-result-details">' in source


def test_batch_2_layout_collapses_cleanly_on_small_screens() -> None:
    source = read("styles/simplified-platform.css")

    assert ".mdk-simple-decision" in source
    assert ".mdk-simple-tools-drawer" in source
    assert ".mdk-simple-resume-summary" in source
    assert "@media (max-width: 900px)" in source
    assert "@media (max-width: 640px)" in source
    assert source.count("{") == source.count("}")
