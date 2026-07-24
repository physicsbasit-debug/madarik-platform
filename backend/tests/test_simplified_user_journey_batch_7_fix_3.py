from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
START_WORKSPACE = ROOT / "frontend/src/features/workflow/StartWorkspace.tsx"


def read_start_workspace() -> str:
    return START_WORKSPACE.read_text(encoding="utf-8")


def test_current_work_keeps_professional_overview_contract() -> None:
    content = read_start_workspace()
    assert 'className="mdk-current-work start-overview-strip"' in content


def test_legacy_layout_delete_contract_is_preserved_but_non_blocking() -> None:
    content = read_start_workspace()
    assert "interface StartWorkspaceLegacyCallbacks" in content
    assert "onDeleteLayoutAsset: (assetId: string) => void;" in content
    assert (
        'onDeleteLayoutAsset?: StartWorkspaceLegacyCallbacks["onDeleteLayoutAsset"];'
        in content
    )
