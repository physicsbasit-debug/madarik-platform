from __future__ import annotations

import re

_SUPERSCRIPT_TRANSLATION = str.maketrans(
    {
        "-": "⁻",
        "+": "⁺",
        "0": "⁰",
        "1": "¹",
        "2": "²",
        "3": "³",
        "4": "⁴",
        "5": "⁵",
        "6": "⁶",
        "7": "⁷",
        "8": "⁸",
        "9": "⁹",
    }
)
_SUBSCRIPT_TRANSLATION = str.maketrans(
    {
        "0": "₀",
        "1": "₁",
        "2": "₂",
        "3": "₃",
        "4": "₄",
        "5": "₅",
        "6": "₆",
        "7": "₇",
        "8": "₈",
        "9": "₉",
    }
)

_MULTIPLICATION = r"[×xX]"
_DASH = r"[\-–−]"
_COEFFICIENT = r"[+-]?(?:\d+(?:\.\d+)?|\.\d+)"

_REVERSED_NEGATIVE_EXPONENT_PATTERNS = (
    re.compile(
        rf"(?<![\w.])(?P<exponent>\d{{1,2}})\s*{_DASH}\s*10\s*{_MULTIPLICATION}\s*(?P<coefficient>{_COEFFICIENT})(?![\w.])"
    ),
    re.compile(
        rf"(?<![\w.])10\s*{_DASH}\s*(?P<exponent>\d{{1,2}})\s*{_MULTIPLICATION}\s*(?P<coefficient>{_COEFFICIENT})(?![\w.])"
    ),
)
_REVERSED_POSITIVE_EXPONENT_PATTERN = re.compile(
    rf"(?<![\w.])10(?P<exponent>\d{{1,2}})\s*{_MULTIPLICATION}\s*(?P<coefficient>{_COEFFICIENT})(?![\w.])"
)
_BIDI_OR_SPACE = r"[\s\u200e\u200f\u202a-\u202e\u2066-\u2069]*"
_STANDARD_DASH_NEGATIVE_EXPONENT_PATTERN = re.compile(
    rf"(?<![\w.])(?P<coefficient>{_COEFFICIENT}){_BIDI_OR_SPACE}{_MULTIPLICATION}{_BIDI_OR_SPACE}10{_BIDI_OR_SPACE}{_DASH}{_BIDI_OR_SPACE}(?P<exponent>\d{{1,2}})(?![\w.])"
)
_STANDARD_ASCII_EXPONENT_PATTERN = re.compile(
    rf"(?<![\w.])(?P<coefficient>{_COEFFICIENT})\s*{_MULTIPLICATION}\s*10(?:\s*\^\s*(?P<signed_exponent>[+-]?\d{{1,2}})|\s*(?P<exponent>\d{{1,2}}))(?![\w.])"
)

# OCR generated from Symbol-encoded PDFs sometimes leaks the glyph code instead
# of the omega sign. Keep this narrowly scoped to the known sequence.
_OMEGA_GLYPH_CODE_PATTERN = re.compile(r"/g58", re.IGNORECASE)

# Nuclear notation is repaired only for valid element symbols and only when the
# second number is the larger mass number. This avoids rewriting ordinary labels.
_ELEMENT_SYMBOLS = {
    "H", "He", "Li", "Be", "B", "C", "N", "O", "F", "Ne", "Na", "Mg", "Al", "Si", "P", "S",
    "Cl", "Ar", "K", "Ca", "Sc", "Ti", "V", "Cr", "Mn", "Fe", "Co", "Ni", "Cu", "Zn", "Ga",
    "Ge", "As", "Se", "Br", "Kr", "Rb", "Sr", "Y", "Zr", "Nb", "Mo", "Tc", "Ru", "Rh", "Pd",
    "Ag", "Cd", "In", "Sn", "Sb", "Te", "I", "Xe", "Cs", "Ba", "La", "Ce", "Pr", "Nd", "Pm",
    "Sm", "Eu", "Gd", "Tb", "Dy", "Ho", "Er", "Tm", "Yb", "Lu", "Hf", "Ta", "W", "Re", "Os",
    "Ir", "Pt", "Au", "Hg", "Tl", "Pb", "Bi", "Po", "At", "Rn", "Fr", "Ra", "Ac", "Th", "Pa",
    "U", "Np", "Pu", "Am", "Cm", "Bk", "Cf", "Es", "Fm", "Md", "No", "Lr", "Rf", "Db", "Sg",
    "Bh", "Hs", "Mt", "Ds", "Rg", "Cn", "Nh", "Fl", "Mc", "Lv", "Ts", "Og",
}
_NUCLEAR_SUFFIX_PATTERN = re.compile(
    r"(?<![A-Za-z0-9])(?P<symbol>[A-Z][a-z]?)\s*(?P<atomic>\d{1,3})\s+(?P<mass>\d{2,3})(?!\d)"
)

