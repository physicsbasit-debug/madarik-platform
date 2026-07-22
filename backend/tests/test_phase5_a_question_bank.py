from pathlib import Path

from app.models.project import (
    CognitiveCategory,
    ProjectSession,
    QuestionItem,
)
from app.services.question_bank_repository import (
    QuestionBankRepository,
    build_question_fingerprint,
)


ROOT = Path(__file__).resolve().parents[2]


def build_question(
    translated_text: str = "احسب سرعة الموجة.",
) -> QuestionItem:
    return QuestionItem(
        id="question-1",
        original_number="1",
        original_text="Calculate wave speed.",
        translated_text=translated_text,
        marks=2,
        order_index=1,
        cognitive_category=(
            CognitiveCategory.application
        ),
        curriculum_grade=10,
        curriculum_science_domain="physics",
        curriculum_semester_id="g10-sem2",
        curriculum_subject_id="g10-physics",
        curriculum_unit_id=(
            "g10-physics-sem2-waves"
        ),
        curriculum_lesson_id=(
            "g10-waves-properties"
        ),
        curriculum_learning_outcome_ids=[
            "g10-lo-waves-properties-1"
        ],
    )


def build_project() -> ProjectSession:
    return ProjectSession(
        id="project-1",
        questions=[build_question()],
    )


def test_fingerprint_changes_with_content() -> None:
    first = build_question_fingerprint(
        build_question("احسب سرعة الموجة.")
    )
    second = build_question_fingerprint(
        build_question("فسر سرعة الموجة.")
    )

    assert first != second


def test_repository_saves_question_snapshot(
    tmp_path: Path,
) -> None:
    repository = QuestionBankRepository(
        tmp_path / "question-bank.db"
    )
    project = build_project()
    question = project.questions[0]

    item = repository.save_from_project_question(
        project,
        question,
    )

    assert item.source_project_id == project.id
    assert item.source_question_id == question.id
    assert (
        item.question_snapshot.cognitive_category
        is CognitiveCategory.application
    )
    assert (
        item.question_snapshot.curriculum_grade
        == 10
    )


def test_saving_same_question_updates_not_duplicates(
    tmp_path: Path,
) -> None:
    repository = QuestionBankRepository(
        tmp_path / "question-bank.db"
    )
    project = build_project()

    first = repository.save_from_project_question(
        project,
        project.questions[0],
    )
    project.questions[0].translated_text = (
        "احسب السرعة الجديدة."
    )
    second = repository.save_from_project_question(
        project,
        project.questions[0],
    )

    items = repository.list_for_project(project.id)

    assert first.id == second.id
    assert len(items) == 1
    assert (
        items[0].question_snapshot.translated_text
        == "احسب السرعة الجديدة."
    )


def test_repository_deletes_bank_item_only(
    tmp_path: Path,
) -> None:
    repository = QuestionBankRepository(
        tmp_path / "question-bank.db"
    )
    project = build_project()
    item = repository.save_from_project_question(
        project,
        project.questions[0],
    )

    removed = repository.delete(
        project.id,
        item.id,
    )

    assert removed is not None
    assert repository.list_for_project(
        project.id
    ) == []
    assert len(project.questions) == 1


def test_question_bank_api_routes_exist() -> None:
    content = (
        ROOT / "backend/app/api/projects.py"
    ).read_text(encoding="utf-8")

    assert "list_project_question_bank" in content
    assert "save_question_to_bank" in content
    assert "delete_question_bank_item" in content


def test_review_has_question_bank_panel() -> None:
    content = (
        ROOT
        / "frontend/src/features/review/ReviewStep.tsx"
    ).read_text(encoding="utf-8")

    assert "QuestionBankPanel" in content
    assert "projectId={projectId}" in content
    assert (
        "activeQuestions.find(\n"
        "        (question) => "
        "!(question.linkedLayoutAssetIds"
    ) in content
    assert (
        "<ClassificationReviewSummary "
        "questions={questions} />"
    ) in content


def test_readme_tracks_phase_5a() -> None:
    content = (
        ROOT / "README.md"
    ).read_text(encoding="utf-8")

    assert "Phase 5-A" in content
    assert (
        "Question Bank Data Model and Persistence"
        in content
    )
