from __future__ import annotations

from app.models.differentiated_activity import (
    DifferentiatedActivity,
    DifferentiatedActivityGenerationRequest,
    DifferentiatedActivityGenerationResponse,
    DifferentiationLevel,
)
from app.models.question_bank import QuestionBankItem
from app.services.differentiated_activity_repository import (
    DifferentiatedActivityRepository,
)


def _context(bank_item: QuestionBankItem | None) -> str:
    if bank_item is None:
        return ""
    q = bank_item.question_snapshot
    return (q.translated_text or q.original_text or "").strip()


def _build(
    payload: DifferentiatedActivityGenerationRequest,
    level: DifferentiationLevel,
    context: str,
    owner_account_id: str | None,
) -> DifferentiatedActivity:
    base = {
        "owner_account_id": owner_account_id,
        "source_project_id": payload.source_project_id,
        "grade": payload.grade,
        "science_domain": payload.science_domain,
        "subject_id": payload.subject_id,
        "semester_id": payload.semester_id,
        "unit_id": payload.unit_id,
        "lesson_id": payload.lesson_id,
        "learning_outcome_ids": payload.learning_outcome_ids,
        "level": level,
        "objective": payload.objective,
        "materials": payload.materials,
    }

    if level is DifferentiationLevel.support:
        title = f"{payload.title} - دعم"
        instructions = (
            "نفذ المهمة خطوة خطوة بمساندة المعلم أو زميل. "
            f"المهمة الأساسية: {payload.core_task}"
        )
        criteria = [
            "يحدد الفكرة العلمية الرئيسة.",
            "ينفذ الخطوات بالترتيب.",
            "يشرح النتيجة بجملة علمية صحيحة.",
        ]
        minutes = payload.estimated_minutes + 10
    elif level is DifferentiationLevel.extension:
        title = f"{payload.title} - إثراء"
        instructions = (
            "نفذ المهمة باستقلالية ثم أضف تفسيرًا أو تطبيقًا جديدًا. "
            f"المهمة الأساسية: {payload.core_task}"
        )
        criteria = [
            "يقدم تفسيرًا علميًا مترابطًا.",
            "يربط الفكرة بتطبيق جديد.",
            "يبرر النتيجة بالأدلة أو الحسابات.",
        ]
        minutes = payload.estimated_minutes + 5
    else:
        title = f"{payload.title} - أساسي"
        instructions = (
            "نفذ المهمة مستخدمًا المفاهيم العلمية المناسبة، "
            f"وسجل خطوات الحل. المهمة الأساسية: {payload.core_task}"
        )
        criteria = [
            "يطبق المفهوم العلمي بصورة صحيحة.",
            "يعرض خطواته بوضوح.",
            "يتحقق من صحة النتيجة.",
        ]
        minutes = payload.estimated_minutes

    if context:
        instructions += f" السؤال المرجعي: {context}"

    return DifferentiatedActivity(
        **base,
        title=title,
        instructions=instructions,
        success_criteria=criteria,
        estimated_minutes=minutes,
    )


def generate_differentiated_activity_set(
    payload: DifferentiatedActivityGenerationRequest,
    repository: DifferentiatedActivityRepository,
    owner_account_id: str | None = None,
    bank_item: QuestionBankItem | None = None,
) -> DifferentiatedActivityGenerationResponse:
    context = _context(bank_item)
    items = [
        _build(payload, level, context, owner_account_id)
        for level in (
            DifferentiationLevel.support,
            DifferentiationLevel.core,
            DifferentiationLevel.extension,
        )
    ]
    saved = [repository.save(item) for item in items]
    return DifferentiatedActivityGenerationResponse(
        items=saved,
        total=len(saved),
        source_question_bank_item_id=payload.source_question_bank_item_id,
    )
