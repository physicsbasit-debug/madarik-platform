"""Conservative parser for hierarchical multipart exam questions.

The parser preserves ``QuestionItem.original_text`` and adds a flat list of
``QuestionPart`` records. Hierarchy is represented through ``parent_id`` so
existing persistence and API contracts remain backward compatible.
"""

from __future__ import annotations

import re
from uuid import uuid4

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

ROMAN_LABEL_RE = re.compile(r"[ivxlcdm]{1,6}", re.IGNORECASE)
ROMAN_SINGLE_LABELS = frozenset("ivxlcdm")
WHITESPACE_RE = re.compile(r"[ \t]+")


def normalize_part_label(label: str) -> str:
    """Normalize labels such as a or (ii) to (a) and (ii)."""

    normalized = str(label or "").strip()

    if normalized.startswith("(") and normalized.endswith(")"):
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


def _is_next_alphabetic_label(
    previous_label: str | None,
    current_label: str,
) -> bool:
    if (
        previous_label is None
        or len(previous_label) != 1
        or len(current_label) != 1
        or not previous_label.isalpha()
        or not current_label.isalpha()
    ):
        return False

    return ord(current_label) == ord(previous_label) + 1


def _marker_kind(
    tokens: list[str],
    index: int,
    *,
    active_alpha_label: str | None,
    previous_kind: str | None,
) -> str:
    """Classify a marker as alphabetic, Roman, or numeric.

    Single-letter Roman symbols are ambiguous. Context keeps normal alphabetic
    sequences such as ``(h), (i), (j)`` at the root level, while familiar
    exam structures such as ``(b), (i), (ii)`` become parent and children.
    """

    token = tokens[index]

    if token.isdigit():
        return "numeric"

    if len(token) > 1 and ROMAN_LABEL_RE.fullmatch(token):
        return "roman"

    if token not in ROMAN_SINGLE_LABELS:
        return "alpha"

    if _is_next_alphabetic_label(
        active_alpha_label,
        token,
    ):
        return "alpha"

    next_token = (
        tokens[index + 1]
        if index + 1 < len(tokens)
        else None
    )

    if (
        token == "i"
        and next_token is not None
        and len(next_token) > 1
        and ROMAN_LABEL_RE.fullmatch(next_token)
    ):
        return "roman"

    if active_alpha_label is not None and token == "i":
        return "roman"

    if previous_kind == "roman":
        return "roman"

    return "alpha"


def parse_question_parts(text: str) -> list[QuestionPart]:
    """Parse familiar alphabetic, Roman and numeric part markers.

    Hierarchy rules remain deliberately conservative:

    - Alphabetic markers form root-level parts.
    - Roman or numeric markers following an alphabetic root become its children.
    - A normal alphabetic sequence such as ``(h), (i), (j)`` stays root-level.
    - Roman-only or numeric-only sequences without an alphabetic root stay flat.
    - A structural parent is retained even when it has no direct body text.
    - Uppercase A-D MCQ options and incidental prose references remain excluded.
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

    if len(markers) == 1 and prefix:
        return []

    tokens = [
        marker.group("label").lower()
        for marker in markers
    ]
    parts: list[QuestionPart] = []
    active_alpha_id: str | None = None
    active_alpha_label: str | None = None
    previous_kind: str | None = None

    for marker_index, marker in enumerate(markers):
        token = tokens[marker_index]
        kind = _marker_kind(
            tokens,
            marker_index,
            active_alpha_label=active_alpha_label,
            previous_kind=previous_kind,
        )

        part_id = str(uuid4())
        parent_id = (
            active_alpha_id
            if kind in {"roman", "numeric"}
            and active_alpha_id is not None
            else None
        )

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

        part = QuestionPart(
            id=part_id,
            label=normalize_part_label(token),
            original_text=body,
            translated_text="",
            marks=extract_part_marks(body),
            parent_id=parent_id,
            order_index=len(parts) + 1,
        )
        parts.append(part)

        if kind == "alpha":
            active_alpha_id = part_id
            active_alpha_label = token

        previous_kind = kind

    parent_ids = {
        part.parent_id
        for part in parts
        if part.parent_id is not None
    }

    kept_parts = [
        part
        for part in parts
        if part.original_text or part.id in parent_ids
    ]

    return [
        part.model_copy(
            update={"order_index": index}
        )
        for index, part in enumerate(
            kept_parts,
            start=1,
        )
    ]
