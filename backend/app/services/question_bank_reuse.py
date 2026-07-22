from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

from app.models.project import (
    ProjectSession,
    QuestionAssetInfo,
    QuestionItem,
    QuestionPart,
    QuestionStatus,
)
from app.models.question_bank import QuestionBankItem


class QuestionBankReuseError(ValueError):
    pass


def _clone_attachments(
    question: QuestionItem,
) -> list[QuestionAssetInfo]:
    return [
        attachment.model_copy(
            update={"id": str(uuid4())},
            deep=True,
        )
        for attachment in question.attachments
    ]


def _clone_parts(
    question: QuestionItem,
) -> list[QuestionPart]:
    id_map = {
        part.id: str(uuid4())
        for part in question.parts
    }

    return [
        part.model_copy(
            update={
                "id": id_map[part.id],
                "parent_id": (
                    id_map.get(part.parent_id)
                    if part.parent_id
                    else None
                ),
            },
            deep=True,
        )
        for part in question.parts
    ]


def reuse_question_bank_item(
    target_project: ProjectSession,
    bank_item: QuestionBankItem,
) -> tuple[QuestionItem, bool]:
    existing = next(
        (
            question
            for question in target_project.questions
            if (
                question
                .reused_from_question_bank_item_id
                == bank_item.id
            )
        ),
        None,
    )
    if existing is not None:
        return existing, False

    snapshot = bank_item.question_snapshot
    next_order = (
        max(
            (
                question.order_index
                for question in target_project.questions
            ),
            default=0,
        )
        + 1
    )

    cloned = snapshot.model_copy(
        update={
            "id": str(uuid4()),
            "original_number": (
                snapshot.original_number
                or str(next_order)
            ),
            "order_index": next_order,
            "status": QuestionStatus.needs_review,
            "attachments": _clone_attachments(snapshot),
            "parts": _clone_parts(snapshot),
            "linked_layout_asset_ids": [],
            "source_page_numbers": [],
            "source_page_start": None,
            "source_page_end": None,
            "reused_from_question_bank_item_id":
                bank_item.id,
            "reused_from_source_project_id":
                bank_item.source_project_id,
            "reused_at":
                datetime.now(timezone.utc),
            "review_notes": (
                "أُعيد استخدام السؤال من بنك الأسئلة؛ "
                "يجب مراجعته داخل سياق المشروع الحالي."
            ),
        },
        deep=True,
    )

    target_project.questions.append(cloned)
    return cloned, True
