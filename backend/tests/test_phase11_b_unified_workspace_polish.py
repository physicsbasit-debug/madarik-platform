from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def read(relative: str) -> str:
    return (ROOT / relative).read_text(encoding="utf-8")


def test_topbar_more_action_is_named_and_content_is_centered() -> None:
    shell = read("frontend/src/components/PlatformShell.tsx")

    assert "MoreHorizontal" in shell
    assert "<span>المزيد</span>" in shell
    assert 'className="platform-content-inner"' in shell
    assert "ChevronDown" not in shell


def test_dashboard_copy_is_product_focused_and_professional() -> None:
    dashboard = read(
        "frontend/src/features/workflow/ScienceTaskHome.tsx"
    )

    assert "من المصدر إلى الاختبار في مساحة عمل واحدة" in dashboard
    assert "مساحة موحدة للمحتوى العلمي والتقويم" in dashboard
    assert "تقدم صغير للبشرية" not in dashboard
    assert "محاولة تذكر أين اختفت" not in dashboard


def test_phase11_b_adds_shared_visual_tokens_and_focus_states() -> None:
    css = read("frontend/src/styles/global.css")

    assert "Phase 11-B: Unified workspace polish" in css
    assert "--platform-radius-xl" in css
    assert "--platform-shadow-soft" in css
    assert ".platform-content-inner" in css
    assert ":focus-visible" in css


def test_all_first_class_module_headers_share_one_visual_language() -> None:
    css = read("frontend/src/styles/global.css")

    for header in (
        ".cloud-sources-header",
        ".curriculum-browser-header",
        ".question-bank-library-header",
        ".assessment-builder-header",
        ".differentiated-header",
        ".scientific-diagrams-header",
        ".quick-translation-header",
    ):
        assert header in css

    assert "One visual language for all first-class modules" in css


def test_dashboard_and_navigation_are_compact_at_medium_widths() -> None:
    css = read("frontend/src/styles/global.css")

    assert "@media (max-width: 1360px)" in css
    assert "@media (max-width: 1120px)" in css
    assert "grid-template-columns: 238px minmax(0, 1fr)" in css
    assert "grid-template-columns: repeat(2, minmax(0, 1fr))" in css


def test_navigation_items_expose_full_labels_to_assistive_technology() -> None:
    shell = read("frontend/src/components/PlatformShell.tsx")

    assert "title={item.label}" in shell
    assert 'aria-current={active ? "page" : undefined}' in shell
