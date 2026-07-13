"""Conservative parser for multipart exam questions.

Phase 3-A3a preserves QuestionItem.original_text and adds a structured
representation only when recognizable question-part markers are present.
"""

from __future__ import annotations

import re

from app.models.project import QuestionPart


PART_MARKER_RE = re.compile(
    r"(?<!\S)"
    r"\("
    r"(?P<label>"
    r"[a-z]"
    r"|[ivxlcdm]{1,6}"
    r"|\d{1,2}"
    r")"
    r"\)"
    r"(?=\s)"
    r"\s*",
    re.IGNORECASE,
)

PART_MARK_PATTERNS = (
    re.compile(
        r"\[(?P<marks>\d{1,2})\s*(?:mark|marks)?\]",
        re.IGNORECASE,
    ),
    re.compile(
        r"\((?P<marks>\d{1,2})\s*(?:mark|marks)\)",
        re.IGNORECASE,
    ),
)

WHITESPACE_RE = re.compile(r"[ \t]+")


def normalize_part_label(label: str) -> str:
    """Normalize labels such as a or (ii) to (a) and (ii)."""

    normalized = str(label or "").strip()

    if (
        normalized.startswith("(")
        and normalized.endswith(")")
    ):
        normalized = normalized[1:-1].strip()

    if not normalized:
        raise ValueError("وسم جزء السؤال فارغ.")

    if not re.fullmatch(
        r"(?:[a-z]|[ivxlcdm]{1,6}|\d{1,2})",
        normalized,
        re.IGNORECASE,
    ):
        raise ValueError(
            f"وسم جزء السؤال غير مدعوم: {label}"
        )

    return f"({normalized.lower()})"


def extract_part_marks(text: str) -> int | None:
    """Return the last explicit mark value in one part."""

    for pattern in PART_MARK_PATTERNS:
        matches = list(pattern.finditer(text))

        if not matches:
            continue

        try:
            return int(matches[-1].group("marks"))
        except (TypeError, ValueError):
            return None

    return None


def _normalize_source_text(text: str) -> str:
    return (
        str(text or "")
        .replace("\r\n", "\n")
        .replace("\r", "\n")
        .strip()
    )


def _normalize_part_text(text: str) -> str:
    lines: list[str] = []

    for raw_line in text.splitlines():
        line = WHITESPACE_RE.sub(
            " ",
            raw_line,
        ).strip()

        if line:
            lines.append(line)

    return "\n".join(lines).strip()


def parse_question_parts(text: str) -> list[QuestionPart]:
    """Parse familiar alphabetic, Roman and numeric part markers.

    Conservative rules:

    - Uppercase A-D MCQ options are handled elsewhere.
    - Figure references such as Fig. 2.2 are not markers.
    - Scientific units and equations remain untouched.
    - Text before the first marker is attached to the first part.
    - A lone marker is accepted only when it starts the question.
    - No reliable markers returns an empty list.
    """

    source = _normalize_source_text(text)

    if not source:
        return []

    markers = list(PART_MARKER_RE.finditer(source))

    if not markers:
        return []

    prefix = _normalize_part_text(
        source[: markers[0].start()]
    )

    # Avoid treating an incidental "(a)" inside prose as a
    # structured multipart question.
    if len(markers) == 1 and prefix:
        return []

    parts: list[QuestionPart] = []

    for marker_index, marker in enumerate(markers):
        body_start = marker.end()
        body_end = (
            markers[marker_index + 1].start()
            if marker_index + 1 < len(markers)
            else len(source)
        )

        body = _normalize_part_text(
            source[body_start:body_end]
        )

        if marker_index == 0 and prefix:
            body = _normalize_part_text(
                f"{prefix}\n{body}"
            )

        if not body:
            continue

        parts.append(
            QuestionPart(
                label=normalize_part_label(
                    marker.group("label")
                ),
                original_text=body,
                translated_text="",
                marks=extract_part_marks(body),
                order_index=len(parts) + 1,
            )
        )

    return parts
