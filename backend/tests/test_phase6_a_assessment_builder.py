from pathlib import Path
import pytest

from app.models.assessment import AssessmentBlueprint
from app.models.project import CognitiveCategory, ProjectSession, QuestionItem
from app.services.assessment_builder import AssessmentBlueprintError, build_assessment_detail
from app.services.assessment_repository import AssessmentRepository
from app.services.question_bank_repository import QuestionBankRepository

ROOT = Path(__file__).resolve().parents[2]

def build_question(question_id: str, *, marks: int, category: CognitiveCategory) -> QuestionItem:
    return QuestionItem(
        id=question_id,
        original_number=question_id,
        original_text=f"Question {question_id}",
        translated_text=f"السؤال {question_id}",
        marks=marks,
        order_index=1,
        cognitive_category=category,
        curriculum_grade=10,
        curriculum_science_domain="physics",
        curriculum_semester_id="g10-sem2",
        curriculum_subject_id="g10-physics",
        curriculum_unit_id="waves",
    )

def test_repository_persists_assessment_draft(tmp_path: Path) -> None:
    repository = AssessmentRepository(tmp_path / "assessment.db")
    draft = repository.create(
        blueprint=AssessmentBlueprint(),
        owner_account_id="owner-1",
        source_project_id="project-1",
    )
    loaded = repository.get(draft.id)
    assert loaded is not None
    assert loaded.blueprint.total_marks == 20
    assert loaded.owner_account_id == "owner-1"

def test_blueprint_requires_cognitive_total_100(tmp_path: Path) -> None:
    assessment_repository = AssessmentRepository(tmp_path / "assessment.db")
    bank_repository = QuestionBankRepository(tmp_path / "assessment.db")
    draft = assessment_repository.create(
        blueprint=AssessmentBlueprint(
            knowledge_percent=20,
            application_percent=20,
            reasoning_percent=20,
        ),
        owner_account_id=None,
        source_project_id=None,
    )
    with pytest.raises(AssessmentBlueprintError):
        build_assessment_detail(draft, bank_repository)

def test_builder_adds_bank_items_without_duplicates(tmp_path: Path) -> None:
    db_path = tmp_path / "assessment.db"
    assessment_repository = AssessmentRepository(db_path)
    bank_repository = QuestionBankRepository(db_path)
    project = ProjectSession(
        id="project-1",
        questions=[build_question("q1", marks=2, category=CognitiveCategory.application)],
    )
    bank_item = bank_repository.save_from_project_question(project, project.questions[0])
    draft = assessment_repository.create(
        blueprint=AssessmentBlueprint(),
        owner_account_id=None,
        source_project_id=project.id,
    )
    _, first_added = assessment_repository.add_bank_item(draft, bank_item)
    _, second_added = assessment_repository.add_bank_item(draft, bank_item)
    assert first_added is True
    assert second_added is False
    assert draft.question_bank_item_ids == [bank_item.id]

def test_balance_calculates_marks_and_categories(tmp_path: Path) -> None:
    db_path = tmp_path / "assessment.db"
    assessment_repository = AssessmentRepository(db_path)
    bank_repository = QuestionBankRepository(db_path)
    project = ProjectSession(
        id="project-1",
        questions=[
            build_question("q1", marks=2, category=CognitiveCategory.knowledge),
            build_question("q2", marks=3, category=CognitiveCategory.reasoning),
        ],
    )
    draft = assessment_repository.create(
        blueprint=AssessmentBlueprint(total_marks=10, target_question_count=4),
        owner_account_id=None,
        source_project_id=project.id,
    )
    for question in project.questions:
        item = bank_repository.save_from_project_question(project, question)
        assessment_repository.add_bank_item(draft, item)
    detail = build_assessment_detail(draft, bank_repository)
    assert detail.balance.selected_question_count == 2
    assert detail.balance.selected_marks == 5
    assert detail.balance.remaining_marks == 5
    assert detail.balance.knowledge_count == 1
    assert detail.balance.reasoning_count == 1

def test_assessment_api_routes_exist() -> None:
    content = (ROOT / "backend/app/api/projects.py").read_text(encoding="utf-8")
    assert "create_assessment_draft" in content
    assert "update_assessment_blueprint" in content
    assert "add_assessment_bank_item" in content
    assert "remove_assessment_bank_item" in content

def test_task_home_opens_assessment_builder() -> None:
    home = (ROOT / "frontend/src/features/workflow/ScienceTaskHome.tsx").read_text(encoding="utf-8")
    app = (ROOT / "frontend/src/app/App.tsx").read_text(encoding="utf-8")
    assert "onOpenAssessmentBuilder" in home
    assert "فتح منشئ الاختبارات" in home
    assert 'workspaceMode === "assessment"' in app
    assert "AssessmentBuilder" in app

def test_builder_workspace_has_blueprint_and_balance() -> None:
    content = (ROOT / "frontend/src/features/assessment/AssessmentBuilder.tsx").read_text(encoding="utf-8")
    assert "جدول المواصفات" in content
    assert "الدرجة الكلية" in content
    assert "المستهدف" in content
    assert "addAssessmentBankItem" in content
    assert "removeAssessmentBankItem" in content

def test_readme_tracks_phase_6a() -> None:
    content = (ROOT / "README.md").read_text(encoding="utf-8")
    assert "Phase 6-A" in content
    assert "Assessment Blueprint and Test Builder Foundation" in content
