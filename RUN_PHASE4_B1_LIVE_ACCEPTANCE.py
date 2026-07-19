#!/usr/bin/env python3
"""Optional live provider smoke test. Never prints API keys or raw provider payloads."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
BACKEND = ROOT / "backend"
if str(BACKEND) not in sys.path:
    sys.path.insert(0, str(BACKEND))

from app.services.ai_provider import (  # noqa: E402
    evaluate_provider_decision,
    translate_with_optional_external_provider,
    validate_arabic_translation_quality,
    validate_translation_fidelity,
)
from app.models.project import TranslationOutcomeStatus  # noqa: E402


def main() -> int:
    source = "Calculate V = IR when I = 2 A and R = 5 Ω. [2]"
    fallback = "احسب V = IR عندما تكون I = 2 A والمقاومة R = 5 Ω. [2]"
    decision = evaluate_provider_decision(source)

    print(f"provider={decision.provider}")
    print(f"decision={decision.reason}")
    if not decision.can_use_external:
        print("SKIP: external provider is not ready. Configure backend/.env and rerun.")
        return 0

    result = translate_with_optional_external_provider(
        original_text=source,
        glossary=[],
        fallback_translation=fallback,
    )
    quality = validate_arabic_translation_quality(source, result.translated_text)
    fidelity = validate_translation_fidelity(source, result.translated_text)

    print(f"outcome={result.outcome.value}")
    print(f"used_external_provider={result.used_external_provider}")
    print(f"arabic_quality={quality.is_compliant}")
    print(f"scientific_fidelity={fidelity.is_compliant}")

    accepted_outcomes = {
        TranslationOutcomeStatus.external_success,
        TranslationOutcomeStatus.corrected_success,
    }
    if (
        result.outcome not in accepted_outcomes
        or not result.used_external_provider
        or not quality.is_compliant
        or not fidelity.is_compliant
    ):
        print("FAIL: live provider did not pass Phase 4-B1 acceptance.")
        return 1

    print("PASS: live provider passed Phase 4-B1 smoke acceptance.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