_UNIT_POWER_PATTERN = re.compile(
    r"(?<![A-Za-z])(?P<unit>m|cm|mm)\s*(?P<power>[23])(?!\d)",
    re.IGNORECASE,
)
_FOCUS_INDEX_PATTERN = re.compile(r"\bF\s+([12])\b")

_SCIENTIFIC_RENDER_PATTERN = re.compile(
    r"(?<![\w.])[+-]?(?:\d+(?:\.\d+)?|\.\d+)\s*×\s*10[⁺⁻⁰¹²³⁴⁵⁶⁷⁸⁹]+(?:\s*(?:[A-Za-z]+|Ω)(?:\s*/\s*[A-Za-z]+[²³]?)?)?"
)
_NUCLEAR_RENDER_PATTERN = re.compile(
    r"[⁰¹²³⁴⁵⁶⁷⁸⁹]+[₀₁₂₃₄₅₆₇₈₉]+[A-Z][a-z]?"
)


def _superscript(value: str) -> str:
    return value.translate(_SUPERSCRIPT_TRANSLATION)


def _subscript(value: str) -> str:
    return value.translate(_SUBSCRIPT_TRANSLATION)


def _scientific_notation(coefficient: str, exponent: str) -> str:
    return f"{coefficient} × 10{_superscript(exponent)}"


def _replace_negative_reversed(match: re.Match[str]) -> str:
    return _scientific_notation(
        match.group("coefficient"),
        f"-{match.group('exponent')}",
    )


def _replace_positive_reversed(match: re.Match[str]) -> str:
    return _scientific_notation(
        match.group("coefficient"),
        match.group("exponent"),
    )


def _replace_standard_ascii(match: re.Match[str]) -> str:
    exponent = match.group("signed_exponent") or match.group("exponent")
    return _scientific_notation(match.group("coefficient"), exponent)


def _replace_nuclear_suffix(match: re.Match[str]) -> str:
    symbol = match.group("symbol")
    atomic = int(match.group("atomic"))
    mass = int(match.group("mass"))

    if symbol not in _ELEMENT_SYMBOLS or mass <= atomic:
        return match.group(0)

    return f"{_superscript(str(mass))}{_subscript(str(atomic))}{symbol}"


def normalise_scientific_text(value: str) -> str:
    """Repair deterministic OCR damage in scientific values before export.

    The function deliberately targets high-confidence corruption patterns seen in
    examination PDFs. It does not invent missing values or attempt to translate
    prose. Ambiguous text remains reviewable rather than being silently rewritten.
    """

    text = value or ""
    text = _OMEGA_GLYPH_CODE_PATTERN.sub("Ω", text)

    for pattern in _REVERSED_NEGATIVE_EXPONENT_PATTERNS:
        text = pattern.sub(_replace_negative_reversed, text)

    text = _REVERSED_POSITIVE_EXPONENT_PATTERN.sub(
        _replace_positive_reversed,
        text,
    )
    text = _STANDARD_DASH_NEGATIVE_EXPONENT_PATTERN.sub(
        lambda match: _scientific_notation(
            match.group("coefficient"),
            f"-{match.group('exponent')}",
        ),
        text,
    )
    text = _STANDARD_ASCII_EXPONENT_PATTERN.sub(
        _replace_standard_ascii,
        text,
    )
    text = _NUCLEAR_SUFFIX_PATTERN.sub(_replace_nuclear_suffix, text)
    text = _UNIT_POWER_PATTERN.sub(
        lambda match: f"{match.group('unit')}{_superscript(match.group('power'))}",
        text,
    )
    text = _FOCUS_INDEX_PATTERN.sub(
        lambda match: f"F{_subscript(match.group(1))}",
        text,
    )
    return text


def protect_scientific_bidi(value: str) -> str:
    """Wrap scientific spans with LRM so RTL rendering preserves their order."""

    text = value or ""

    def wrap(match: re.Match[str]) -> str:
        token = match.group(0)
        if token.startswith("\u200e") and token.endswith("\u200e"):
            return token
        return f"\u200e{token}\u200e"

    text = _SCIENTIFIC_RENDER_PATTERN.sub(wrap, text)
    text = _NUCLEAR_RENDER_PATTERN.sub(wrap, text)
    return text
