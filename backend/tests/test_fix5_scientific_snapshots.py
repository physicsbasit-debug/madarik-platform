from __future__ import annotations

from app.services.export import _clean_export_text
from app.services.scientific_text import normalise_scientific_text


def test_repairs_coefficient_first_negative_exponents_left_by_ocr() -> None:
    repaired = normalise_scientific_text(
        "duration 5.0 × 10–4 s; charge 8.5 × 10–10 C"
    )

    assert repaired == "duration 5.0 × 10⁻⁴ s; charge 8.5 × 10⁻¹⁰ C"


def test_repairs_negative_exponents_with_direction_marks() -> None:
    repaired = normalise_scientific_text(
        "5.0\u200e × \u200f10\u200e–\u200f4 s and "
        "8.5\u2066 × \u206910−10 C"
    )

    assert repaired == "5.0 × 10⁻⁴ s and 8.5 × 10⁻¹⁰ C"


def test_keeps_already_correct_negative_exponents_unchanged() -> None:
    source = "5.0 × 10⁻⁴ s and 8.5 × 10⁻¹⁰ C"

    assert normalise_scientific_text(source) == source


def test_export_cleaning_applies_final_negative_exponent_repair() -> None:
    cleaned = _clean_export_text(
        "contact duration 5.0 × 10–4 s; transferred charge 8.5 × 10–10 C"
    )

    assert "5.0 × 10⁻⁴ s" in cleaned
    assert "8.5 × 10⁻¹⁰ C" in cleaned
    assert "10–4" not in cleaned
    assert "10–10" not in cleaned
