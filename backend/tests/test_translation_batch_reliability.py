from __future__ import annotations

from dataclasses import dataclass

from fastapi.testclient import TestClient

from app.main import app
from app.models.project import (
    ProjectSession,
    QuestionItem,
    QuestionPart,
    QuestionStatus,
    TranslationBatchStatus,
    TranslationBatchSummary,
    TranslationItemOutcome,
    TranslationItemType,
    TranslationOutcomeStatus,
)
from app.services.ai_provider import TranslationProviderResult
from app.services.readiness import build_project_readiness_report
from app.services.session_store import InMemoryProjectStore
from app.services.translation import (
    translate_questions_batch_with_glossary,
    translate_questions_with_glossary,
)


client = TestClient(app)


def _question(
    question_id: str,
    number: str,
    text: str,
    *,
    status: QuestionStatus = QuestionStatus.approved,
    translated_text: str = "",
    parts: list[QuestionPart] | None = None,
) -> QuestionItem:
    return QuestionItem(
        id=question_id,
        original_number=number,
        original_text=text,
        translated_text=translated_text,
        status=status,
        order_index=int(number) if number.isdigit() else 1,
        parts=parts or [],
    )


def test_phase4_a5_mixed_batch_continues_with_external_fallback_and_skip(monkeypatch):
    def fake_provider(original_text, glossary, *, context=None):
        if "resistance" in original_text:
            raise RuntimeError("provider exploded")
        return TranslationProviderResult(
            translated_text="اذكر وظيفة غشاء الخلية. [1]",
            provider="gemini",
            used_external_provider=True,
            note="external",
            outcome=TranslationOutcomeStatus.external_success,
        )

    monkeypatch.setattr(
        "app.services.translation._translate_text_with_provider",
        fake_provider,
    )

    questions = [
        _question("q-1", "1", "State the function of the cell membrane. [1]"),
        _question(
            "q-2",
            "2",
            "Explain why the current decreases when the resistance increases. [2]",
        ),
        _question(
            "q-3",
            "3",
            "Deleted question",
            status=QuestionStatus.deleted,
            translated_text="قديم",
        ),
    ]

    result = translate_questions_batch_with_glossary(questions, [])

    assert len(result.questions) == 3
    assert result.questions[0].translated_text.startswith("اذكر")
    assert result.questions[1].translated_text.startswith("فسّر")
    assert result.questions[2].translated_text == "قديم"
    assert result.summary.status == TranslationBatchStatus.completed_with_fallbacks
    assert result.summary.external_success_count == 1
    assert result.summary.local_fallback_count == 1
    assert result.summary.skipped_count == 1
    assert result.summary.failed_safely_count == 0
    assert result.summary.urgent_review_count == 1


def test_phase4_a5_corrected_success_has_its_own_batch_classification(monkeypatch):
    monkeypatch.setattr(
        "app.services.translation._translate_text_with_provider",
        lambda *args, **kwargs: TranslationProviderResult(
            translated_text="احسب V = IR عندما تكون I = 2 A. [2]",
            provider="gemini",
            used_external_provider=True,
            note="corrected",
            outcome=TranslationOutcomeStatus.corrected_success,
        ),
    )

    result = translate_questions_batch_with_glossary(
        [_question("q-corrected", "1", "Calculate V = IR when I = 2 A. [2]")],
        [],
    )

    assert result.summary.status == TranslationBatchStatus.completed
    assert result.summary.corrected_success_count == 1
    assert result.summary.external_success_count == 0
    assert result.summary.urgent_review_count == 0


