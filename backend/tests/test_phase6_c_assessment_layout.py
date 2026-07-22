from pathlib import Path

from app.models.assessment import (
    AssessmentDraft,
    AssessmentItemConfiguration,
    AssessmentLayoutUpdate,
    AssessmentSection,
)
from app.models.project import QuestionItem
from app.models.question_bank import QuestionBankItem
from app.services.assessment_builder import (
    build_assessment_detail,
)
from app.services.assessment_repository import (
    AssessmentRepository,
)
from app.services.question_bank_repository import (
    QuestionBankRepository,
)


ROOT = Path(__file__).resolve().parents[2]


def add_bank_item(
    repository: QuestionBankRepository,
    item_id: str,
    marks: int,
) -> QuestionBankItem:
    item = QuestionBankItem(
        id=item_id,
        source_project_id="source",
        source_question_id=f"q-{item_id}",
        content_fingerprint=item_id,
        question_snapshot=QuestionItem(
            id=f"q-{item_id}",
            original_number=item_id,
            original_text=item_id,
            translated_text=item_id,
            marks=marks,
            order_index=1,
        ),
    )
    with repository._connect() as connection:
        connection.execute(
            """
            INSERT INTO question_bank (
                id,
                source_project_id,
                source_question_id,
                owner_account_id,
                content_fingerprint,
                updated_at,
                payload
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                item.id,
                item.source_project_id,
                item.source_question_id,
                None,
                item.content_fingerprint,
                item.updated_at.isoformat(),
                item.model_dump_json(),
            ),
        )
    return item


def test_layout_persists_sections_order_and_marks(
    tmp_path: Path,
) -> None:
    assessment_repository = AssessmentRepository(
        tmp_path / "db.sqlite"
    )
    bank_repository = QuestionBankRepository(
        tmp_path / "db.sqlite"
    )
    add_bank_item(bank_repository, "one", 2)
    add_bank_item(bank_repository, "two", 3)

    draft = AssessmentDraft(
        question_bank_item_ids=["one", "two"]
    )
    assessment_repository.save(draft)

    first_section = AssessmentSection(
        id="s1",
        title="القسم الأول",
        order_index=1,
    )
    second_section = AssessmentSection(
        id="s2",
        title="القسم الثاني",
        order_index=2,
    )
    assessment_repository.update_layout(
        draft,
        AssessmentLayoutUpdate(
            sections=[
                first_section,
                second_section,
            ],
            item_configurations=[
                AssessmentItemConfiguration(
                    bank_item_id="two",
                    section_id="s2",
                    order_index=1,
                    marks_override=5,
                ),
                AssessmentItemConfiguration(
                    bank_item_id="one",
                    section_id="s1",
                    order_index=2,
                ),
            ],
        ),
    )

    detail = build_assessment_detail(
        draft,
        bank_repository,
    )

    assert detail.questions[0].bank_item_id == "two"
    assert detail.questions[0].marks == 5
    assert detail.questions[0].source_marks == 3
    assert detail.questions[0].section_id == "s2"
    assert detail.balance.selected_marks == 7


def test_layout_ignores_unknown_items(
    tmp_path: Path,
) -> None:
    repository = AssessmentRepository(
        tmp_path / "db.sqlite"
    )
    draft = AssessmentDraft(
        question_bank_item_ids=["known"]
    )

    repository.update_layout(
        draft,
        AssessmentLayoutUpdate(
            item_configurations=[
                AssessmentItemConfiguration(
                    bank_item_id="unknown",
                    order_index=1,
                )
            ]
        ),
    )

    assert [
        item.bank_item_id
        for item in draft.item_configurations
    ] == ["known"]


def test_old_draft_has_default_section() -> None:
    draft = AssessmentDraft()
    assert len(draft.sections) == 1
    assert draft.sections[0].title == "القسم الأول"


def test_layout_api_exists() -> None:
    content = (
        ROOT / "backend/app/api/projects.py"
    ).read_text(encoding="utf-8")
    assert "update_assessment_layout" in content
    assert "/layout" in content


def test_frontend_has_section_order_mark_controls() -> None:
    content = (
        ROOT
        / "frontend/src/features/assessment/AssessmentBuilder.tsx"
    ).read_text(encoding="utf-8")
    assert "إضافة قسم" in content
    assert "تحريك السؤال للأعلى" in content
    assert "marksOverride" in content
    assert "updateAssessmentLayout" in content


def test_readme_describes_new_program_nature() -> None:
    content = (ROOT / "README.md").read_text(
        encoding="utf-8"
    )
    assert "ما هي منصة مدارك؟" in content
    assert "منظومة إدارة محتوى وتقويم علمي" in content
    assert "Phase 6-C" in content
