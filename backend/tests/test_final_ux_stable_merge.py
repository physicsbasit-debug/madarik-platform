from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]

def test_render_experiment_files_are_absent() -> None:
    blocked = [
        "render.yaml", "backend/Dockerfile", "backend/.dockerignore",
        "backend/tests/test_phase5_a_render_backend_preview.py",
        "docs/PHASE_5_A_RENDER_BACKEND_PREVIEW.md",
        ".github/workflows/pages-preview.yml",
    ]
    for rel in blocked:
        assert not (ROOT / rel).exists(), rel

def test_workspace_components_exist() -> None:
    expected = [
        "frontend/src/components/WorkspaceShell.tsx",
        "frontend/src/components/WorkspaceSidebar.tsx",
        "frontend/src/components/WorkspaceTopBar.tsx",
    ]
    for rel in expected:
        assert (ROOT / rel).exists(), rel

def test_redesigned_workspaces_exist() -> None:
    expected = [
        "frontend/src/features/workflow/StartWorkspace.tsx",
        "frontend/src/features/workflow/UnifiedReviewWorkspace.tsx",
        "frontend/src/features/export/ExportStep.tsx",
    ]
    for rel in expected:
        assert (ROOT / rel).exists(), rel

def test_main_deployment_files_remain_unmodified() -> None:
    config=(ROOT/'backend/app/core/config.py').read_text(encoding='utf-8')
    assert 'MADARIK_ALLOWED_ORIGINS' not in config
    vite=(ROOT/'frontend/vite.config.ts').read_text(encoding='utf-8')
    assert 'VITE_BASE_PATH' not in vite
    assert 'loadEnv' not in vite

def test_merge_documentation_exists() -> None:
    assert (ROOT/'docs/FINAL_UX_STABLE_MERGE.md').exists()
