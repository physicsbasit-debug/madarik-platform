from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
FRONTEND = ROOT / "frontend" / "src"


def read(relative_path: str) -> str:
    return (FRONTEND / relative_path).read_text(encoding="utf-8")


def test_platform_shell_uses_three_primary_destinations() -> None:
    source = read("components/PlatformShell.tsx")

    assert "const primaryNavigation" in source
    assert 'label: "الرئيسية"' in source
    assert 'label: "أعمالي"' in source
    assert 'label: "بنك الأسئلة"' in source
    assert "navigationGroups" not in source
    assert "mdk-simple-primary-nav" in source


def test_home_starts_from_the_three_user_tasks() -> None:
    source = read("features/workflow/ScienceTaskHome.tsx")

    assert "ماذا تريد أن تنجز اليوم؟" in source
    assert "معالجة ورقة اختبار" in source
    assert "إنشاء اختبار جديد" in source
    assert "إنشاء نشاط متمايز" in source
    assert "Google Drive" in source
    assert "OneDrive" in source
    assert "moduleCards.map" not in source


def test_ready_paper_flow_is_upload_prepare_review_export() -> None:
    source = read("features/workflow/QuickTranslationWorkspace.tsx")

    assert "اختر ورقة الاختبار" in source
    assert "جهّز الورقة" in source
    assert "راجع النتيجة ثم صدّر" in source
    assert "بيانات الورقة الاختيارية" in source
    assert "تشغيل الترجمة السريعة" not in source
    assert "translationAttentionCount" in source


def test_simplified_ui_has_responsive_and_accessibility_guards() -> None:
    source = read("styles/simplified-platform.css")

    assert source.count("@media") >= 2
    assert ":focus-visible" in source
    assert ".mdk-simple-mobile-panel" in source
    assert ".mdk-simple-inline-warning" in source
    assert source.count("{") == source.count("}")
