from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def read(relative: str) -> str:
    return (ROOT / relative).read_text(encoding="utf-8")


def test_platform_shell_exposes_all_product_modules() -> None:
    shell = read("frontend/src/components/PlatformShell.tsx")

    for section in (
        '"home"',
        '"professional"',
        '"quick"',
        '"cloud-sources"',
        '"curriculum"',
        '"question-bank"',
        '"assessment"',
        '"differentiated-activities"',
        '"scientific-diagrams"',
    ):
        assert section in shell

    for label in (
        "لوحة التحكم",
        "المشاريع والمعالجة",
        "المصادر السحابية",
        "المناهج والدروس",
        "بنك الأسئلة",
        "منشئ الاختبارات",
        "الأنشطة التعليمية",
        "الرسوم العلمية",
    ):
        assert label in shell


def test_all_workspace_modes_render_inside_platform_shell() -> None:
    app = read("frontend/src/app/App.tsx")

    assert "let platformContent: ReactNode" in app
    assert "<PlatformShell" in app
    assert "activeSection={workspaceMode}" in app
    assert "onNavigate={navigatePlatform}" in app
    assert "{platformContent}" in app

    shell_position = app.index("<PlatformShell")
    assert app.index('workspaceMode === "home"') < shell_position
    assert app.index('workspaceMode === "quick"') < shell_position
    assert app.index('workspaceMode === "curriculum"') < shell_position
    assert app.index('workspaceMode === "question-bank"') < shell_position


def test_dashboard_presents_real_modules_and_current_project() -> None:
    dashboard = read(
        "frontend/src/features/workflow/ScienceTaskHome.tsx"
    )

    assert "المشروع النشط" in dashboard
    assert "المشاريع المحفوظة" in dashboard
    assert "مزود الترجمة" in dashboard
    assert "وحدات المنصة" in dashboard
    assert "رحلة العمل المتكاملة" in dashboard
    assert "قريبًا" not in dashboard

    for callback in (
        "onOpenCloudSources",
        "onOpenCurriculum",
        "onOpenQuestionBank",
        "onOpenAssessmentBuilder",
        "onOpenDifferentiatedActivities",
        "onOpenScientificDiagrams",
    ):
        assert callback in dashboard


def test_paper_workflow_is_nested_and_responsive() -> None:
    shell = read("frontend/src/components/WorkspaceShell.tsx")
    sidebar = read("frontend/src/components/WorkspaceSidebar.tsx")
    css = read("frontend/src/styles/global.css")

    assert "professional-workspace" in shell
    assert "professional-workspace-layout" in shell
    assert "workflow-rail" in sidebar
    assert "مساحة معالجة الورقة" in sidebar
    assert ".platform-shell" in css
    assert ".platform-account-drawer" in css
    assert ".platform-dashboard" in css
    assert "@media (max-width: 1040px)" in css
    assert "@media (max-width: 720px)" in css
