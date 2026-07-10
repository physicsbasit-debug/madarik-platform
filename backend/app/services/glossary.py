"""Deterministic glossary extraction for Phase 1-E1.

This phase deliberately avoids AI. It uses a small internal science-term seed list
and scans parsed question text conservatively. The output is for teacher review only.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from hashlib import sha1

from app.models.project import GlossaryTerm, GlossaryTermStatus, QuestionItem


@dataclass(frozen=True)
class TermDefinition:
    english: str
    arabic: str
    subject: str


SCIENCE_TERMS: tuple[TermDefinition, ...] = (
    # Physics
    TermDefinition("resultant force", "القوة المحصلة", "فيزياء"),
    TermDefinition("force", "القوة", "فيزياء"),
    TermDefinition("mass", "الكتلة", "فيزياء"),
    TermDefinition("weight", "الوزن", "فيزياء"),
    TermDefinition("density", "الكثافة", "فيزياء"),
    TermDefinition("speed", "السرعة", "فيزياء"),
    TermDefinition("velocity", "السرعة المتجهة", "فيزياء"),
    TermDefinition("acceleration", "التسارع", "فيزياء"),
    TermDefinition("distance", "المسافة", "فيزياء"),
    TermDefinition("time", "الزمن", "فيزياء"),
    TermDefinition("energy", "الطاقة", "فيزياء"),
    TermDefinition("work done", "الشغل المبذول", "فيزياء"),
    TermDefinition("power", "القدرة", "فيزياء"),
    TermDefinition("current", "شدة التيار", "فيزياء"),
    TermDefinition("resistance", "المقاومة", "فيزياء"),
    TermDefinition("potential difference", "فرق الجهد", "فيزياء"),
    TermDefinition("voltage", "فرق الجهد", "فيزياء"),
    TermDefinition("circuit", "دائرة كهربائية", "فيزياء"),
    TermDefinition("series circuit", "دائرة توالٍ", "فيزياء"),
    TermDefinition("parallel circuit", "دائرة توازٍ", "فيزياء"),
    TermDefinition("wave", "موجة", "فيزياء"),
    TermDefinition("frequency", "التردد", "فيزياء"),
    TermDefinition("wavelength", "الطول الموجي", "فيزياء"),
    TermDefinition("amplitude", "السعة", "فيزياء"),
    TermDefinition("reflection", "الانعكاس", "فيزياء"),
    TermDefinition("refraction", "الانكسار", "فيزياء"),
    # Chemistry
    TermDefinition("rate of reaction", "معدل التفاعل", "كيمياء"),
    TermDefinition("reaction rate", "معدل التفاعل", "كيمياء"),
    TermDefinition("temperature", "درجة الحرارة", "كيمياء"),
    TermDefinition("concentration", "التركيز", "كيمياء"),
    TermDefinition("catalyst", "عامل حفاز", "كيمياء"),
    TermDefinition("enzyme", "إنزيم", "أحياء"),
    TermDefinition("acid", "حمض", "كيمياء"),
    TermDefinition("alkali", "قلوي", "كيمياء"),
    TermDefinition("base", "قاعدة", "كيمياء"),
    TermDefinition("neutralisation", "تعادل", "كيمياء"),
    TermDefinition("oxidation", "أكسدة", "كيمياء"),
    TermDefinition("reduction", "اختزال", "كيمياء"),
    TermDefinition("molecule", "جزيء", "كيمياء"),
    TermDefinition("atom", "ذرة", "كيمياء"),
    TermDefinition("ion", "أيون", "كيمياء"),
    # Biology
    TermDefinition("cell membrane", "غشاء الخلية", "أحياء"),
    TermDefinition("cell wall", "جدار الخلية", "أحياء"),
    TermDefinition("cytoplasm", "السيتوبلازم", "أحياء"),
    TermDefinition("nucleus", "النواة", "أحياء"),
    TermDefinition("mitochondria", "الميتوكوندريا", "أحياء"),
    TermDefinition("chloroplast", "البلاستيدة الخضراء", "أحياء"),
    TermDefinition("photosynthesis", "البناء الضوئي", "أحياء"),
    TermDefinition("respiration", "التنفس", "أحياء"),
    TermDefinition("diffusion", "الانتشار", "أحياء"),
    TermDefinition("osmosis", "الخاصية الأسموزية", "أحياء"),
    TermDefinition("active transport", "النقل النشط", "أحياء"),
    TermDefinition("transpiration", "النتح", "أحياء"),
    TermDefinition("pollination", "التلقيح", "أحياء"),
)


def _whole_phrase_pattern(term: str) -> re.Pattern[str]:
    """Return a conservative word-boundary pattern for an English term."""

    escaped = re.escape(term.lower()).replace(r"\ ", r"\s+")
    return re.compile(rf"(?<![a-z]){escaped}(?![a-z])", flags=re.IGNORECASE)


def _stable_term_id(english_term: str) -> str:
    digest = sha1(english_term.lower().encode("utf-8")).hexdigest()[:10]
    return f"term-{digest}"


def _question_text_blob(questions: list[QuestionItem]) -> str:
    return "\n".join(question.original_text for question in questions if question.original_text.strip())


def extract_glossary_terms_from_questions(
    questions: list[QuestionItem],
    *,
    default_subject: str = "",
) -> list[GlossaryTerm]:
    """Extract known science terms from parsed question cards.

    This is intentionally rule-based and deterministic. Terms are sorted by first
    appearance in the question text, then by phrase length, so multi-word terms
    like "rate of reaction" are preferred over smaller fragments.
    """

    text_blob = _question_text_blob(questions)
    if not text_blob.strip():
        return []

    lowered = text_blob.lower()
    detected: list[tuple[int, TermDefinition]] = []
    seen_english: set[str] = set()

    # Sort longer terms first to reduce noisy single-word duplicates in the same location.
    sorted_terms = sorted(SCIENCE_TERMS, key=lambda item: len(item.english), reverse=True)
    for definition in sorted_terms:
        english_key = definition.english.lower()
        if english_key in seen_english:
            continue
        match = _whole_phrase_pattern(definition.english).search(lowered)
        if match:
            detected.append((match.start(), definition))
            seen_english.add(english_key)

    detected.sort(key=lambda item: (item[0], item[1].english))

    terms: list[GlossaryTerm] = []
    for _, definition in detected:
        terms.append(
            GlossaryTerm(
                id=_stable_term_id(definition.english),
                english_term=definition.english,
                arabic_term=definition.arabic,
                subject=definition.subject or default_subject,
                status=GlossaryTermStatus.needs_review,
                source="detected",
                notes="مصطلح مكتشف آليًا من أسئلة الورقة. راجعه قبل الترجمة.",
            )
        )
    return terms
