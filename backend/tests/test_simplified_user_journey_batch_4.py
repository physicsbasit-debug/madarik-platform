from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
FRONTEND = ROOT / "frontend" / "src"


def read(relative_path: str) -> str:
    return (FRONTEND / relative_path).read_text(encoding="utf-8")


def test_paper_processing_starts_in_one_click_without_source_dialog() -> None:
    source = read("features/workflow/ScienceTaskHome.tsx")

    assert "onClick={onQuickTranslation}" in source
    assert "sourceChooserOpen" not in source
    assert "setSourceChooserOpen" not in source
    assert "من أين تريد اختيار الملف؟" not in source
    quick_source = read("features/workflow/QuickTranslationWorkspace.tsx")
    assert "الخطوة الوحيدة المطلوبة منك" in quick_source
    assert "اختر ورقة الاختبار" in quick_source


def test_cloud_sources_remain_available_without_blocking_primary_flow() -> None:
    source = read("features/workflow/ScienceTaskHome.tsx")

    assert 'className="mdk-simple-cloud-shortcut"' in source
    assert "ملفك محفوظ في السحابة؟" in source
    assert "Google Drive أو OneDrive" in source
    assert "onClick={onOpenCloudSources}" in source


def test_home_has_no_project_context_bar_or_visible_sync_footer() -> None:
    source = read("components/PlatformShell.tsx")

    assert 'activeSection !== "home" ? (' in source
    assert 'className="mdk-simple-context-bar"' in source
    assert '<span className="mdk-simple-sync-note" hidden>' in source
    assert '<footer className="mdk-simple-sync-note"' not in source


def test_batch_4_styles_keep_cloud_shortcut_responsive() -> None:
    source = read("styles/simplified-platform.css")

    assert ".mdk-simple-cloud-shortcut" in source
    assert ".mdk-simple-sync-note[hidden]" in source
    assert "@media (max-width: 640px)" in source
    assert source.count("{") == source.count("}")
