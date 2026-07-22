from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_export_stage_uses_single_title() -> None:
    steps = (ROOT / "frontend/src/constants/steps.ts").read_text(encoding="utf-8")
    export_step = (ROOT / "frontend/src/features/export/ExportStep.tsx").read_text(encoding="utf-8")

    assert "label: 'التصدير والجاهزية'" in steps
    assert "<h2>التصدير والجاهزية</h2>" not in export_step
    assert 'className="export-control-bar"' in export_step


def test_export_choices_use_two_row_layout() -> None:
    content = (ROOT / "frontend/src/features/export/ExportStep.tsx").read_text(encoding="utf-8")
    styles = (ROOT / "frontend/src/styles/global.css").read_text(encoding="utf-8")

    assert "export-mode-card" in content
    assert "export-formats-card" in content
    assert "export-choice-wide" in content
    assert ".export-choice-grid" in styles
    assert "grid-template-columns: repeat(2, minmax(0, 1fr));" in styles


def test_marks_mismatch_is_horizontal_decision_bar() -> None:
    content = (ROOT / "frontend/src/features/export/ExportStep.tsx").read_text(encoding="utf-8")

    assert "marks-decision-bar" in content
    assert "اعتماد مجموع الأسئلة" in content
    assert "تحويل الدرجة إلى" in content
    assert "<select" not in content[content.index("marks-decision-bar"):content.index("export-blockers-panel")]


def test_export_preview_has_visual_paper_thumbnail() -> None:
    content = (ROOT / "frontend/src/features/export/ExportStep.tsx").read_text(encoding="utf-8")
    styles = (ROOT / "frontend/src/styles/global.css").read_text(encoding="utf-8")

    assert "export-paper-thumbnail" in content
    assert "export-paper-brand" in content
    assert ".export-paper-thumbnail" in styles


def test_primary_export_and_review_translate_actions_are_compact() -> None:
    review = (ROOT / "frontend/src/features/review/ReviewStep.tsx").read_text(encoding="utf-8")
    styles = (ROOT / "frontend/src/styles/global.css").read_text(encoding="utf-8")

    assert "review-translate-action" in review
    assert ".export-main-button" in styles
    assert "min-width: 19rem;" in styles
    assert ".review-translate-action" in styles
