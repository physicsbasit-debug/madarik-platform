from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def test_choice_cards_use_horizontal_inner_layout() -> None:
    content = (
        ROOT / "frontend/src/features/export/ExportStep.tsx"
    ).read_text(encoding="utf-8")

    assert content.count('className="export-choice-card-body"') == 2
    assert "نسخة عربية نظيفة" in content
    assert "Word DOCX" in content


def test_preview_and_readiness_are_two_columns_only() -> None:
    content = (
        ROOT / "frontend/src/features/export/ExportStep.tsx"
    ).read_text(encoding="utf-8")

    preview_index = content.index('className="export-preview-grid"')
    ready_index = content.index("export-ready-card", preview_index)
    identity_index = content.index("export-identity-row", preview_index)

    assert preview_index < ready_index < identity_index


def test_identity_is_full_width_below_preview() -> None:
    content = (
        ROOT / "frontend/src/features/export/ExportStep.tsx"
    ).read_text(encoding="utf-8")

    assert "export-identity-row-content" in content
    assert "export-preview-identity" not in content


def test_primary_export_action_is_stacked() -> None:
    content = (
        ROOT / "frontend/src/styles/global.css"
    ).read_text(encoding="utf-8")

    assert ".export-primary-action" in content
    assert "grid-template-columns: 1fr;" in content
    assert ".export-primary-message" in content


def test_fake_letter_icons_are_removed() -> None:
    content = (
        ROOT / "frontend/src/styles/global.css"
    ).read_text(encoding="utf-8")

    assert "content: none !important;" in content
    assert "word-break: normal;" in content
    assert "overflow-wrap: normal;" in content
