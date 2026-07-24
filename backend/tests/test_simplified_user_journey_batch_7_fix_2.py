from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
START_WORKSPACE = ROOT / "frontend/src/features/workflow/StartWorkspace.tsx"


def test_start_workspace_accepts_complete_app_question_contract() -> None:
    content = START_WORKSPACE.read_text(encoding="utf-8")

    assert 'questions: ProjectSession["questions"];' in content


def test_start_workspace_keeps_layout_and_parse_contracts() -> None:
    content = START_WORKSPACE.read_text(encoding="utf-8")

    for contract in (
        "layoutAssets: PdfLayoutAssetInfo[];",
        "onDeleteLayoutAsset: (assetId: string) => void;",
        "onParseQuestions: () => void;",
    ):
        assert contract in content
