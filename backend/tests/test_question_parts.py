from __future__ import annotations

from app.models.project import (
    ProjectSession,
    QuestionItem,
)
from app.services.question_parser import (
    parse_questions_from_text,
)
from app.services.question_parts import (
    extract_part_marks,
    normalize_part_label,
    parse_question_parts,
)


COMPLEX_QUESTION = """
(a) Complete the definitions by giving the name of each quantity.
mass × acceleration = ................................ [2]

(b) Fig. 2.2 shows a man using a golf club to hit a ball.
The ball has a mass of 0.046 kg.
The club is in contact for 5.0 × 10–4 s and the ball leaves at 65 m / s.

(i) Calculate the momentum of the ball. [2]
(ii) Calculate the average resultant force. [2]
(iii) State the type of energy stored in the compressed ball. [1]
[Total: 7]
"""


def test_parse_complex_question_parts_in_order() -> None:
    parts = parse_question_parts(COMPLEX_QUESTION)

    assert [part.label for part in parts] == [
        "(a)",
        "(b)",
        "(i)",
        "(ii)",
        "(iii)",
    ]

    assert [part.order_index for part in parts] == [
        1,
        2,
        3,
        4,
        5,
    ]

    assert parts[0].parent_id is None
    assert parts[1].parent_id is None
    assert [
        part.parent_id
        for part in parts[2:]
    ] == [
        parts[1].id,
        parts[1].id,
        parts[1].id,
    ]

    assert [part.marks for part in parts] == [
        2,
        None,
        2,
        2,
        1,
    ]


def test_parser_preserves_figure_references_and_units() -> None:
    parts = parse_question_parts(COMPLEX_QUESTION)

    second_part = parts[1].original_text

    assert "Fig. 2.2" in second_part
    assert "0.046 kg" in second_part
    assert "5.0 × 10–4 s" in second_part
    assert "65 m / s" in second_part


def test_parser_preserves_empty_parent_with_roman_children() -> None:
    parts = parse_question_parts(
        "(d) State whether the results agree. "
        "(e) "
        "(i) Draw the symbol. [1] "
        "(ii) Explain why the method is reliable. [2]"
    )

    assert [part.label for part in parts] == [
        "(d)",
        "(e)",
        "(i)",
        "(ii)",
    ]
    assert parts[1].original_text == ""
    assert parts[2].parent_id == parts[1].id
    assert parts[3].parent_id == parts[1].id


def test_normal_alphabetic_sequence_keeps_i_as_root_part() -> None:
    parts = parse_question_parts(
        "(h) State one reason. "
        "(i) State a second reason. "
        "(j) State a third reason."
    )

    assert [part.label for part in parts] == [
        "(h)",
        "(i)",
        "(j)",
    ]
    assert all(part.parent_id is None for part in parts)


def test_roman_only_sequence_stays_flat_without_parent() -> None:
    parts = parse_question_parts(
        "(i) State the unit. [1] "
        "(ii) Calculate the value. [2]"
    )

    assert [part.label for part in parts] == [
        "(i)",
        "(ii)",
    ]
    assert all(part.parent_id is None for part in parts)


def test_text_without_part_markers_returns_empty_list() -> None:
    assert parse_question_parts(
        "Calculate the momentum of the ball. [2]"
    ) == []


def test_uppercase_mcq_options_are_not_question_parts() -> None:
    text = (
        "Which quantity is measured in newtons? "
        "A mass B force C power D energy"
    )

    assert parse_question_parts(text) == []


def test_single_part_marker_is_allowed_at_start_only() -> None:
    start_parts = parse_question_parts(
        "(a) State the unit of force. [1]"
    )

    incidental_parts = parse_question_parts(
        "Use statement (a) when explaining the answer."
    )

    assert len(start_parts) == 1
    assert start_parts[0].label == "(a)"
    assert incidental_parts == []


def test_prefix_before_multiple_parts_is_preserved() -> None:
    parts = parse_question_parts(
        "Answer all parts. "
        "(a) Define momentum. [1] "
        "(b) Calculate momentum. [2]"
    )

    assert len(parts) == 2
    assert parts[0].original_text.startswith(
        "Answer all parts."
    )


def test_label_and_marks_helpers() -> None:
    assert normalize_part_label("ii") == "(ii)"
    assert normalize_part_label("(a)") == "(a)"

    assert extract_part_marks(
        "Calculate the force. [2]"
    ) == 2

    assert extract_part_marks(
        "No explicit mark value."
    ) is None


def test_old_question_payload_defaults_to_empty_parts() -> None:
    question = QuestionItem.model_validate(
        {
            "id": "old-question",
            "original_number": "1",
            "original_text": "Old saved question",
            "translated_text": "سؤال قديم",
            "order_index": 1,
        }
    )

    assert question.parts == []


def test_old_question_part_payload_defaults_to_root_level() -> None:
    part = QuestionItem.model_validate(
        {
            "id": "question-with-old-part",
            "original_number": "2",
            "original_text": "Old multipart question",
            "translated_text": "",
            "order_index": 1,
            "parts": [
                {
                    "id": "old-part",
                    "label": "(a)",
                    "original_text": "State the unit.",
                    "translated_text": "",
                    "marks": 1,
                    "order_index": 1,
                }
            ],
        }
    ).parts[0]

    assert part.parent_id is None


def test_project_round_trip_preserves_question_parts() -> None:
    parts = parse_question_parts(
        "(a) Define force. [1] "
        "(b) "
        "(i) Calculate force. [2]"
    )

    project = ProjectSession(
        questions=[
            QuestionItem(
                id="question-1",
                original_number="1",
                original_text="Multipart question",
                translated_text="",
                order_index=1,
                parts=parts,
            )
        ]
    )

    restored = ProjectSession.model_validate(
        project.model_dump(mode="json")
    )

    restored_parts = restored.questions[0].parts

    assert len(restored_parts) == 3
    assert restored_parts[2].marks == 2
    assert restored_parts[2].parent_id == restored_parts[1].id


def test_question_parser_populates_parts() -> None:
    questions = parse_questions_from_text(
        "1 (a) Define momentum. [1]\n"
        "(b) Calculate momentum. [2]"
    )

    assert len(questions) == 1

    assert [
        part.label
        for part in questions[0].parts
    ] == [
        "(a)",
        "(b)",
    ]


def test_question_parser_keeps_mcq_behavior() -> None:
    questions = parse_questions_from_text(
        "1 Which quantity is measured in newtons? "
        "A mass B force C power D energy"
    )

    assert len(questions) == 1

    assert [
        option.label
        for option in questions[0].options
    ] == [
        "A",
        "B",
        "C",
        "D",
    ]

    assert questions[0].parts == []
