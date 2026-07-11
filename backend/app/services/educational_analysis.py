from __future__ import annotations

import re
from collections import Counter

from app.models.project import EducationalAnalysisReport, ProjectSession, QuestionItem, QuestionStatus


COMMAND_PATTERNS: list[tuple[str, str]] = [
    ("تذكر مباشر", r"\bstate\b|اذكر"),
    ("وصف", r"\bdescribe\b|صف"),
    ("تفسير", r"\bexplain\b|فسّر|فسر"),
    ("حساب", r"\bcalculate\b|احسب"),
    ("مقارنة", r"\bcompare\b|قارن"),
    ("اقتراح", r"\bsuggest\b|اقترح"),
    ("تحديد/تعرف", r"\bdetermine\b|\bidentify\b|حدّد|حدد|عرّف|عرف"),
    ("تبرير/تقويم", r"\bjustify\b|\bevaluate\b|برّر|برر|قيّم|قيم"),
    ("رسم/تسمية", r"\bdraw\b|\blabel\b|ارسم|سمِّ|سم"),
]


def _active_questions(project: ProjectSession) -> list[QuestionItem]:
    return sorted(
        [question for question in project.questions if question.status != QuestionStatus.deleted],
        key=lambda question: question.order_index,
    )


def _detect_command(question: QuestionItem) -> str:
    text = f"{question.original_text} {question.translated_text}".lower()
    for label, pattern in COMMAND_PATTERNS:
        if re.search(pattern, text, flags=re.IGNORECASE):
            return label
    return "غير مصنف"


def _review_load(warnings_count: int, needs_review_count: int, question_count: int) -> str:
    if question_count == 0:
        return "none"
    if warnings_count >= 3 or needs_review_count / max(question_count, 1) >= 0.6:
        return "high"
    if warnings_count >= 1 or needs_review_count:
        return "medium"
    return "low"


def _marks_bucket(marks: int | None) -> str:
    if marks is None:
        return "بلا درجة"
    if marks <= 1:
        return "درجة واحدة"
    if marks <= 3:
        return "2-3 درجات"
    return "4 درجات فأكثر"


def build_educational_analysis(project: ProjectSession) -> EducationalAnalysisReport:
    """Build a conservative educational analysis for the reviewed assessment.

    This is a foundation report, not a psychometric engine. Naturally, humans
    will ask for psychometrics before the data is clean. We decline politely here.
    """

    questions = _active_questions(project)
    question_count = len(questions)
    total_marks = sum(question.marks or 0 for question in questions)
    average_marks = round(total_marks / question_count, 2) if question_count else 0.0
    translated_question_count = sum(1 for question in questions if question.translated_text.strip())
    needs_review_count = sum(1 for question in questions if question.status == QuestionStatus.needs_review)

    command_distribution = Counter(_detect_command(question) for question in questions)
    marks_distribution = Counter(_marks_bucket(question.marks) for question in questions)

    warnings: list[str] = []
    recommendations: list[str] = []

    if question_count == 0:
        warnings.append("لا توجد أسئلة نشطة يمكن تحليلها.")
    if translated_question_count < question_count:
        warnings.append("توجد أسئلة بلا ترجمة مكتملة.")
    if any(question.marks is None for question in questions):
        warnings.append("توجد أسئلة بلا درجات محددة.")
    if not project.answer_key:
        warnings.append("لم تُولّد مسودة نموذج إجابة بعد.")
    if not project.layout_assets and project.uploaded_file and project.uploaded_file.name.lower().endswith(".pdf"):
        warnings.append("لا توجد لقطات تخطيط PDF مرفقة للمراجعة البصرية.")

    if command_distribution.get("تفسير", 0) + command_distribution.get("تبرير/تقويم", 0) == 0 and question_count:
        recommendations.append("أضف أو راجع أسئلة تفسير/تبرير لرفع عمق القياس، إن كان هدف الورقة يسمح بذلك.")
    if command_distribution.get("حساب", 0) and not project.answer_key:
        recommendations.append("ولّد مسودة نموذج الإجابة لمراجعة خطوات الحساب والوحدات قبل التصدير.")
    if needs_review_count:
        recommendations.append("اعتمد الأسئلة بعد مراجعة الترجمة والدرجات لتقليل عبء المراجعة قبل الطباعة.")
    if project.layout_assets:
        recommendations.append("راجع لقطات التخطيط للتأكد من مواضع الرسوم والجداول وربطها يدويًا بالسؤال المناسب عند الحاجة.")
    if not recommendations:
        recommendations.append("الورقة تبدو منظمة مبدئيًا؛ نفّذ مراجعة بشرية نهائية للترجمة ونموذج الإجابة قبل الاستخدام.")

    dominant_command = "غير مصنف"
    if command_distribution:
        dominant_command = command_distribution.most_common(1)[0][0]

    educational_summary = (
        f"تضم الورقة {question_count} سؤالًا نشطًا بإجمالي {total_marks} درجة ومتوسط {average_marks} درجة للسؤال. "
        f"أبرز نمط أسئلة ظاهر هو: {dominant_command}. "
        "القراءة تحليل تأسيسي يساعد المعلم على مراجعة الاتزان العام، وليست حكمًا نهائيًا على جودة الاختبار."
    )

    return EducationalAnalysisReport(
        question_count=question_count,
        total_marks=total_marks,
        average_marks=average_marks,
        translated_question_count=translated_question_count,
        answer_key_items_count=len(project.answer_key),
        layout_assets_count=len(project.layout_assets),
        command_distribution=dict(command_distribution),
        marks_distribution=dict(marks_distribution),
        review_load=_review_load(len(warnings), needs_review_count, question_count),
        educational_summary=educational_summary,
        recommendations=recommendations,
        warnings=warnings,
        needs_review=True,
    )
