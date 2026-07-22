from pathlib import Path

from app.models.project import (
    ProjectSession,
    QuestionAssetInfo,
    QuestionItem,
    QuestionPart,
    QuestionStatus,
)
from app.models.question_bank import QuestionBankItem
from app.services.question_bank_reuse import (
    reuse_question_bank_item,
)


ROOT = Path(__file__).resolve().parents[2]


def build_bank_item() -> QuestionBankItem:
    question = QuestionItem(
        id="source-question",
        original_number="7",
        original_text="Explain diffraction.",
        translated_text="فسر الحيود.",
        marks=2,
        order_index=3,
        linked_layout_asset_ids=["layout-1"],
        source_page_numbers=[2],
        source_page_start=2,
        source_page_end=2,
        attachments=[
            QuestionAssetInfo(
                id="attachment-1",
                name="figure.png",
                size=10,
                type="image/png",
                data_base64="abc",
            )
        ],
        parts=[
            QuestionPart(
                id="part-1",
                label="a",
                original_text="Part A",
                translated_text="الجزء أ",
                marks=1,
                order_index=1,
            )
        ],
        curriculum_grade=10,
        curriculum_subject_id="g10-physics",
        curriculum_unit_id="waves",
    )
    return QuestionBankItem(
        id="bank-item-1",
        source_project_id="source-project",
        source_question_id=question.id,
        content_fingerprint="fingerprint",
        question_snapshot=question,
    )


def test_reuse_creates_independent_question() -> None:
    project = ProjectSession(id="target-project")
    bank_item = build_bank_item()

    reused, created = reuse_question_bank_item(
        project,
        bank_item,
    )

    assert created is True
    assert reused.id != bank_item.question_snapshot.id
    assert reused.status is QuestionStatus.needs_review
    assert reused.order_index == 1
    assert (
        reused.reused_from_question_bank_item_id
        == bank_item.id
    )
    assert reused.curriculum_grade == 10


def test_reuse_regenerates_nested_ids() -> None:
    project = ProjectSession(id="target-project")
    bank_item = build_bank_item()

    reused, _ = reuse_question_bank_item(
        project,
        bank_item,
    )

    assert (
        reused.attachments[0].id
        != bank_item.question_snapshot
        .attachments[0].id
    )
    assert (
        reused.parts[0].id
        != bank_item.question_snapshot.parts[0].id
    )


def test_reuse_clears_source_project_links() -> None:
    project = ProjectSession(id="target-project")
    reused, _ = reuse_question_bank_item(
        project,
        build_bank_item(),
    )

    assert reused.linked_layout_asset_ids == []
    assert reused.source_page_numbers == []
    assert reused.source_page_start is None
    assert reused.source_page_end is None


def test_reuse_same_item_is_idempotent() -> None:
    project = ProjectSession(id="target-project")
    bank_item = build_bank_item()

    first, first_created = reuse_question_bank_item(
        project,
        bank_item,
    )
    second, second_created = reuse_question_bank_item(
        project,
        bank_item,
    )

    assert first_created is True
    assert second_created is False
    assert first.id == second.id
    assert len(project.questions) == 1


def test_reuse_api_route_exists() -> None:
    content = (
        ROOT / "backend/app/api/projects.py"
    ).read_text(encoding="utf-8")

    assert "reuse_question_bank_library_item" in content
    assert "reuse/{target_project_id}" in content
    assert "project_store.touch(target_project_id)" in content


def test_library_has_reuse_control() -> None:
    content = (
        ROOT
        / "frontend/src/features/question-bank/QuestionBankLibrary.tsx"
    ).read_text(encoding="utf-8")

    assert "reuseQuestionBankItemInProject" in content
    assert "إضافة إلى المشروع الحالي" in content
    assert "onQuestionReused" in content


def test_readme_tracks_phase_5c() -> None:
    content = (
        ROOT / "README.md"
    ).read_text(encoding="utf-8")

    assert "Phase 5-C" in content
    assert (
        "Reuse Question Bank Items in Projects"
        in content
    )
