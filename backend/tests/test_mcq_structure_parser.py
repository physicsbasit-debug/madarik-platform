from app.models.project import QuestionItem
from app.services.question_parser import parse_questions_from_text


def test_inline_mcq_options_are_separated_from_question_stem() -> None:
    text = (
        "7 An object has a mass of 20 kg. "
        "Its velocity changes from 6 m/s to 10 m/s. "
        "Which impulse has acted on the object? "
        "A 80 Ns B 120 Ns C 200 Ns D 320 Ns"
    )

    questions = parse_questions_from_text(text)

    assert len(questions) == 1
    question = questions[0]

    assert question.original_number == "7"
    assert question.original_text == (
        "An object has a mass of 20 kg. "
        "Its velocity changes from 6 m/s to 10 m/s. "
        "Which impulse has acted on the object?"
    )
    assert [(option.label, option.text) for option in question.options] == [
        ("A", "80 Ns"),
        ("B", "120 Ns"),
        ("C", "200 Ns"),
        ("D", "320 Ns"),
    ]
    assert question.raw_text == text.removeprefix("7 ")
    assert question.marks is None


def test_opening_article_a_is_not_treated_as_option_marker() -> None:
    text = (
        "12 A student compares four containers. "
        "Which container has the greatest pressure? "
        "A first B second C third D fourth"
    )

    question = parse_questions_from_text(text)[0]

    assert question.original_text.startswith("A student compares")
    assert [option.label for option in question.options] == ["A", "B", "C", "D"]
    assert [option.text for option in question.options] == [
        "first",
        "second",
        "third",
        "fourth",
    ]


def test_old_question_payloads_remain_compatible() -> None:
    question = QuestionItem(
        id="legacy-question",
        original_number="1",
        original_text="State the function of the cell membrane.",
        translated_text="ترجمة تجريبية",
        order_index=1,
    )

    assert question.options == []
    assert question.raw_text is None
