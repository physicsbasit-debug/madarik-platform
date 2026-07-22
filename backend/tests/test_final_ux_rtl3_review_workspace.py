from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def read(relative_path: str) -> str:
    return (ROOT / relative_path).read_text(encoding="utf-8")


def test_review_workspace_uses_three_rtl_columns() -> None:
    review = read("frontend/src/features/review/ReviewStep.tsx")
    assert 'className="rtl-review-workspace"' in review
    assert 'className="rtl-review-question-list"' in review
    assert 'className="rtl-review-question-main"' in review
    assert 'className="rtl-review-visual-panel"' in review


def test_review_workspace_focuses_one_selected_question() -> None:
    review = read("frontend/src/features/review/ReviewStep.tsx")
    assert "selectedQuestionId" in review
    assert "questionsForDisplay" in review
    assert "setSelectedQuestionId(question.id)" in review


def test_review_visual_panel_preserves_crop_and_unlink_actions() -> None:
    review = read("frontend/src/features/review/ReviewStep.tsx")
    assert "setCropTarget" in review
    assert "onUnlinkLayoutAsset(selectedQuestion.id, asset.id)" in review


def test_review_workspace_has_responsive_css() -> None:
    css = read("frontend/src/styles/global.css")
    assert ".rtl-review-workspace" in css
    assert "grid-template-columns" in css
    assert "@media (max-width: 780px)" in css
