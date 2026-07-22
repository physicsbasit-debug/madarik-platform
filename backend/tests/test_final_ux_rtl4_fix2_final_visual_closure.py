from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def test_review_translation_action_is_inside_bulk_actions() -> None:
    content = (
        ROOT / "frontend/src/features/review/ReviewStep.tsx"
    ).read_text(encoding="utf-8")

    bulk_index = content.index('className="review-bulk-actions"')
    translate_index = content.index(
        'className="primary-button compact review-translate-action"'
    )
    assert translate_index > bulk_index
    assert 'section-heading split-heading' in content


def test_final_stage_does_not_render_next_navigation_button() -> None:
    content = (
        ROOT / "frontend/src/app/App.tsx"
    ).read_text(encoding="utf-8")

    assert "activeIndex < steps.length - 1" in content
    assert "activeIndex === steps.length - 1 ||" not in content


def test_identity_is_part_of_export_preview_row() -> None:
    content = (
        ROOT / "frontend/src/features/export/ExportStep.tsx"
    ).read_text(encoding="utf-8")

    preview_index = content.index('className="export-preview-grid"')
    identity_index = content.index(
        "export-choice-card export-identity-card export-preview-identity"
    )
    ready_index = content.index("export-ready-card")
    assert preview_index < identity_index < ready_index


def test_export_options_have_stronger_card_styles() -> None:
    content = (
        ROOT / "frontend/src/styles/global.css"
    ).read_text(encoding="utf-8")

    assert ".export-radio-card::before" in content
    assert ".export-format-option::before" in content
    assert ".export-preview-identity" in content
    assert "minmax(13rem, 0.5fr)" in content


def test_disabled_navigation_is_visually_inactive() -> None:
    content = (
        ROOT / "frontend/src/styles/global.css"
    ).read_text(encoding="utf-8")

    assert ".workspace-stage-actions .secondary-button:disabled" in content
    assert "cursor: not-allowed" in content
