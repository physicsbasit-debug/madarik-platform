from __future__ import annotations

from dataclasses import dataclass
import re
from typing import Iterable

from app.models.project import (
    ExtractedPdfPageInfo,
    FullExamIntakeCheck,
    FullExamIntakeReport,
    FullExamIntakeStatus,
    FullExamPageSummary,
    FullExamQuestionSpan,
    PdfLayoutAssetInfo,
    PdfPageKind,
    QuestionItem,
    QuestionStatus,
)
from app.services.question_parts import parse_question_parts
from app.services.text_extraction import PdfTextPage


_MAIN_QUESTION_RE = re.compile(
    r"^\s*(?P<number>\d{1,2})\s+(?P<body>\S.*)$"
)
_TOTAL_MARKS_RE = re.compile(
    r"\[\s*Total\s*:\s*(?P<marks>\d{1,3})\s*\]",
    flags=re.IGNORECASE,
)
_REPORTED_TOTAL_RE = re.compile(
    r"total\s+mark\s+for\s+this\s+paper\s+is\s+(?P<marks>\d{1,3})",
    flags=re.IGNORECASE,
)
_VISUAL_REFERENCE_RE = re.compile(
    r"\b(?:Fig(?:ure)?|Table|Diagram|Graph)[ \t]*\.?[ \t]*\d+(?:\.\d+)?",
    flags=re.IGNORECASE,
)
_ONLY_ANSWER_LINE_RE = re.compile(r"^[\s._…·-]+(?:\[\s*\d+\s*\])?$")
_MARK_SUFFIX_RE = re.compile(r"(\[\s*\d+\s*\])\s*$")


@dataclass(frozen=True)
class _QuestionStart:
    number: int
    page_number: int
    line_index: int
    body: str


@dataclass(frozen=True)
class _QuestionSegment:
    number: int
    page_numbers: tuple[int, ...]
    lines: tuple[str, ...]


_BOILERPLATE_SUBSTRINGS = (
    "© UCLES",
    "[Turn over]",
)
_PAGE_CODE_RE = re.compile(r"^\d{4}/\d{2}/[A-Z]{1,4}/\d{2}", flags=re.IGNORECASE)
_DOCUMENT_PAGE_COUNT_RE = re.compile(
    r"^This document has \d+ pages?(?:\.|$)",
    flags=re.IGNORECASE,
)
_BARCODE_RE = re.compile(r"^\*?\d{8,}\*?$")
_LEGAL_PREFIXES = (
    "Permission to reproduce items",
    "reasonable effort has been made",
    "publisher (UCLES)",
    "publisher will be pleased",
    "Cambridge Assessment International Education",
    "Cambridge Assessment Group",
    "Cambridge Assessment is the brand name",
    "University of Cambridge Local Examinations Syndicate",
    "Cambridge Local Examinations Syndicate",
)


def _compact_line(value: str) -> str:
    return re.sub(r"[ \t]+", " ", value or "").strip()


def _is_page_boilerplate(line: str, page_number: int) -> bool:
    compact = _compact_line(line)
    if not compact:
        return True
    if compact == str(page_number):
        return True
    if any(fragment in compact for fragment in _BOILERPLATE_SUBSTRINGS):
        return True
    if _PAGE_CODE_RE.match(compact):
        return True
    if _DOCUMENT_PAGE_COUNT_RE.match(compact):
        return True
    if _BARCODE_RE.match(compact):
        return True
    if any(compact.startswith(prefix) for prefix in _LEGAL_PREFIXES):
        return True
    return False


def _clean_answer_line(line: str) -> str:
    compact = _compact_line(line)
    if not compact:
        return ""
    if _ONLY_ANSWER_LINE_RE.fullmatch(compact):
        mark_match = _MARK_SUFFIX_RE.search(compact)
        return mark_match.group(1) if mark_match else ""
    return compact


def _visual_reference_keys(text: str) -> set[str]:
    return {
        re.sub(r"\s+", "", match.group(0)).casefold()
        for match in _VISUAL_REFERENCE_RE.finditer(text or "")
    }


def clean_pdf_page_lines(page: ExtractedPdfPageInfo | PdfTextPage) -> list[str]:
    """Remove repeated page furniture while preserving exam content."""

    page_number = page.page_number
    text = page.text
    cleaned: list[str] = []
    for raw_line in text.replace("\r\n", "\n").replace("\r", "\n").split("\n"):
        if _is_page_boilerplate(raw_line, page_number):
            continue
        line = _clean_answer_line(raw_line)
        if line:
            cleaned.append(line)
    return cleaned


def _is_semantic_blank(lines: list[str]) -> bool:
    meaningful = [line for line in lines if line.casefold() != "blank page"]
    return not meaningful


