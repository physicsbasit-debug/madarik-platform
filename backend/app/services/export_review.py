from __future__ import annotations

import re

from app.models.project import (
    FullExamTranslationAcceptanceStatus,
    MarksPolicy,
    OutputMode,
    ProjectMetadata,
    ProjectSession,
    QuestionItem,
)

_VISUAL_REFERENCE_PATTERN = re.compile(
    r"(?:"
    r"\b(?:fig(?:ure)?|diagram|graph|chart|table)\s*\.?\s*\d+(?:\.\d+)*"
    r"|\b(?:draw|sketch|plot)\b"
    r"|(?:الشكل|شكل|الرسم|رسم|المخطط|مخطط|الجدول|جدول)\s*\d*(?:\.\d+)*"
    r")",
    re.IGNORECASE,
)


def _question_review_text(question: QuestionItem) -> str:
    values = [
        question.original_text,
        question.translated_text,
        question.raw_text or "",
        *(part.original_text for part in question.parts),
        *(part.translated_text for part in question.parts),
        *(option.text for option in question.options),
    ]
    return "\n".join(value for value in values if value)


def question_requires_visual(question: QuestionItem) -> bool:
    """Return whether the question text explicitly depends on a visual."""

    return bool(_VISUAL_REFERENCE_PATTERN.search(_question_review_text(question)))


def missing_visual_asset_question_numbers(
    questions: list[QuestionItem],
    *,
    valid_attachment_ids: set[str] | None = None,
) -> list[str]:
    """List visual-dependent questions without a renderable question asset.

    Linked full-page snapshots remain review references. They do not count as a
    student-facing export asset until the teacher crops or uploads a question
    attachment. This prevents a single page snapshot from masquerading as every
    diagram in an exam.
    """

    missing: list[str] = []
    for index, question in enumerate(questions, start=1):
        if not question_requires_visual(question):
            continue

        if valid_attachment_ids is None:
            has_asset = bool(question.attachments)
        else:
            has_asset = any(
                attachment.id in valid_attachment_ids
                for attachment in question.attachments
            )

        if not has_asset:
            missing.append(question.original_number.strip() or str(index))

    return missing


def parse_declared_total_marks(value: str) -> int | None:
    match = re.search(r"\d+", value or "")
    return int(match.group(0)) if match else None

def declared_total_marks_mismatch(
    metadata: ProjectMetadata,
    question_total: int,
) -> bool:
    declared = parse_declared_total_marks(metadata.total_marks)
    return declared is not None and declared != question_total


def marks_policy_resolves_total(
    metadata: ProjectMetadata,
    question_total: int,
) -> bool:
    """Return whether the paper-level marks mismatch has an explicit policy."""

    if not declared_total_marks_mismatch(metadata, question_total):
        return True

    if metadata.marks_policy == MarksPolicy.use_question_total:
        return True

    if metadata.marks_policy == MarksPolicy.scale_to_declared:
        declared = parse_declared_total_marks(metadata.total_marks)
        return bool(declared and declared > 0 and question_total > 0)

    return False


def student_export_marks_label(
    metadata: ProjectMetadata,
    question_total: int,
) -> str:
    """Return the honest paper-level marks label used in student exports."""

    declared = parse_declared_total_marks(metadata.total_marks)

    if declared is None:
        return str(question_total)

    if not declared_total_marks_mismatch(metadata, question_total):
        return str(declared)

    if metadata.marks_policy == MarksPolicy.use_question_total:
        return str(question_total)

    if metadata.marks_policy == MarksPolicy.scale_to_declared:
        return f"{declared} (محولة من {question_total})"

    return str(declared)


def student_export_total_label(metadata: ProjectMetadata) -> str:
    return (
        "المجموع الخام"
        if metadata.marks_policy == MarksPolicy.scale_to_declared
        else "مجموع الدرجات"
    )


def student_export_mode_label(project: ProjectSession) -> str:
    """Never label fallback or unaccepted Arabic as a clean final version."""

    if project.metadata.output_mode == OutputMode.bilingual:
        return "ثنائية اللغة"

    report = project.full_exam_translation_report
    if (
        report is not None
        and report.status == FullExamTranslationAcceptanceStatus.accepted
    ):
        return "عربية معتمدة"

    return "مسودة ترجمة تحتاج مراجعة"
