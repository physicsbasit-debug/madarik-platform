from __future__ import annotations

from app.models.assessment import (
    AssessmentBalanceSummary,
    AssessmentDraft,
    AssessmentDraftDetail,
    AssessmentQuestionSummary,
)
from app.models.project import CognitiveCategory
from app.services.question_bank_repository import QuestionBankRepository


class AssessmentBlueprintError(ValueError):
    pass


def validate_blueprint(draft: AssessmentDraft) -> None:
    if draft.blueprint.cognitive_percent_total() != 100:
        raise AssessmentBlueprintError(
            "يجب أن يكون مجموع نسب المستويات المعرفية 100%."
        )


def build_assessment_detail(
    draft: AssessmentDraft,
    question_bank_repository: QuestionBankRepository,
) -> AssessmentDraftDetail:
    validate_blueprint(draft)

    bank_items = []
    for item_id in draft.question_bank_item_ids:
        item = question_bank_repository.get(item_id)
        if item is not None:
            bank_items.append(item)

    questions = [
        AssessmentQuestionSummary(
            bank_item_id=item.id,
            question_number=(
                item.question_snapshot.original_number or "—"
            ),
            text=(
                item.question_snapshot.translated_text
                or item.question_snapshot.original_text
            ),
            marks=item.question_snapshot.marks or 0,
            cognitive_category=(
                item.question_snapshot.cognitive_category
            ),
            grade=item.question_snapshot.curriculum_grade,
            unit_id=item.question_snapshot.curriculum_unit_id,
        )
        for item in bank_items
    ]

    selected_count = len(questions)
    selected_marks = sum(question.marks for question in questions)
    counts = {
        CognitiveCategory.knowledge: 0,
        CognitiveCategory.application: 0,
        CognitiveCategory.reasoning: 0,
        CognitiveCategory.unclassified: 0,
    }
    for question in questions:
        counts[question.cognitive_category] += 1

    denominator = selected_count or 1
    balance = AssessmentBalanceSummary(
        selected_question_count=selected_count,
        selected_marks=selected_marks,
        remaining_question_count=max(
            draft.blueprint.target_question_count - selected_count,
            0,
        ),
        remaining_marks=max(
            draft.blueprint.total_marks - selected_marks,
            0,
        ),
        knowledge_count=counts[CognitiveCategory.knowledge],
        application_count=counts[CognitiveCategory.application],
        reasoning_count=counts[CognitiveCategory.reasoning],
        unclassified_count=counts[CognitiveCategory.unclassified],
        knowledge_percent=round(
            counts[CognitiveCategory.knowledge] / denominator * 100,
            1,
        ),
        application_percent=round(
            counts[CognitiveCategory.application] / denominator * 100,
            1,
        ),
        reasoning_percent=round(
            counts[CognitiveCategory.reasoning] / denominator * 100,
            1,
        ),
        question_target_met=(
            selected_count == draft.blueprint.target_question_count
        ),
        marks_target_met=(
            selected_marks == draft.blueprint.total_marks
        ),
        cognitive_targets_valid=(
            counts[CognitiveCategory.unclassified] == 0
        ),
    )
    return AssessmentDraftDetail(
        draft=draft,
        questions=questions,
        balance=balance,
    )
