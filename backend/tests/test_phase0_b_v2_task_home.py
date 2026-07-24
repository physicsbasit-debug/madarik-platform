from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def test_science_task_home_component_exists() -> None:
    assert (
        ROOT / "frontend/src/features/workflow/ScienceTaskHome.tsx"
    ).exists()


def test_task_home_exposes_translation_workflows() -> None:
    content = (
        ROOT / "frontend/src/features/workflow/ScienceTaskHome.tsx"
    ).read_text(encoding="utf-8")

    assert "ترجمة سريعة" in content
    assert "بدء مشروع ورقة" in content
    assert "onQuickTranslation" in content
    assert "onProfessionalTranslation" in content


def test_product_modules_are_first_class_actions() -> None:
    content = (
        ROOT / "frontend/src/features/workflow/ScienceTaskHome.tsx"
    ).read_text(encoding="utf-8")

    assert "المناهج والدروس" in content
    assert "بنك الأسئلة" in content
    assert "منشئ الاختبارات" in content
    assert "الأنشطة التعليمية" in content
    assert "قريبًا" not in content


def test_app_starts_in_task_home_mode() -> None:
    content = (ROOT / "frontend/src/app/App.tsx").read_text(encoding="utf-8")

    assert 'useState<PlatformSection>("home")' in content
    assert "type PlatformSection" in content
    assert 'workspaceMode === "home"' in content
    assert "openQuickTranslation" in content
    assert "openProfessionalTranslation" in content

def test_workspace_can_return_to_task_home() -> None:
    content = (ROOT / "frontend/src/app/App.tsx").read_text(encoding="utf-8")

    assert "returnToTaskHome" in content
    assert "onNavigate={navigatePlatform}" in content
    assert "<PlatformShell" in content


def test_task_home_styles_are_responsive() -> None:
    content = (
        ROOT / "frontend/src/styles/global.css"
    ).read_text(encoding="utf-8")

    assert ".platform-dashboard" in content
    assert ".platform-module-grid" in content
    assert "@media (max-width: 1040px)" in content
    assert "@media (max-width: 720px)" in content


def test_phase_document_exists() -> None:
    assert (
        ROOT / "docs/PHASE_0_B_V2_NAVIGATION_AND_TASK_HOME.md"
    ).exists()
