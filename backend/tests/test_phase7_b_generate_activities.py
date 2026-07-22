from pathlib import Path

from app.models.differentiated_activity import (
    DifferentiatedActivityGenerationRequest,
    DifferentiationLevel,
)
from app.models.project import QuestionItem
from app.models.question_bank import QuestionBankItem
from app.services.differentiated_activity_generator import (
    generate_differentiated_activity_set,
)
from app.services.differentiated_activity_repository import (
    DifferentiatedActivityRepository,
)

ROOT = Path(__file__).resolve().parents[2]


def request() -> DifferentiatedActivityGenerationRequest:
    return DifferentiatedActivityGenerationRequest(
        title="نشاط الموجات",
        grade=10,
        science_domain="physics",
        subject_id="g10-physics",
        objective="تفسير خصائص الموجات.",
        core_task="قارن بين التردد والطول الموجي.",
        estimated_minutes=20,
    )


def bank_item() -> QuestionBankItem:
    question = QuestionItem(
        id="q1",
        original_number="1",
        original_text="Explain wave frequency.",
        translated_text="فسر تردد الموجة.",
        marks=2,
        order_index=1,
    )
    return QuestionBankItem(
        id="bank-1",
        source_project_id="source",
        source_question_id=question.id,
        content_fingerprint="fingerprint",
        question_snapshot=question,
    )


def test_generator_creates_three_levels(tmp_path: Path) -> None:
    repository = DifferentiatedActivityRepository(
        tmp_path / "db.sqlite"
    )
    result = generate_differentiated_activity_set(
        request(), repository, bank_item=bank_item()
    )
    assert result.total == 3
    assert {item.level for item in result.items} == {
        DifferentiationLevel.support,
        DifferentiationLevel.core,
        DifferentiationLevel.extension,
    }


def test_levels_have_distinct_instructions(tmp_path: Path) -> None:
    repository = DifferentiatedActivityRepository(
        tmp_path / "db.sqlite"
    )
    result = generate_differentiated_activity_set(
        request(), repository, bank_item=bank_item()
    )
    data = {item.level: item.instructions for item in result.items}
    assert "خطوة خطوة" in data[DifferentiationLevel.support]
    assert "المهمة الأساسية" in data[DifferentiationLevel.core]
    assert "استقلالية" in data[DifferentiationLevel.extension]


def test_question_context_is_included(tmp_path: Path) -> None:
    repository = DifferentiatedActivityRepository(
        tmp_path / "db.sqlite"
    )
    result = generate_differentiated_activity_set(
        request(), repository, bank_item=bank_item()
    )
    assert all("فسر تردد الموجة" in item.instructions for item in result.items)


def test_generated_set_is_persisted(tmp_path: Path) -> None:
    repository = DifferentiatedActivityRepository(
        tmp_path / "db.sqlite"
    )
    generate_differentiated_activity_set(request(), repository)
    assert len(repository.list()) == 3


def test_generation_api_exists() -> None:
    content = (ROOT / "backend/app/api/projects.py").read_text(encoding="utf-8")
    assert "generate_differentiated_activities" in content
    assert "differentiated-activities/generate" in content


def test_frontend_has_generation_controls() -> None:
    content = (
        ROOT
        / "frontend/src/features/activities/DifferentiatedActivities.tsx"
    ).read_text(encoding="utf-8")
    assert "توليد ثلاث نسخ" in content
    assert "دون سؤال مرجعي" in content
    assert "generateDifferentiatedActivities" in content


def test_readme_tracks_phase_7b() -> None:
    content = (ROOT / "README.md").read_text(encoding="utf-8")
    assert "Phase 7-B" in content
    assert "Generate Differentiated Activities from Curriculum and Questions" in content