def test_phase4_a5_multipart_failures_are_isolated_and_hierarchy_is_preserved(monkeypatch):
    def fake_provider(original_text, glossary, *, context=None):
        if "resistance" in original_text:
            raise TimeoutError("one part failed")
        return TranslationProviderResult(
            translated_text="اذكر وظيفة غشاء الخلية. [1]",
            provider="gemini",
            used_external_provider=True,
            note="external",
            outcome=TranslationOutcomeStatus.external_success,
        )

    monkeypatch.setattr(
        "app.services.translation._translate_text_with_provider",
        fake_provider,
    )

    question = _question(
        "q-parts-a5",
        "4",
        "Multipart",
        parts=[
            QuestionPart(
                id="heading",
                label="(a)",
                original_text="",
                translated_text="",
                order_index=1,
            ),
            QuestionPart(
                id="child",
                label="(i)",
                original_text="State the function of the cell membrane. [1]",
                translated_text="",
                parent_id="heading",
                order_index=2,
            ),
            QuestionPart(
                id="second",
                label="(b)",
                original_text=(
                    "Explain why the current decreases when the resistance "
                    "increases. [2]"
                ),
                translated_text="",
                order_index=3,
            ),
        ],
    )

    result = translate_questions_batch_with_glossary([question], [])
    translated = result.questions[0]

    assert [part.id for part in translated.parts] == ["heading", "child", "second"]
    assert translated.parts[1].parent_id == "heading"
    assert translated.parts[1].translated_text.startswith("اذكر")
    assert translated.parts[2].translated_text.startswith("فسّر")
    assert result.summary.total_items == 3
    assert result.summary.skipped_count == 1
    assert result.summary.external_success_count == 1
    assert result.summary.local_fallback_count == 1


def test_phase4_a5_failed_safely_preserves_existing_translation(monkeypatch):
    monkeypatch.setattr(
        "app.services.translation._translate_text_with_provider",
        lambda *args, **kwargs: (_ for _ in ()).throw(RuntimeError("provider")),
    )
    monkeypatch.setattr(
        "app.services.translation.translate_question_text",
        lambda *args, **kwargs: (_ for _ in ()).throw(ValueError("fallback")),
    )

    result = translate_questions_batch_with_glossary(
        [
            _question(
                "q-preserve",
                "1",
                "State the force. [1]",
                translated_text="ترجمة سابقة محفوظة.",
            )
        ],
        [],
    )

    assert result.questions[0].translated_text == "ترجمة سابقة محفوظة."
    assert result.summary.status == TranslationBatchStatus.completed_with_failures
    assert result.summary.failed_safely_count == 1
    assert result.summary.urgent_review_count == 1
    assert result.summary.items[0].status == TranslationOutcomeStatus.failed_safely


def test_phase4_a5_question_orchestration_error_does_not_abort_next_question(monkeypatch):
    original_builder = __import__(
        "app.services.translation",
        fromlist=["_build_combined_parts_translation"],
    )._build_combined_parts_translation

    def broken_builder(parts):
        if any(part.id == "break-me" for part in parts):
            raise KeyError("bad hierarchy")
        return original_builder(parts)

    monkeypatch.setattr(
        "app.services.translation._build_combined_parts_translation",
        broken_builder,
    )
    monkeypatch.setattr(
        "app.services.translation._translate_text_with_provider",
        lambda original_text, glossary, *, context=None: TranslationProviderResult(
            translated_text=f"ترجمة: {original_text}",
            provider="gemini",
            used_external_provider=True,
            outcome=TranslationOutcomeStatus.external_success,
        ),
    )

    questions = [
        _question(
            "q-broken",
            "1",
            "Broken multipart",
            parts=[
                QuestionPart(
                    id="break-me",
                    label="(a)",
                    original_text="State the force. [1]",
                    translated_text="",
                    order_index=1,
                )
            ],
        ),
        _question("q-good", "2", "State the unit of force. [1]"),
    ]

    result = translate_questions_batch_with_glossary(questions, [])

    assert len(result.questions) == 2
    assert result.summary.failed_safely_count == 1
    assert result.summary.external_success_count == 1
    assert result.questions[1].translated_text.startswith("ترجمة:")


def test_phase4_a5_deleted_question_never_calls_provider(monkeypatch):
    calls = 0

    def fail_if_called(*args, **kwargs):
        nonlocal calls
        calls += 1
        raise AssertionError("deleted question reached provider")

    monkeypatch.setattr(
        "app.services.translation._translate_text_with_provider",
        fail_if_called,
    )

    result = translate_questions_batch_with_glossary(
        [
            _question(
                "q-deleted",
                "1",
                "Deleted",
                status=QuestionStatus.deleted,
            )
        ],
        [],
    )

    assert calls == 0
    assert result.summary.skipped_count == 1
    assert result.summary.items[0].message.startswith("تم تجاوز السؤال المحذوف")


