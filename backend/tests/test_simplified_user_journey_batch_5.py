from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SHELL = (ROOT / "frontend/src/components/PlatformShell.tsx").read_text(encoding="utf-8")
HOME = (ROOT / "frontend/src/features/workflow/ScienceTaskHome.tsx").read_text(encoding="utf-8")
CSS = (ROOT / "frontend/src/styles/simplified-platform.css").read_text(encoding="utf-8")


def test_snapshot_controls_are_hidden_under_advanced_management() -> None:
    assert '<details className="mdk-simple-advanced-menu">' in SHELL
    assert '<summary>إدارة متقدمة</summary>' in SHELL
    assert "استيراد نسخة عمل" in SHELL
    assert "تنزيل نسخة العمل" in SHELL


def test_primary_header_stays_focused_on_three_destinations() -> None:
    assert '{ key: "home", label: "الرئيسية"' in SHELL
    assert '{ key: "professional", label: "أعمالي"' in SHELL
    assert '{ key: "question-bank", label: "بنك الأسئلة"' in SHELL
    assert 'title={item.label}' in SHELL


def test_home_only_surfaces_translation_or_connection_problems() -> None:
    assert 'const homeAlertText =' in HOME
    assert 'apiStatus === "offline"' in HOME
    assert '!translationProviderStatus?.configured' in HOME
    assert 'translationProviderStatus.ready === false' in HOME
    assert '{homeAlertText ? (' in HOME
    assert 'role="status"' in HOME
    assert "function providerLabel" not in HOME
    assert "{providerLabel(translationProviderStatus)}" not in HOME
    assert 'apiStatus === "offline" ? "وضع محلي" : "الحفظ التلقائي يعمل"' not in HOME


def test_context_and_advanced_controls_have_compact_styles() -> None:
    assert ".mdk-simple-advanced-menu" in CSS
    assert ".mdk-simple-home-status.is-warning" in CSS
    assert "grid-template-columns: auto minmax(0, 1fr);" in CSS
