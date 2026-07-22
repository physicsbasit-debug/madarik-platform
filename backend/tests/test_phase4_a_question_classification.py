from pathlib import Path

from app.models.project import (
    CognitiveCategory,
    QuestionItem,
    QuestionPatch,
)


ROOT = Path(__file__).resolve().parents[2]


def test_question_defaults_to_unclassified() -> None:
    item = QuestionItem(
        id="q1",
        original_number="1",
        original_text="State the unit of force.",
        translated_text="اذكر وحدة القوة.",
        order_index=1,
    )
    assert (
        item.cognitive_category
        is CognitiveCategory.unclassified
    )
    assert item.classification_confidence == 0.0


def test_question_patch_accepts_classification() -> None:
    patch = QuestionPatch(
        cognitive_category=CognitiveCategory.reasoning,
        classification_confidence=0.8,
        classification_reason="سبب",
        classification_source="automatic_rule",
    )
    assert (
        patch.cognitive_category
        is CognitiveCategory.reasoning
    )
    assert patch.classification_confidence == 0.8


def test_classifier_contains_all_categories() -> None:
    content = (
        ROOT
        / "frontend/src/features/review/question-classifier.ts"
    ).read_text(encoding="utf-8")
    for value in (
        "knowledge",
        "application",
        "reasoning",
        "unclassified",
    ):
        assert value in content


def test_classifier_has_arabic_cues() -> None:
    content = (
        ROOT
        / "frontend/src/features/review/question-classifier.ts"
    ).read_text(encoding="utf-8")
    assert "اذكر" in content
    assert "احسب" in content
    assert "فسر" in content
    assert "قارن" in content


def test_review_uses_classification_card() -> None:
    content = (
        ROOT
        / "frontend/src/features/review/ReviewStep.tsx"
    ).read_text(encoding="utf-8")
    assert "QuestionClassificationCard" in content
    assert "selectedQuestion" in content
    assert "onUpdateQuestion={onUpdateQuestion}" in content


def test_api_maps_classification_fields() -> None:
    content = (
        ROOT / "frontend/src/services/api.ts"
    ).read_text(encoding="utf-8")
    assert "cognitive_category" in content
    assert "classification_confidence" in content
    assert "cognitiveCategory" in content


def test_readme_tracks_phase_4a() -> None:
    content = (ROOT / "README.md").read_text(
        encoding="utf-8"
    )
    assert "Phase 4-A" in content
    assert "Science Question Classification Foundation" in content
