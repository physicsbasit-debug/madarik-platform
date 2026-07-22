from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def test_export_redesign_uses_current_control_and_identity_layout() -> None:
    content = (
        ROOT / "frontend/src/features/export/ExportStep.tsx"
    ).read_text(encoding="utf-8")

    assert "export-control-bar-redesign" in content
    assert "export-control-actions" in content
    assert "export-identity-row" in content
    assert "export-preview-identity" not in content


def test_upload_zone_uses_dynamic_drag_state_class() -> None:
    content = (
        ROOT / "frontend/src/features/file-upload/FileUploadStep.tsx"
    ).read_text(encoding="utf-8")

    assert "start-upload-zone" in content
    assert "is-drag-active" in content
    assert "onFileSelected(file)" in content