def _is_cover_page(page_number: int, lines: list[str]) -> bool:
    text = "\n".join(lines).casefold()
    return (
        page_number == 1
        and "instructions" in text
        and "information" in text
        and "answer all questions" in text
    )


def _find_question_starts(
    pages: list[ExtractedPdfPageInfo | PdfTextPage],
) -> tuple[list[_QuestionStart], dict[int, list[str]]]:
    """Find sequential main-question starts without confusing graph values for questions."""

    starts: list[_QuestionStart] = []
    cleaned_by_page: dict[int, list[str]] = {}
    expected_number = 1

    for page in pages:
        lines = clean_pdf_page_lines(page)
        cleaned_by_page[page.page_number] = lines
        if _is_semantic_blank(lines) or _is_cover_page(page.page_number, lines):
            continue

        for line_index, line in enumerate(lines):
            match = _MAIN_QUESTION_RE.match(line)
            if not match:
                continue

            number = int(match.group("number"))
            body = match.group("body").strip()
            if number != expected_number:
                continue
            if not body or re.fullmatch(r"[\d\s./-]+", body):
                continue

            starts.append(
                _QuestionStart(
                    number=number,
                    page_number=page.page_number,
                    line_index=line_index,
                    body=body,
                )
            )
            expected_number += 1

    return starts, cleaned_by_page


def _build_question_segments(
    pages: list[ExtractedPdfPageInfo | PdfTextPage],
) -> tuple[list[_QuestionSegment], dict[int, list[str]]]:
    starts, cleaned_by_page = _find_question_starts(pages)
    if not starts:
        return [], cleaned_by_page

    positions = {
        (start.page_number, start.line_index): start
        for start in starts
    }
    ordered_pages = sorted(cleaned_by_page)
    page_index_lookup = {page_number: index for index, page_number in enumerate(ordered_pages)}
    segments: list[_QuestionSegment] = []

    for start_index, start in enumerate(starts):
        next_start = starts[start_index + 1] if start_index + 1 < len(starts) else None
        lines: list[str] = []
        page_numbers: list[int] = []

        first_page_index = page_index_lookup[start.page_number]
        last_page_index = (
            page_index_lookup[next_start.page_number]
            if next_start is not None
            else len(ordered_pages) - 1
        )

        for page_position in range(first_page_index, last_page_index + 1):
            page_number = ordered_pages[page_position]
            page_lines = cleaned_by_page[page_number]
            if _is_semantic_blank(page_lines) or _is_cover_page(page_number, page_lines):
                continue

            begin = start.line_index if page_number == start.page_number else 0
            end = (
                next_start.line_index
                if next_start is not None and page_number == next_start.page_number
                else len(page_lines)
            )

            selected = page_lines[begin:end]
            if page_number == start.page_number and selected:
                first_line_match = _MAIN_QUESTION_RE.match(selected[0])
                if first_line_match and int(first_line_match.group("number")) == start.number:
                    selected = [first_line_match.group("body").strip(), *selected[1:]]

            selected = [line for line in selected if line.casefold() != "blank page"]
            if selected:
                lines.extend(selected)
                page_numbers.append(page_number)

        if lines and page_numbers:
            segments.append(
                _QuestionSegment(
                    number=start.number,
                    page_numbers=tuple(dict.fromkeys(page_numbers)),
                    lines=tuple(lines),
                )
            )

    return segments, cleaned_by_page


def _extract_total_marks(text: str) -> int | None:
    matches = list(_TOTAL_MARKS_RE.finditer(text))
    if not matches:
        return None
    return int(matches[-1].group("marks"))


def _strip_total_line(text: str) -> str:
    return _TOTAL_MARKS_RE.sub("", text).strip()


