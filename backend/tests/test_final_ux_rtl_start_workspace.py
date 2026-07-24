from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
START_WORKSPACE = ROOT / "frontend/src/features/workflow/StartWorkspace.tsx"
SIMPLIFIED_CSS = ROOT / "frontend/src/styles/simplified-platform.css"


def _source() -> str:
    return START_WORKSPACE.read_text(encoding="utf-8")


def _css() -> str:
    return SIMPLIFIED_CSS.read_text(encoding="utf-8")


def test_start_workspace_uses_responsive_rtl_work_library() -> None:
    source = _source()
    css = _css()

    assert 'className="mdk-work-library"' in source
    assert 'className="mdk-work-library__grid"' in source
    assert ".mdk-work-library__grid" in css
    assert "grid-template-columns: repeat(3, minmax(0, 1fr));" in css
    assert "@media" in css


def test_start_workspace_preserves_existing_business_callbacks() -> None:
    source = _source()

    for callback_name in (
        "onOpenProject",
        "onDeleteProject",
        "onDeleteProjects",
        "onDeleteLayoutAsset",
        "onParseQuestions",
    ):
        assert callback_name in source

    assert "onOpenProject(project.id)" in source
    assert "onDeleteProject(project.id)" in source


def test_start_workspace_preserves_layout_asset_contract() -> None:
    source = _source()

    assert "PdfLayoutAssetInfo" in source
    assert "layoutAssets: PdfLayoutAssetInfo[];" in source
    assert "onDeleteLayoutAsset: (assetId: string) => void;" in source
