from __future__ import annotations

import re

from app.models.project import AnswerKeyItem, QuestionItem, QuestionStatus


def _normalise(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def _question_core_text(question: QuestionItem) -> str:
    text = question.translated_text.strip() or question.original_text.strip()
    return _normalise(text)


def _draft_answer_for_question(question: QuestionItem) -> tuple[str, str]:
    """Return a conservative answer draft and confidence marker.

    This is not a true model answer engine. It is a teacher-review scaffold, which
    is a polite way to say: useful, but do not hand it to students like stone
    tablets from a mountain.
    """

    text = _question_core_text(question)
    lower = f"{question.original_text} {question.translated_text}".lower()

    if "cell membrane" in lower or "غشاء الخلية" in text:
        return "يسمح غشاء الخلية بمرور بعض المواد إلى داخل الخلية وخارجها، ويساعد على تنظيم تبادل المواد.", "medium"

    if "current" in lower and "resistance" in lower:
        return "تقل شدة التيار عند زيادة المقاومة لأن المقاومة تعيق حركة الشحنات في الدائرة عند ثبات فرق الجهد.", "medium"

    if "speed" in lower and "frequency" in lower and "wavelength" in lower:
        return "تستخدم العلاقة: السرعة = التردد × الطول الموجي، ثم تعوّض القيم المعطاة مع كتابة الوحدة المناسبة.", "medium"

    if "rate of reaction" in lower or "معدل التفاعل" in text:
        return "يزداد معدل التفاعل غالبًا بزيادة درجة الحرارة بسبب زيادة طاقة الجسيمات وعدد التصادمات الفعّالة.", "medium"

    if re.search(r"\bcalculate\b|احسب", lower + " " + text):
        return "يُراجع القانون المناسب، ثم تُعوّض القيم المعطاة في السؤال مع إظهار خطوات الحساب والوحدة النهائية.", "low"

    if re.search(r"\bexplain\b|فسّر", lower + " " + text):
        return "إجابة تفسيرية تربط السبب بالنتيجة باستخدام المفهوم العلمي المناسب من الدرس.", "low"

    if re.search(r"\bdescribe\b|صف", lower + " " + text):
        return "وصف علمي منظم يذكر التغير أو الخاصية المطلوبة كما وردت في السؤال.", "low"

    if re.search(r"\bstate\b|اذكر", lower + " " + text):
        return "تُذكر النقطة أو المصطلح العلمي المطلوب مباشرة دون شرح زائد.", "low"

    return "مسودة إجابة تحتاج مراجعة المعلم بناءً على نص السؤال والمفهوم العلمي المستهدف.", "low"


def build_answer_key_draft(questions: list[QuestionItem]) -> list[AnswerKeyItem]:
    """Build a draft answer key for non-deleted questions."""

    answer_items: list[AnswerKeyItem] = []
    active_questions = sorted(
        [question for question in questions if question.status != QuestionStatus.deleted],
        key=lambda question: question.order_index,
    )

    for index, question in enumerate(active_questions, start=1):
        draft_answer, confidence = _draft_answer_for_question(question)
        answer_items.append(
            AnswerKeyItem(
                question_id=question.id,
                question_number=str(index),
                draft_answer=draft_answer,
                marks=question.marks,
                confidence=confidence,
                source="pattern-draft",
                needs_review=True,
                notes="هذه مسودة آلية لمساعدة المعلم، وليست نموذج إجابة معتمدًا.",
            )
        )

    return answer_items
