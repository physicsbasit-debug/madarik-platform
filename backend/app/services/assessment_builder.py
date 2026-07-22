from __future__ import annotations

from app.models.assessment import (
    AssessmentAutoSelectionResponse,
    AssessmentBlueprintValidation,
    AssessmentBalanceSummary,
    AssessmentDraft,
    AssessmentDraftDetail,
    AssessmentItemConfiguration,
    AssessmentQuestionSummary,
)
from app.models.project import CognitiveCategory
from app.models.question_bank import QuestionBankItem
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

    config_by_id = {
        config.bank_item_id: config
        for config in draft.item_configurations
    }
    ordered_ids = sorted(
        draft.question_bank_item_ids,
        key=lambda item_id: (
            config_by_id.get(
                item_id,
                AssessmentItemConfiguration(
                    bank_item_id=item_id,
                    order_index=10_000,
                ),
            ).order_index
        ),
    )

    bank_items = []
    for item_id in ordered_ids:
        item = question_bank_repository.get(item_id)
        if item is not None:
            bank_items.append(item)

    questions = []
    for default_index, item in enumerate(
        bank_items,
        start=1,
    ):
        config = config_by_id.get(
            item.id,
            AssessmentItemConfiguration(
                bank_item_id=item.id,
                order_index=default_index,
            ),
        )
        source_marks = item.question_snapshot.marks or 0
        effective_marks = (
            config.marks_override
            if config.marks_override is not None
            else source_marks
        )
        questions.append(
            AssessmentQuestionSummary(
                bank_item_id=item.id,
                question_number=(
                    item.question_snapshot.original_number or "—"
                ),
                text=(
                    item.question_snapshot.translated_text
                    or item.question_snapshot.original_text
                ),
                marks=effective_marks,
                source_marks=source_marks,
                marks_override=config.marks_override,
                section_id=config.section_id,
                order_index=config.order_index,
                cognitive_category=(
                    item.question_snapshot.cognitive_category
                ),
                grade=item.question_snapshot.curriculum_grade,
                unit_id=item.question_snapshot.curriculum_unit_id,
            )
        )

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



def _target_count(total_questions: int, percent: int) -> int:
    return round(total_questions * percent / 100)


def validate_assessment_blueprint(
    draft: AssessmentDraft,
    question_bank_repository: QuestionBankRepository,
) -> AssessmentBlueprintValidation:
    detail = build_assessment_detail(draft, question_bank_repository)
    balance = detail.balance
    targets = {
        CognitiveCategory.knowledge: _target_count(
            draft.blueprint.target_question_count,
            draft.blueprint.knowledge_percent,
        ),
        CognitiveCategory.application: _target_count(
            draft.blueprint.target_question_count,
            draft.blueprint.application_percent,
        ),
        CognitiveCategory.reasoning: _target_count(
            draft.blueprint.target_question_count,
            draft.blueprint.reasoning_percent,
        ),
    }
    issues: list[str] = []
    if balance.selected_question_count != draft.blueprint.target_question_count:
        issues.append('عدد الأسئلة المختارة لا يطابق العدد المستهدف.')
    if balance.selected_marks != draft.blueprint.total_marks:
        issues.append('مجموع درجات الأسئلة لا يطابق الدرجة الكلية.')
    if balance.knowledge_count != targets[CognitiveCategory.knowledge]:
        issues.append('توزيع المعرفة لا يطابق جدول المواصفات.')
    if balance.application_count != targets[CognitiveCategory.application]:
        issues.append('توزيع التطبيق لا يطابق جدول المواصفات.')
    if balance.reasoning_count != targets[CognitiveCategory.reasoning]:
        issues.append('توزيع الاستدلال لا يطابق جدول المواصفات.')
    if balance.unclassified_count:
        issues.append('توجد أسئلة غير مصنفة معرفيًا داخل المسودة.')
    return AssessmentBlueprintValidation(
        ready=not issues,
        total_selected_questions=balance.selected_question_count,
        target_questions=draft.blueprint.target_question_count,
        total_selected_marks=balance.selected_marks,
        target_marks=draft.blueprint.total_marks,
        knowledge_selected=balance.knowledge_count,
        knowledge_target=targets[CognitiveCategory.knowledge],
        application_selected=balance.application_count,
        application_target=targets[CognitiveCategory.application],
        reasoning_selected=balance.reasoning_count,
        reasoning_target=targets[CognitiveCategory.reasoning],
        unclassified_selected=balance.unclassified_count,
        issues=issues,
    )


def auto_select_questions_for_assessment(
    draft: AssessmentDraft,
    bank_items: list[QuestionBankItem],
    question_bank_repository: QuestionBankRepository,
) -> AssessmentAutoSelectionResponse:
    compatible = [
        item for item in bank_items
        if item.question_snapshot.curriculum_grade == draft.blueprint.grade
        and (not draft.blueprint.science_domain or item.question_snapshot.curriculum_science_domain == draft.blueprint.science_domain)
        and (not draft.blueprint.unit_id or item.question_snapshot.curriculum_unit_id == draft.blueprint.unit_id)
    ]
    targets = {
        CognitiveCategory.knowledge: _target_count(draft.blueprint.target_question_count, draft.blueprint.knowledge_percent),
        CognitiveCategory.application: _target_count(draft.blueprint.target_question_count, draft.blueprint.application_percent),
        CognitiveCategory.reasoning: _target_count(draft.blueprint.target_question_count, draft.blueprint.reasoning_percent),
    }
    grouped = {category: [] for category in targets}
    skipped: list[str] = []
    for item in compatible:
        category = item.question_snapshot.cognitive_category
        if category in grouped:
            grouped[category].append(item)
        else:
            skipped.append(item.id)
    selected: list[QuestionBankItem] = []
    shortages: list[str] = []
    labels = {CognitiveCategory.knowledge:'المعرفة', CognitiveCategory.application:'التطبيق', CognitiveCategory.reasoning:'الاستدلال'}
    for category, needed in targets.items():
        candidates = sorted(grouped[category], key=lambda item: (item.question_snapshot.marks, item.updated_at))
        chosen = candidates[:needed]
        selected.extend(chosen)
        if len(chosen) < needed:
            shortages.append(f'نقص في أسئلة {labels[category]}: المتاح {len(chosen)} والمطلوب {needed}.')
    selected_ids={item.id for item in selected}
    remaining=draft.blueprint.target_question_count-len(selected)
    if remaining>0:
        extras=sorted([item for item in compatible if item.id not in selected_ids and item.question_snapshot.cognitive_category in grouped], key=lambda item:(item.question_snapshot.marks,item.updated_at))
        selected.extend(extras[:remaining])
    draft.question_bank_item_ids=[item.id for item in selected]
    detail=build_assessment_detail(draft, question_bank_repository)
    validation=validate_assessment_blueprint(draft, question_bank_repository)
    return AssessmentAutoSelectionResponse(
        detail=detail,
        validation=validation,
        selected_item_ids=[item.id for item in selected],
        skipped_item_ids=skipped,
        shortages=shortages,
    )