def parse_full_exam_questions_from_pages(
    pages: Iterable[ExtractedPdfPageInfo | PdfTextPage],
) -> list[QuestionItem]:
    """Build page-aware question cards from a complete text-based exam PDF.

    Main question numbers are accepted only in sequential order. This prevents
    chart axes, page numbers, values, and paper codes from becoming imaginary
    questions. Continuation pages remain attached to the current question.
    """

    page_list = sorted(list(pages), key=lambda item: item.page_number)
    segments, _ = _build_question_segments(page_list)
    questions: list[QuestionItem] = []

    for order_index, segment in enumerate(segments, start=1):
        raw_text = "\n".join(segment.lines).strip()
        detected_marks = _extract_total_marks(raw_text)
        original_text = _strip_total_line(raw_text)
        page_start = min(segment.page_numbers)
        page_end = max(segment.page_numbers)
        page_label = (
            f"الصفحة {page_start}"
            if page_start == page_end
            else f"الصفحات {page_start}–{page_end}"
        )
        parts = parse_question_parts(original_text)

        questions.append(
            QuestionItem(
                id=f"full-exam-q-{segment.number}",
                original_number=str(segment.number),
                original_text=original_text,
                raw_text=raw_text,
                translated_text="ترجمة مؤجلة إلى مسار المراجعة.",
                marks=detected_marks,
                detected_marks=detected_marks,
                status=QuestionStatus.needs_review,
                order_index=order_index,
                attachment_note=(
                    f"تم اكتشاف السؤال من {page_label}. "
                    "تُربط لقطات صفحات PDF آليًا عند توفرها."
                ),
                parts=parts,
                source_page_numbers=list(segment.page_numbers),
                source_page_start=page_start,
                source_page_end=page_end,
                review_notes=(
                    "تم تقسيم هذا السؤال ضمن قبول ورقة كاملة بقواعد Phase 4-A6a. "
                    f"المصدر: {page_label}. راجع النص والأجزاء والرسوم قبل الترجمة."
                ),
            )
        )

    return questions


def link_layout_assets_to_page_aware_questions(
    questions: list[QuestionItem],
    layout_assets: list[PdfLayoutAssetInfo],
) -> list[QuestionItem]:
    """Link full-page layout snapshots to questions using detected source pages."""

    asset_ids_by_page: dict[int, list[str]] = {}
    for asset in layout_assets:
        asset_ids_by_page.setdefault(asset.page_number, []).append(asset.id)

    linked_questions: list[QuestionItem] = []
    for question in questions:
        detected_ids = [
            asset_id
            for page_number in question.source_page_numbers
            for asset_id in asset_ids_by_page.get(page_number, [])
        ]
        merged_ids = list(dict.fromkeys([*question.linked_layout_asset_ids, *detected_ids]))
        note = question.attachment_note
        if detected_ids:
            note = (
                f"تم ربط {len(detected_ids)} لقطة صفحة PDF آليًا بهذا السؤال وفق صفحات المصدر. "
                "استخدم القص البصري لاحقًا لعزل الرسم أو الجدول المطلوب."
            )
        linked_questions.append(
            question.model_copy(
                update={
                    "linked_layout_asset_ids": merged_ids,
                    "attachment_note": note,
                }
            )
        )
    return linked_questions


def _reported_total_marks(pages: list[ExtractedPdfPageInfo | PdfTextPage]) -> int | None:
    for page in pages:
        match = _REPORTED_TOTAL_RE.search(page.text)
        if match:
            return int(match.group("marks"))
    return None


def _question_spans_from_segments(
    segments: list[_QuestionSegment],
    questions: list[QuestionItem] | None,
) -> list[FullExamQuestionSpan]:
    question_by_number = {
        question.original_number: question
        for question in (questions or [])
    }
    spans: list[FullExamQuestionSpan] = []
    for segment in segments:
        text = "\n".join(segment.lines)
        question = question_by_number.get(str(segment.number))
        linked_count = len(question.linked_layout_asset_ids) if question else 0
        spans.append(
            FullExamQuestionSpan(
                question_number=str(segment.number),
                page_numbers=list(segment.page_numbers),
                page_start=min(segment.page_numbers),
                page_end=max(segment.page_numbers),
                detected_total_marks=_extract_total_marks(text),
                visual_reference_count=len(_visual_reference_keys(text)),
                linked_layout_asset_count=linked_count,
            )
        )
    return spans


