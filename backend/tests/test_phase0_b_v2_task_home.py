from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def test_science_task_home_component_exists() -> None:
    assert (
        ROOT / "frontend/src/features/workflow/ScienceTaskHome.tsx"
    ).exists()


def test_task_home_exposes_two_real_workflows() -> None:
    content = (
        ROOT / "frontend/src/features/workflow/ScienceTaskHome.tsx"
    ).read_text(encoding="utf-8")

    assert "ترجمة سريعة" in content
    assert "ترجمة احترافية" in content
    assert "onQuickTranslation" in content
    assert "onProfessionalTranslation" in content


def test_future_tasks_are_informational_only() -> None:
    content = (
        ROOT / "frontend/src/features/workflow/ScienceTaskHome.tsx"
    ).read_text(encoding="utf-8")

    assert "مكتبة المناهج والمصادر" in content
    assert "بنك الأسئلة" in content
    assert "إنشاء اختبار" in content
    assert "أنشطة متمايزة" in content
    assert "قريبًا" in content


def test_app_starts_in_task_home_mode() -> None:
    content = (ROOT / "frontend/src/app/App.tsx").read_text(encoding="utf-8")

    assert 'useState<"home" | "quick" | "professional">("home")' in content
    assert 'workspaceMode === "home"' in content
    assert "openQuickTranslation" in content
    assert "openProfessionalTranslation" in content


def test_workspace_can_return_to_task_home() -> None:
    content = (ROOT / "frontend/src/app/App.tsx").read_text(encoding="utf-8")

    assert "returnToTaskHome" in content
    assert "العودة إلى المهام" in content


def test_task_home_styles_are_responsive() -> None:
    content = (
        ROOT / "frontend/src/styles/global.css"
    ).read_text(encoding="utf-8")

    assert ".science-task-home" in content
    assert ".science-task-primary-grid" in content
    assert "@media (max-width: 820px)" in content
    assert "@media (max-width: 560px)" in content


def test_phase_document_exists() -> None:
    assert (
        ROOT / "docs/PHASE_0_B_V2_NAVIGATION_AND_TASK_HOME.md"
    ).exists()
