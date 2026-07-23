from __future__ import annotations

import re

_INVALID_FILENAME_CHARS = re.compile(r'[<>:"/\\|?*\x00-\x1F]+')
_RESERVED_WINDOWS_NAMES = {
    "CON", "PRN", "AUX", "NUL",
    *(f"COM{index}" for index in range(1, 10)),
    *(f"LPT{index}" for index in range(1, 10)),
}


def safe_filename_stem(value: str, fallback: str = "file", max_length: int = 90) -> str:
    """Return a filesystem-safe filename stem across Windows/macOS/Linux."""

    normalized = _INVALID_FILENAME_CHARS.sub("-", value.strip())
    normalized = re.sub(r"\s+", " ", normalized).strip(" .-")
    normalized = re.sub(r"-+", "-", normalized)
    if not normalized:
        normalized = fallback

    if normalized.upper() in _RESERVED_WINDOWS_NAMES:
        normalized = f"_{normalized}"

    normalized = normalized[:max_length].rstrip(" .-")
    return normalized or fallback
