from pathlib import Path

from app.models.project import (
    CognitiveCategory,
    ProjectSession,
    QuestionItem,
)
from app.services.question_bank_repository import (
    QuestionBankRepository,
)


ROOT = Path(__file__).resolve().parents[2]


def build_question(
    *,
    question_id: str,
    text: str,
    grade: int,
    category: CognitiveCategory,
    unit_id: str,
) -> QuestionItem:
    return QuestionItem(
        id=question_id,
        original_number=question_id,
        original_text=text,
        translated_text=text,
        marks=2,
        order_index=1,
        cognitive_category=category,
        curriculum_grade=grade,
        curriculum_science_domain="physics",
        curriculum_semester_id="g10-sem2",
        curriculum_subject_id="g10-physics",
        curriculum_unit_id=unit_id,
    )


def test_repository_searches_text_and_filters(
    tmp_path: Path,
) -> None:
    repository = QuestionBankRepository(
        tmp_path / "bank.db"
    )

    first_project = ProjectSession(
        id="p1",
        questions=[
            build_question(
                question_id="q1",
                text="احسب سرعة الموجة",
                grade=10,
                category=(
                    CognitiveCategory.application
                ),
                unit_id="waves",
            )
        ],
    )
    second_project = ProjectSession(
        id="p2",
        questions=[
            build_question(
                question_id="q2",
                text="فسر الانعكاس",
                grade=9,
                category=(
                    CognitiveCategory.reasoning
                ),
                unit_id="light",
            )
        ],
    )

    repository.save_from_project_question(
        first_project,
        first_project.questions[0],
    )
    repository.save_from_project_question(
        second_project,
        second_project.questions[0],
    )

    results = repository.search(
        query="سرعة",
        grade=10,
        cognitive_category="application",
    )

    assert len(results) == 1
    assert (
        results[0].source_question_id
        == "q1"
    )


def test_repository_filters_unit(
    tmp_path: Path,
) -> None:
    repository = QuestionBankRepository(
        tmp_path / "bank.db"
    )
    project = ProjectSession(
        id="p1",
        questions=[
            build_question(
                question_id="q1",
                text="موجات",
                grade=10,
                category=(
                    CognitiveCategory.knowledge
                ),
                unit_id="waves",
            ),
            build_question(
                question_id="q2",
                text="ضوء",
                grade=10,
                category=(
                    CognitiveCategory.knowledge
                ),
                unit_id="light",
            ),
        ],
    )

    for question in project.questions:
        repository.save_from_project_question(
            project,
            question,
        )

    results = repository.search(
        unit_id="light"
    )

    assert len(results) == 1
    assert (
        results[0].source_question_id
        == "q2"
    )


def test_repository_gets_single_item(
    tmp_path: Path,
) -> None:
    repository = QuestionBankRepository(
        tmp_path / "bank.db"
    )
    project = ProjectSession(
        id="p1",
        questions=[
            build_question(
                question_id="q1",
                text="سؤال",
                grade=10,
                category=(
                    CognitiveCategory.knowledge
                ),
                unit_id="waves",
            )
        ],
    )
    saved = repository.save_from_project_question(
        project,
        project.questions[0],
    )

    loaded = repository.get(saved.id)

    assert loaded is not None
    assert loaded.id == saved.id


def test_library_api_routes_exist() -> None:
    content = (
        ROOT / "backend/app/api/projects.py"
    ).read_text(encoding="utf-8")

    assert "search_question_bank_library" in content
    assert "get_question_bank_library_item" in content
    assert "question-bank/library" in content


def test_library_workspace_exists() -> None:
    content = (
        ROOT
        / "frontend/src/features/question-bank/QuestionBankLibrary.tsx"
    ).read_text(encoding="utf-8")

    assert "مكتبة بنك الأسئلة" in content
    assert "searchQuestionBankLibrary" in content
    assert "كل التصنيفات" in content
    assert "كل الصفوف" in content


def test_task_home_opens_question_bank() -> None:
    home = (
        ROOT
        / "frontend/src/features/workflow/ScienceTaskHome.tsx"
    ).read_text(encoding="utf-8")
    app = (
        ROOT / "frontend/src/app/App.tsx"
    ).read_text(encoding="utf-8")

    assert "onOpenQuestionBank" in home
    assert "فتح البنك" in home
    assert 'workspaceMode === "question-bank"' in app
    assert "QuestionBankLibrary" in app


def test_readme_tracks_phase_5b() -> None:
    content = (
        ROOT / "README.md"
    ).read_text(encoding="utf-8")

    assert "Phase 5-B" in content
    assert (
        "Question Bank Library, Search, and Filters"
        in content
    )
