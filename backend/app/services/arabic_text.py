"""Optional Arabic shaping helpers.

The production requirements include ``arabic-reshaper`` and ``python-bidi``.
The helpers degrade to Unicode logical-order text when those optional runtime
packages are unavailable, allowing non-PDF workflows and repository tests to
start instead of failing during module import.
"""

from __future__ import annotations

try:  # pragma: no cover - exercised when optional dependency is installed.
    import arabic_reshaper as _arabic_reshaper
except ImportError:  # pragma: no cover - environment-dependent fallback.
    _arabic_reshaper = None

try:  # pragma: no cover - exercised when optional dependency is installed.
    from bidi.algorithm import get_display as _get_display
except ImportError:  # pragma: no cover - environment-dependent fallback.
    _get_display = None


def reshape_arabic(text: str) -> str:
    if not text:
        return ""
    if _arabic_reshaper is None:
        return text
    return _arabic_reshaper.reshape(text)


def display_arabic(text: str) -> str:
    reshaped = reshape_arabic(text)
    if _get_display is None:
        return reshaped
    return _get_display(reshaped)
