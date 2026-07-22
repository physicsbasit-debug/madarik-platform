from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]


def read(relative_path: str) -> str:
    return (REPO_ROOT / relative_path).read_text(encoding="utf-8")


def test_rtl_workspace_shell_components_exist() -> None:
    components = REPO_ROOT / "frontend" / "src" / "components"
    assert (components / "WorkspaceShell.tsx").exists()
    assert (components / "WorkspaceSidebar.tsx").exists()
    assert (components / "WorkspaceTopBar.tsx").exists()
    assert (components / "WorkflowStatusStrip.tsx").exists()


def test_app_uses_rtl_workspace_shell_without_changing_stage_contract() -> None:
    app = read("frontend/src/app/App.tsx")
    steps = read("frontend/src/constants/steps.ts")

    assert "<WorkspaceShell" in app
    assert "<WorkspaceSidebar" in app
    assert "<WorkspaceTopBar" in app
    assert "<WorkflowStatusStrip" in app
    assert "StartWorkspace" in app
    assert "UnifiedReviewWorkspace" in app
    assert "ExportStep" in app
    assert "key: 'start'" in steps
    assert "key: 'review'" in steps
    assert "key: 'export'" in steps


def test_workspace_is_explicitly_rtl_and_sidebar_is_on_the_right() -> None:
    shell = read("frontend/src/components/WorkspaceShell.tsx")
    css = read("frontend/src/styles/global.css")

    assert 'dir="rtl"' in shell
    assert ".rtl-workspace-shell" in css
    assert "grid-template-columns: 286px minmax(0, 1fr)" in css
    assert ".workspace-sidebar" in css
    assert "grid-column: 1" in css


def test_rtl_phase_keeps_business_logic_out_of_new_components() -> None:
    for component in (
        "WorkspaceShell.tsx",
        "WorkspaceSidebar.tsx",
        "WorkspaceTopBar.tsx",
        "WorkflowStatusStrip.tsx",
    ):
        content = read(f"frontend/src/components/{component}")
        assert "../services/api" not in content
        assert "fetch(" not in content
