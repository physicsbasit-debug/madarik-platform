#!/usr/bin/env python3
"""Run a redacted live Gemini translation acceptance check.

The script never prints or stores API keys, provider payloads, prompts, or the
translated text. It emits only safe status metadata and hashes.
"""

from __future__ import annotations

import argparse
from collections.abc import Callable, Mapping
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import sys
from typing import Any
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parent
BACKEND = ROOT / "backend"
if str(BACKEND) not in sys.path:
    sys.path.insert(0, str(BACKEND))

from app.core.release import APP_VERSION, RELEASE_PHASE  # noqa: E402
from app.models.project import (  # noqa: E402
    GlossaryTerm,
    GlossaryTermSource,
    GlossaryTermStatus,
    TranslationOutcomeStatus,
)
from app.services.ai_provider import (  # noqa: E402
    ProviderDecision,
    TranslationPromptContext,
    TranslationProviderResult,
    evaluate_provider_decision,
    get_ai_provider_status,
    translate_with_optional_external_provider,
    validate_arabic_translation_quality,
    validate_glossary_compliance,
    validate_translation_fidelity,
)

EXPECTED_PROVIDER = "gemini"
EXPECTED_GEMINI_HOST = "generativelanguage.googleapis.com"
ACCEPTED_OUTCOMES = {
    TranslationOutcomeStatus.external_success,
    TranslationOutcomeStatus.corrected_success,
}
SOURCE_TEXT = (
    "Explain why the current decreases when the resistance increases in the "
    "circuit shown in Fig. 1.1. The potential difference is 5.0 V. [3]"
)
FALLBACK_SENTINEL = "ترجمة احتياطية محلية غير مقبولة لاختبار القبول الحي."
GLOSSARY = [
    GlossaryTerm(
        id="phase10c-current",
        english_term="current",
        arabic_term="التيار الكهربائي",
        subject="physics",
        status=GlossaryTermStatus.approved,
        source=GlossaryTermSource.manual,
    ),
    GlossaryTerm(
        id="phase10c-resistance",
        english_term="resistance",
        arabic_term="المقاومة الكهربائية",
        subject="physics",
        status=GlossaryTermStatus.approved,
        source=GlossaryTermSource.manual,
    ),
    GlossaryTerm(
        id="phase10c-potential-difference",
        english_term="potential difference",
        arabic_term="فرق الجهد الكهربائي",
        subject="physics",
        status=GlossaryTermStatus.approved,
        source=GlossaryTermSource.manual,
    ),
]
CONTEXT = TranslationPromptContext(
    subject="Physics",
    grade="10",
    semester="1",
    question_number="live-acceptance-1",
)

DecisionFunction = Callable[[str], ProviderDecision]
StatusFunction = Callable[[], dict[str, object]]
TranslateFunction = Callable[..., TranslationProviderResult]


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _safe_environment_summary(environment: Mapping[str, str]) -> dict[str, object]:
    base_url = environment.get("GEMINI_BASE_URL", "").strip()
    parsed = urlparse(base_url)
    return {
        "provider": environment.get("MADARIK_AI_PROVIDER", "").strip().lower(),
        "external_enabled": environment.get(
            "MADARIK_AI_EXTERNAL_ENABLED", ""
        ).strip().lower()
        in {"1", "true", "yes", "on"},
        "api_key_configured": bool(environment.get("GEMINI_API_KEY", "").strip()),
        "model": environment.get("GEMINI_MODEL", "").strip(),
        "base_url_scheme": parsed.scheme.lower(),
        "base_url_host": (parsed.hostname or "").lower(),
    }


def _configuration_failures(
    environment: Mapping[str, str],
) -> tuple[list[str], dict[str, object]]:
    summary = _safe_environment_summary(environment)
    failures: list[str] = []

    if summary["provider"] != EXPECTED_PROVIDER:
        failures.append("provider_not_gemini")
    if not summary["external_enabled"]:
        failures.append("external_provider_disabled")
    if not summary["api_key_configured"]:
        failures.append("gemini_api_key_missing")
    if not summary["model"]:
        failures.append("gemini_model_missing")
    if summary["base_url_scheme"] != "https":
        failures.append("gemini_base_url_must_use_https")
    if summary["base_url_host"] != EXPECTED_GEMINI_HOST:
        failures.append("gemini_base_url_host_not_official")

    return failures, summary


