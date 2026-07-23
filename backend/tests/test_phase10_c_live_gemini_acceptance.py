from __future__ import annotations

import importlib.util
import json
from pathlib import Path

from app.models.project import TranslationOutcomeStatus
from app.services.ai_provider import (
    ProviderDecision,
    TranslationProviderResult,
)


ROOT = Path(__file__).resolve().parents[2]
SCRIPT_PATH = ROOT / "RUN_PHASE10_C_LIVE_GEMINI_ACCEPTANCE.py"
SPEC = importlib.util.spec_from_file_location(
    "phase10_c_live_gemini_acceptance",
    SCRIPT_PATH,
)
assert SPEC is not None and SPEC.loader is not None
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def _environment() -> dict[str, str]:
    return {
        "MADARIK_AI_PROVIDER": "gemini",
        "MADARIK_AI_EXTERNAL_ENABLED": "true",
        "GEMINI_API_KEY": "test-secret-never-exported",
        "GEMINI_MODEL": "gemini-test-model",
        "GEMINI_BASE_URL": (
            "https://generativelanguage.googleapis.com/v1beta"
        ),
    }


def _status() -> dict[str, object]:
    return {
        "provider": "gemini",
        "configured": True,
        "external_enabled": True,
        "ready": True,
        "reason": "ready",
        "model": "gemini-test-model",
        "api_mode": "generate_content",
        "base_url_configured": True,
        "prompt_version": "test-prompt",
    }


def _decision(_: str) -> ProviderDecision:
    return ProviderDecision(
        provider="gemini",
        can_use_external=True,
        reason="ready",
        fallback="none",
    )


def _success_translation(**_: object) -> TranslationProviderResult:
    return TranslationProviderResult(
        translated_text=(
            "فسّر لماذا ينخفض التيار الكهربائي عندما تزداد المقاومة "
            "الكهربائية في الدائرة الموضحة في الشكل Fig. 1.1، عندما "
            "يكون فرق الجهد الكهربائي 5.0 V. [3]"
        ),
        provider="gemini",
        used_external_provider=True,
        note="safe provider note",
        outcome=TranslationOutcomeStatus.external_success,
    )


def test_live_gate_passes_only_for_external_compliant_result() -> None:
    exit_code, report = MODULE.run_live_acceptance(
        environment=_environment(),
        decision_function=_decision,
        status_function=_status,
        translate_function=_success_translation,
    )

    assert exit_code == 0
    assert report["status"] == "passed"
    assert report["failures"] == []
    assert report["translation"]["used_external_provider"] is True
    assert report["translation"]["arabic_quality"] is True
    assert report["translation"]["scientific_fidelity"] is True
    assert report["translation"]["glossary_compliance"] is True


def test_live_gate_rejects_local_fallback() -> None:
    def fallback(**_: object) -> TranslationProviderResult:
        return TranslationProviderResult(
            translated_text=MODULE.FALLBACK_SENTINEL,
            provider="mock",
            used_external_provider=False,
            note="fallback",
            outcome=TranslationOutcomeStatus.local_fallback,
        )

    exit_code, report = MODULE.run_live_acceptance(
        environment=_environment(),
        decision_function=_decision,
        status_function=_status,
        translate_function=fallback,
    )

    assert exit_code == 1
    assert report["status"] == "failed"
    assert "external_provider_not_used" in report["failures"]
    assert "fallback_sentinel_returned" in report["failures"]


def test_live_gate_rejects_non_official_gemini_base_url() -> None:
    environment = _environment()
    environment["GEMINI_BASE_URL"] = "https://example.invalid/v1beta"
    called = False

    def must_not_call(**_: object) -> TranslationProviderResult:
        nonlocal called
        called = True
        return _success_translation()

    exit_code, report = MODULE.run_live_acceptance(
        environment=environment,
        decision_function=_decision,
        status_function=_status,
        translate_function=must_not_call,
    )

    assert exit_code == 1
    assert called is False
    assert "gemini_base_url_host_not_official" in report["failures"]


def test_report_is_redacted() -> None:
    environment = _environment()
    exit_code, report = MODULE.run_live_acceptance(
        environment=environment,
        decision_function=_decision,
        status_function=_status,
        translate_function=_success_translation,
    )

    assert exit_code == 0
    serialized = json.dumps(report, ensure_ascii=False)
    assert environment["GEMINI_API_KEY"] not in serialized
    assert _success_translation().translated_text not in serialized
    assert MODULE.SOURCE_TEXT not in serialized
    assert "translated_text_sha256" in serialized
    assert report["environment"]["api_key_configured"] is True
    assert "provider_note" not in report["translation"]
    assert "safe provider note" not in serialized
    assert report["redaction"] == {
        "api_key_stored": False,
        "source_text_stored": False,
        "translated_text_stored": False,
        "provider_payload_stored": False,
        "prompt_stored": False,
    }



def test_live_gate_accepts_one_successful_correction() -> None:
    def corrected(**_: object) -> TranslationProviderResult:
        result = _success_translation()
        return TranslationProviderResult(
            translated_text=result.translated_text,
            provider="gemini",
            used_external_provider=True,
            note="corrected safely",
            outcome=TranslationOutcomeStatus.corrected_success,
        )

    exit_code, report = MODULE.run_live_acceptance(
        environment=_environment(),
        decision_function=_decision,
        status_function=_status,
        translate_function=corrected,
    )

    assert exit_code == 0
    assert report["status"] == "passed"
    assert report["translation"]["correction_used"] is True
    assert report["translation"]["fallback_detected"] is False


def test_live_gate_rejects_missing_api_key_before_provider_call() -> None:
    environment = _environment()
    environment["GEMINI_API_KEY"] = ""
    called = False

    def must_not_call(**_: object) -> TranslationProviderResult:
        nonlocal called
        called = True
        return _success_translation()

    exit_code, report = MODULE.run_live_acceptance(
        environment=environment,
        decision_function=_decision,
        status_function=_status,
        translate_function=must_not_call,
    )

    assert exit_code == 1
    assert called is False
    assert "gemini_api_key_missing" in report["failures"]
    assert report["environment"]["api_key_configured"] is False


def test_live_workflow_is_secret_scoped_and_not_pr_triggered() -> None:
    workflow = (
        ROOT / ".github/workflows/phase10-c-live-gemini.yml"
    ).read_text(encoding="utf-8")

    assert "name: Phase 10-C Live Gemini Acceptance" in workflow
    assert "pull_request:" not in workflow
    assert "secrets.GEMINI_API_KEY" in workflow
    assert "secrets.GEMINI_MODEL" in workflow
    assert "secrets.GEMINI_BASE_URL" in workflow
    assert "RUN_PHASE10_C_LIVE_GEMINI_ACCEPTANCE.py" in workflow
    assert "actions/upload-artifact@v4" in workflow
    assert "echo $GEMINI_API_KEY" not in workflow
    assert "cat $GEMINI_API_KEY" not in workflow
