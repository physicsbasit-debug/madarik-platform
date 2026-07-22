from pathlib import Path

from app.models.project import (
    QuestionItem,
    QuestionPatch,
)


ROOT = Path(__file__).resolve().parents[2]


def build_question() -> QuestionItem:
    return QuestionItem(
        id="q1",
        original_number="1",
        original_text="Explain wave diffraction.",
        translated_text="فسر حيود الموجات.",
        order_index=1,
    )


def test_question_curriculum_fields_default_safely() -> None:
    question = build_question()

    assert question.curriculum_grade is None
    assert question.curriculum_unit_id is None
    assert question.curriculum_learning_outcome_ids == []


def test_question_patch_accepts_curriculum_link() -> None:
    patch = QuestionPatch(
        curriculum_grade=10,
        curriculum_science_domain="physics",
        curriculum_semester_id="g10-sem2",
        curriculum_subject_id="g10-physics",
        curriculum_unit_id="g10-physics-sem2-waves",
        curriculum_lesson_id="g10-waves-properties",
        curriculum_learning_outcome_ids=[
            "g10-lo-waves-properties-1"
        ],
        curriculum_link_source="manual",
    )

    assert patch.curriculum_grade == 10
    assert patch.curriculum_science_domain == "physics"
    assert patch.curriculum_learning_outcome_ids == [
        "g10-lo-waves-properties-1"
    ]


def test_frontend_api_maps_curriculum_fields() -> None:
    content = (
        ROOT / "frontend/src/services/api.ts"
    ).read_text(encoding="utf-8")

    assert "curriculum_grade" in content
    assert "curriculum_learning_outcome_ids" in content
    assert "curriculumGrade" in content


def test_review_has_curriculum_link_card() -> None:
    content = (
        ROOT
        / "frontend/src/features/review/ReviewStep.tsx"
    ).read_text(encoding="utf-8")

    assert "QuestionCurriculumLinkCard" in content
    assert "ClassificationReviewSummary" in content
    assert "import type {\nimport" not in content


def test_curriculum_card_uses_repository_boundary() -> None:
    content = (
        ROOT
        / "frontend/src/features/review/QuestionCurriculumLinkCard.tsx"
    ).read_text(encoding="utf-8")

    assert "localCurriculumRepository" in content
    assert "science-curriculum.seed" not in content
    assert "نواتج التعلم" in content
    assert "فك الارتباط" in content


def test_review_summary_tracks_unclassified_and_unlinked() -> None:
    content = (
        ROOT
        / "frontend/src/features/review/ClassificationReviewSummary.tsx"
    ).read_text(encoding="utf-8")

    assert "غير مصنف" in content
    assert "غير مرتبط بالمنهج" in content
    assert "مكتمل التصنيف والربط" in content


def test_readme_tracks_phase_4b() -> None:
    content = (ROOT / "README.md").read_text(
        encoding="utf-8"
    )

    assert "Phase 4-B" in content
    assert "Curriculum Linking and Classification Review" in content