def run_live_acceptance(
    *,
    environment: Mapping[str, str] = os.environ,
    decision_function: DecisionFunction = evaluate_provider_decision,
    status_function: StatusFunction = get_ai_provider_status,
    translate_function: TranslateFunction = translate_with_optional_external_provider,
) -> tuple[int, dict[str, Any]]:
    """Run the live check and return an exit code plus a redacted report."""

    failures, environment_summary = _configuration_failures(environment)
    report: dict[str, Any] = {
        "schema_version": 1,
        "generated_at": _utc_now(),
        "application_version": APP_VERSION,
        "release_phase": RELEASE_PHASE,
        "gate": "phase10-c-live-gemini-acceptance",
        "status": "failed",
        "environment": environment_summary,
        "source_sha256": _sha256_text(SOURCE_TEXT),
        "source_character_count": len(SOURCE_TEXT),
        "glossary_term_count": len(GLOSSARY),
        "redaction": {
            "api_key_stored": False,
            "source_text_stored": False,
            "translated_text_stored": False,
            "provider_payload_stored": False,
            "prompt_stored": False,
        },
        "failures": failures,
    }

    if failures:
        return 1, report

    try:
        provider_status = status_function()
        decision = decision_function(SOURCE_TEXT)
    except Exception as exc:  # pragma: no cover - defensive runtime guard
        report["failures"].append(
            f"provider_preflight_exception:{exc.__class__.__name__}"
        )
        return 1, report

    report["provider_preflight"] = {
        "provider": str(provider_status.get("provider", "")),
        "configured": bool(provider_status.get("configured", False)),
        "external_enabled": bool(
            provider_status.get("external_enabled", False)
        ),
        "ready": bool(provider_status.get("ready", False)),
        "reason": str(provider_status.get("reason", "")),
        "model": str(provider_status.get("model", "")),
        "api_mode": str(provider_status.get("api_mode", "")),
        "base_url_configured": bool(
            provider_status.get("base_url_configured", False)
        ),
        "prompt_version": str(provider_status.get("prompt_version", "")),
        "decision_provider": decision.provider,
        "decision_reason": decision.reason,
        "decision_can_use_external": decision.can_use_external,
    }

    if decision.provider != EXPECTED_PROVIDER:
        report["failures"].append("provider_decision_not_gemini")
    if not decision.can_use_external:
        report["failures"].append(
            f"provider_decision_blocked:{decision.reason}"
        )
    if report["failures"]:
        return 1, report

    try:
        result = translate_function(
            original_text=SOURCE_TEXT,
            glossary=GLOSSARY,
            fallback_translation=FALLBACK_SENTINEL,
            context=CONTEXT,
        )
    except Exception as exc:  # pragma: no cover - live runtime guard
        report["failures"].append(
            f"translation_exception:{exc.__class__.__name__}"
        )
        return 1, report

    translated_text = result.translated_text or ""
    quality = validate_arabic_translation_quality(
        SOURCE_TEXT,
        translated_text,
    )
    fidelity = validate_translation_fidelity(
        SOURCE_TEXT,
        translated_text,
    )
    glossary = validate_glossary_compliance(
        SOURCE_TEXT,
        translated_text,
        GLOSSARY,
    )

    report["translation"] = {
        "provider": result.provider,
        "outcome": result.outcome.value,
        "used_external_provider": result.used_external_provider,
        "translated_text_sha256": _sha256_text(translated_text),
        "translated_character_count": len(translated_text),
        "arabic_quality": quality.is_compliant,
        "arabic_letter_ratio": quality.arabic_letter_ratio,
        "unexplained_latin_word_count": len(
            quality.unexplained_latin_words
        ),
        "scientific_fidelity": fidelity.is_compliant,
        "protected_token_count": len(fidelity.protected_tokens),
        "missing_protected_token_count": len(fidelity.missing_tokens),
        "glossary_compliance": glossary.is_compliant,
        "applicable_glossary_term_count": len(glossary.applicable_terms),
        "missing_glossary_term_count": len(glossary.missing_terms),
        "correction_used": (
            result.outcome is TranslationOutcomeStatus.corrected_success
        ),
        "fallback_detected": (
            not result.used_external_provider
            or result.outcome is TranslationOutcomeStatus.local_fallback
            or translated_text.strip() == FALLBACK_SENTINEL
        ),
    }

    if result.provider != EXPECTED_PROVIDER:
        report["failures"].append("translation_provider_not_gemini")
    if not result.used_external_provider:
        report["failures"].append("external_provider_not_used")
    if result.outcome not in ACCEPTED_OUTCOMES:
        report["failures"].append(
            f"translation_outcome_not_accepted:{result.outcome.value}"
        )
    if translated_text.strip() == FALLBACK_SENTINEL:
        report["failures"].append("fallback_sentinel_returned")
    if not quality.is_compliant:
        report["failures"].append("arabic_quality_failed")
    if not fidelity.is_compliant:
        report["failures"].append("scientific_fidelity_failed")
    if not glossary.is_compliant:
        report["failures"].append("glossary_compliance_failed")

    if not report["failures"]:
        report["status"] = "passed"
        return 0, report
    return 1, report


def _write_report(path: Path, report: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def _print_safe_summary(report: dict[str, Any]) -> None:
    print("=== Phase 10-C Live Gemini Acceptance ===")
    print(f"status={report.get('status', 'failed')}")
    environment = report.get("environment", {})
    print(f"provider={environment.get('provider', '')}")
    print(f"model={environment.get('model', '')}")
    preflight = report.get("provider_preflight", {})
    if preflight:
        print(f"provider_ready={preflight.get('ready', False)}")
        print(f"decision={preflight.get('decision_reason', '')}")
    translation = report.get("translation", {})
    if translation:
        print(f"outcome={translation.get('outcome', '')}")
        print(
            "used_external_provider="
            f"{translation.get('used_external_provider', False)}"
        )
        print(f"arabic_quality={translation.get('arabic_quality', False)}")
        print(
            "scientific_fidelity="
            f"{translation.get('scientific_fidelity', False)}"
        )
        print(
            "glossary_compliance="
            f"{translation.get('glossary_compliance', False)}"
        )
    failures = report.get("failures", [])
    print(f"failure_count={len(failures)}")
    for failure in failures:
        print(f"failure={failure}")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run a redacted live Gemini acceptance test.",
    )
    parser.add_argument(
        "--json-output",
        type=Path,
        required=True,
        help="Path for the redacted JSON evidence report.",
    )
    args = parser.parse_args()

    exit_code, report = run_live_acceptance()
    _write_report(args.json_output, report)
    _print_safe_summary(report)
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
