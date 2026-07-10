"""Rule-based question parser for Phase 1-D.

This parser is intentionally conservative. It only converts extracted text into
separate question cards when it sees common exam question markers. AI-based
parsing, OCR layout analysis, and figure/table linking are deferred.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from app.models.project import QuestionItem, QuestionStatus

QUESTION_START_RE = re.compile(
    r"^\s*(?:question\s*)?(?P<number>\d{1,3})(?:\s*[\.)\]:-]|\s+)(?P<body>.*)$",
    re.IGNORECASE,
)
MARK_PATTERNS = (
    re.compile(r"\[(?P<marks>\d{1,2})\s*(?:mark|marks)?\]", re.IGNORECASE),
    re.compile(r"\((?P<marks>\d{1,2})\s*(?:mark|marks)\)", re.IGNORECASE),
    re.compile(r"(?P<marks>\d{1,2})\s*(?:mark|marks)\b", re.IGNORECASE),
)
WHITESPACE_RE = re.compile(r"[ \t]+")


@dataclass(frozen=True)
class ParsedQuestionDraft:
    """Internal draft produced before creating stable question IDs."""

    original_number: str
    original_text: str
    detected_marks: int | None


def _normalize_lines(text: str) -> list[str]:
    lines: list[str] = []
    for raw_line in text.replace("\r\n", "\n").replace("\r", "\n").split("\n"):
        line = WHITESPACE_RE.sub(" ", raw_line).strip()
        if line:
            lines.append(line)
    return lines


def _extract_marks(text: str) -> int | None:
    for pattern in MARK_PATTERNS:
        matches = list(pattern.finditer(text))
        if matches:
            try:
                return int(matches[-1].group("marks"))
            except (TypeError, ValueError):
                return None
    return None


def _looks_like_question_start(line: str) -> re.Match[str] | None:
    match = QUESTION_START_RE.match(line)
    if not match:
        return None

    body = match.group("body").strip()
    # Avoid treating bare page numbers or list fragments as questions.
    if not body:
        return None
    if len(body) < 3:
        return None
    return match


def parse_questions_from_text(text: str) -> list[QuestionItem]:
    """Parse extracted PDF text into reviewable question cards.

    The output is deliberately marked as needing review because Phase 1-D uses
    deterministic rules only. Translation is still deferred to Phase 1-E.
    """

    lines = _normalize_lines(text)
    if not lines:
        return []

    drafts: list[ParsedQuestionDraft] = []
    current_number: str | None = None
    current_lines: list[str] = []

    def flush_current() -> None:
        nonlocal current_number, current_lines
        if current_number is None or not current_lines:
            return
        original_text = "\n".join(current_lines).strip()
        if original_text:
            drafts.append(
                ParsedQuestionDraft(
                    original_number=current_number,
                    original_text=original_text,
                    detected_marks=_extract_marks(original_text),
                )
            )
        current_number = None
        current_lines = []

    for line in lines:
        match = _looks_like_question_start(line)
        if match:
            flush_current()
            current_number = match.group("number")
            body = match.group("body").strip()
            current_lines = [body if body else line.strip()]
        elif current_number is not None:
            current_lines.append(line)

    flush_current()

    if not drafts:
        fallback_text = "\n".join(lines).strip()
        detected_marks = _extract_marks(fallback_text)
        drafts = [
            ParsedQuestionDraft(
                original_number="1",
                original_text=fallback_text,
                detected_marks=detected_marks,
            )
        ]

    questions: list[QuestionItem] = []
    for index, draft in enumerate(drafts, start=1):
        questions.append(
            QuestionItem(
                id=f"parsed-q-{index}",
                original_number=draft.original_number,
                original_text=draft.original_text,
                translated_text="ترجمة مؤجلة إلى Phase 1-E.",
                marks=draft.detected_marks,
                detected_marks=draft.detected_marks,
                status=QuestionStatus.needs_review,
                order_index=index,
                attachment_note="لم يتم ربط الصور والجداول بعد. هذه الوظيفة مؤجلة.",
                review_notes="تم تقسيم هذا السؤال آليًا بقواعد Phase 1-D ويحتاج مراجعة بشرية قبل التصدير.",
            )
        )

    return questions