def build_full_exam_intake_report(
    pages: Iterable[ExtractedPdfPageInfo | PdfTextPage],
    *,
    questions: list[QuestionItem] | None = None,
) -> FullExamIntakeReport:
    """Build a deterministic structural acceptance report for one complete exam."""

    page_list = sorted(list(pages), key=lambda item: item.page_number)
    segments, cleaned_by_page = _build_question_segments(page_list)
    spans = _question_spans_from_segments(segments, questions)
    page_to_questions: dict[int, list[str]] = {}
    for span in spans:
        for page_number in span.page_numbers:
            page_to_questions.setdefault(page_number, []).append(span.question_number)

    page_summaries: list[FullExamPageSummary] = []
    blank_count = 0
    cover_count = 0
    question_page_count = 0
    visual_reference_keys: set[str] = set()

    for page in page_list:
        lines = cleaned_by_page.get(page.page_number, clean_pdf_page_lines(page))
        page_visual_keys = _visual_reference_keys("\n".join(lines))
        visual_count = len(page_visual_keys)
        visual_reference_keys.update(page_visual_keys)
        question_numbers = page_to_questions.get(page.page_number, [])

        if _is_semantic_blank(lines):
            kind = PdfPageKind.blank
            blank_count += 1
        elif _is_cover_page(page.page_number, lines):
            kind = PdfPageKind.cover
            cover_count += 1
        elif question_numbers:
            kind = PdfPageKind.question
            question_page_count += 1
        else:
            kind = PdfPageKind.other

        page_summaries.append(
            FullExamPageSummary(
                page_number=page.page_number,
                kind=kind,
                character_count=len(page.text),
                question_numbers=question_numbers,
                visual_reference_count=visual_count,
            )
        )

    detected_numbers = [span.question_number for span in spans]
    sequential = detected_numbers == [str(index) for index in range(1, len(detected_numbers) + 1)]
    detected_total_values = [
        span.detected_total_marks
        for span in spans
        if span.detected_total_marks is not None
    ]
    detected_total = sum(detected_total_values) if detected_total_values else None
    reported_total = _reported_total_marks(page_list)
    totals_match = (
        reported_total is not None
        and detected_total is not None
        and reported_total == detected_total
    )
    all_questions_have_totals = bool(spans) and len(detected_total_values) == len(spans)
    linked_count = sum(span.linked_layout_asset_count for span in spans)
    visual_reference_count = len(visual_reference_keys)

    checks = [
        FullExamIntakeCheck(
            code="pages_available",
            passed=bool(page_list),
            message=(
                f"تم الاحتفاظ بحدود {len(page_list)} صفحة."
                if page_list
                else "لم تُستخرج صفحات قابلة للفحص."
            ),
        ),
        FullExamIntakeCheck(
            code="cover_detected",
            passed=cover_count >= 1,
            message=(
                "تم تمييز صفحة الغلاف والتعليمات."
                if cover_count >= 1
                else "لم تُميز صفحة غلاف واضحة."
            ),
        ),
        FullExamIntakeCheck(
            code="sequential_questions",
            passed=sequential and bool(spans),
            message=(
                f"تسلسل الأسئلة الرئيسية مكتمل من 1 إلى {len(spans)}."
                if sequential and spans
                else "تسلسل أرقام الأسئلة الرئيسية غير مكتمل أو غير واضح."
            ),
        ),
        FullExamIntakeCheck(
            code="question_totals_detected",
            passed=all_questions_have_totals,
            message=(
                "تم اكتشاف مجموع الدرجات لكل سؤال رئيسي."
                if all_questions_have_totals
                else "لم يُكتشف مجموع الدرجات لبعض الأسئلة الرئيسية."
            ),
        ),
        FullExamIntakeCheck(
            code="paper_total_matches",
            passed=totals_match,
            message=(
                f"مجموع الأسئلة ({detected_total}) يطابق الدرجة المعلنة ({reported_total})."
                if totals_match
                else "مجموع درجات الأسئلة لا يطابق الدرجة المعلنة أو تعذر اكتشاف أحدهما."
            ),
        ),
    ]

    warnings: list[str] = []
    if blank_count:
        warnings.append(f"تم تجاوز {blank_count} صفحة فارغة وعدم تحويلها إلى سؤال.")
    if not sequential:
        warnings.append("تحتاج أرقام الأسئلة الرئيسية إلى مراجعة بشرية.")
    if not all_questions_have_totals:
        warnings.append("تحتاج مجاميع بعض الأسئلة إلى مراجعة بشرية.")
    if reported_total is not None and detected_total is not None and reported_total != detected_total:
        warnings.append(
            f"الدرجة المعلنة ({reported_total}) لا تطابق مجموع الأسئلة المكتشف ({detected_total})."
        )
    if visual_reference_count and linked_count == 0 and questions:
        warnings.append(
            "تم اكتشاف مراجع بصرية، لكن لم تُربط لقطات صفحات PDF بالأسئلة بعد."
        )

    if not page_list or not spans:
        status = FullExamIntakeStatus.rejected
    elif all(check.passed for check in checks):
        status = FullExamIntakeStatus.accepted
    else:
        status = FullExamIntakeStatus.needs_review

    return FullExamIntakeReport(
        status=status,
        page_count=len(page_list),
        content_page_count=max(0, len(page_list) - blank_count),
        blank_page_count=blank_count,
        cover_page_count=cover_count,
        question_page_count=question_page_count,
        detected_question_count=len(spans),
        detected_question_numbers=detected_numbers,
        reported_total_marks=reported_total,
        detected_total_marks=detected_total,
        multi_page_question_count=sum(1 for span in spans if len(span.page_numbers) > 1),
        visual_reference_count=visual_reference_count,
        auto_linked_layout_asset_count=linked_count,
        pages=page_summaries,
        question_spans=spans,
        checks=checks,
        warnings=warnings,
    )