def test_phase4_a5_backward_wrapper_still_returns_question_list(monkeypatch):
    monkeypatch.setattr(
        "app.services.translation._translate_text_with_provider",
        lambda *args, **kwargs: TranslationProviderResult(
            translated_text="اذكر وحدة القوة. [1]",
            provider="gemini",
            used_external_provider=True,
            outcome=TranslationOutcomeStatus.external_success,
        ),
    )

    translated = translate_questions_with_glossary(
        [_question("q-wrapper", "1", "State the unit of force. [1]")],
        [],
    )

    assert isinstance(translated, list)
    assert translated[0].translated_text == "اذكر وحدة القوة. [1]"


def test_phase4_a5_old_project_payload_defaults_batch_summary_to_none():
    project = ProjectSession.model_validate(
        {
            "id": "legacy-project",
            "questions": [],
            "glossary": [],
        }
    )

    assert project.translation_batch_summary is None


@dataclass
class _MemoryRepository:
    saved: dict[str, ProjectSession]

    def save(self, project: ProjectSession) -> None:
        self.saved[project.id] = project.model_copy(deep=True)

    def load(self, project_id: str) -> ProjectSession | None:
        project = self.saved.get(project_id)
        return project.model_copy(deep=True) if project else None

    def delete(self, project_id: str) -> bool:
        return self.saved.pop(project_id, None) is not None

    def list_recent(self, limit=50, account_id=None, include_all=True):
        return list(self.saved.values())[:limit]


def test_phase4_a5_store_persists_summary_and_invalidates_it_after_question_edit():
    repository = _MemoryRepository(saved={})
    store = InMemoryProjectStore(repository=repository)
    project = store.create()
    question = _question("q-store", "1", "State the unit of force. [1]")
    summary = TranslationBatchSummary(
        status=TranslationBatchStatus.completed,
        total_questions=1,
        active_questions=1,
        total_items=1,
        external_success_count=1,
        items=[
            TranslationItemOutcome(
                question_id=question.id,
                question_number=question.original_number,
                item_type=TranslationItemType.question,
                status=TranslationOutcomeStatus.external_success,
                provider="gemini",
                used_external_provider=True,
            )
        ],
    )

    updated = store.set_translated_questions(
        project.id,
        [question],
        summary,
    )

    assert updated is not None
    assert updated.translation_batch_summary == summary

    from app.models.project import QuestionPatch

    edited = store.update_question(
        project.id,
        question.id,
        QuestionPatch(translated_text="تعديل يدوي"),
    )

    assert edited is not None
    assert edited.translation_batch_summary is None


def test_phase4_a5_translation_endpoint_returns_persisted_batch_summary(monkeypatch):
    monkeypatch.setattr(
        "app.services.translation._translate_text_with_provider",
        lambda *args, **kwargs: TranslationProviderResult(
            translated_text="اذكر وظيفة غشاء الخلية. [1]",
            provider="gemini",
            used_external_provider=True,
            outcome=TranslationOutcomeStatus.external_success,
        ),
    )

    project_id = client.post("/api/projects").json()["id"]
    client.post(f"/api/projects/{project_id}/demo-content")

    response = client.post(f"/api/projects/{project_id}/translate-questions")

    assert response.status_code == 200
    payload = response.json()
    summary = payload["translation_batch_summary"]
    assert summary["status"] == "completed"
    assert summary["total_questions"] == len(payload["questions"])
    assert summary["total_items"] >= 1
    assert summary["external_success_count"] >= 1


def test_phase4_a5_readiness_surfaces_batch_fallbacks_and_safe_failures():
    project = ProjectSession(
        id="readiness-a5",
        questions=[
            _question(
                "q-ready-a5",
                "1",
                "State the unit of force. [1]",
                translated_text="اذكر وحدة القوة. [1]",
            )
        ],
        translation_batch_summary=TranslationBatchSummary(
            status=TranslationBatchStatus.completed_with_failures,
            total_questions=1,
            active_questions=1,
            total_items=2,
            local_fallback_count=1,
            failed_safely_count=1,
            urgent_review_count=2,
        ),
    )

    report = build_project_readiness_report(project)
    codes = {issue.code for issue in report.issues}

    assert "translation_batch_local_fallbacks" in codes
    assert "translation_batch_failed_safely" in codes
