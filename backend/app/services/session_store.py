from datetime import datetime, timezone
from uuid import uuid4

from app.models.project import (
    AnswerKeyItem,
    EducationalAnalysisReport,
    EducationalQualityToolsReport,
    FullExamEndToEndReport,
    FullExamExportReport,
    FullExamIntakeReport,
    FullExamTranslationReport,
    GlossaryTermPatch,
    StepKey,
    ProjectMetadata,
    ProjectSession,
    PdfLayoutAssetInfo,
    QuestionPatch,
    ExtractedTextInfo,
    UploadedFileInfo,
    ProjectLogoInfo,
    QuestionItem,
    GlossaryTerm,
    QuestionAssetInfo,
    QuestionStatus,
    TranslationBatchSummary,
)
from app.services.demo_content import get_demo_glossary, get_demo_questions
from app.services.full_exam_intake import (
    build_full_exam_intake_report,
    link_layout_assets_to_page_aware_questions,
)
from app.services.full_exam_translation import (
    build_full_exam_translation_report,
)
from app.services.project_repository import ProjectRepository, project_repository


class InMemoryProjectStore:
    """Tiny in-memory store for early project sessions.

    This is deliberately temporary. Persistent drafts are deferred to later phases.
    """

    def __init__(self, repository: ProjectRepository | None = None) -> None:
        self._projects: dict[str, ProjectSession] = {}
        self._repository = repository or project_repository

    def create(self, metadata: ProjectMetadata | None = None, owner_account_id: str | None = None) -> ProjectSession:
        project = ProjectSession(metadata=metadata or ProjectMetadata(), owner_account_id=owner_account_id)
        self._projects[project.id] = project
        self._repository.save(project)
        return project


    def import_snapshot(self, snapshot: ProjectSession, owner_account_id: str | None = None) -> ProjectSession:
        """Import a user-provided project snapshot as a new temporary project.

        The snapshot receives a fresh project id to avoid collisions with any
        currently-open in-memory session. This is not server-side persistence; it
        is a local JSON handoff that lets the teacher survive reloads, browser
        drama, and the ancient curse of unsaved work.
        """

        now = datetime.now(timezone.utc)
        project = snapshot.model_copy(
            update={
                "id": str(uuid4()),
                "created_at": now,
                "updated_at": now,
                "owner_account_id": owner_account_id,
                "full_exam_export_report": None,
                "full_exam_end_to_end_report": None,
            },
            deep=True,
        )
        self._projects[project.id] = project
        self._repository.save(project)
        return project

    def get(self, project_id: str) -> ProjectSession | None:
        cached = self._projects.get(project_id)
        if cached is not None:
            return cached

        persisted = self._repository.load(project_id)
        if persisted is not None:
            self._projects[project_id] = persisted
        return persisted

    def delete(self, project_id: str) -> bool:
        existed_in_memory = self._projects.pop(project_id, None) is not None
        existed_in_repository = self._repository.delete(project_id)
        return existed_in_memory or existed_in_repository

    def touch(self, project_id: str) -> ProjectSession | None:
        project = self.get(project_id)
        if project is None:
            return None
        project.updated_at = datetime.now(timezone.utc)
        self._repository.save(project)
        return project


    @staticmethod
    def _invalidate_full_exam_end_to_end_report(
        project: ProjectSession,
    ) -> None:
        project.full_exam_end_to_end_report = None

    @staticmethod
    def _invalidate_full_exam_export_report(project: ProjectSession) -> None:
        project.full_exam_export_report = None
        InMemoryProjectStore._invalidate_full_exam_end_to_end_report(project)

    @staticmethod
    def _refresh_full_exam_translation_report(
        project: ProjectSession,
        summary: TranslationBatchSummary | None = None,
    ) -> None:
        InMemoryProjectStore._invalidate_full_exam_export_report(project)
        if not project.questions:
            project.full_exam_translation_report = None
            return

        project.full_exam_translation_report = (
            build_full_exam_translation_report(
                project.questions,
                project.glossary,
                summary,
                project.full_exam_intake_report,
            )
        )

    def update_metadata(self, project_id: str, metadata: ProjectMetadata) -> ProjectSession | None:
        project = self.get(project_id)
        if project is None:
            return None
        previous_metadata = project.metadata
        only_marks_policy_changed = (
            previous_metadata.model_dump(exclude={"marks_policy"})
            == metadata.model_dump(exclude={"marks_policy"})
        )

        project.metadata = metadata
        self._invalidate_full_exam_export_report(project)

        if not only_marks_policy_changed:
            project.translation_batch_summary = None
            project.full_exam_translation_report = None
            project.current_step = StepKey.setup

        return self.touch(project_id)

    def set_uploaded_file(self, project_id: str, uploaded_file: UploadedFileInfo | None) -> ProjectSession | None:
        project = self.get(project_id)
        if project is None:
            return None
        project.uploaded_file = uploaded_file
        project.translation_batch_summary = None
        self._invalidate_full_exam_export_report(project)
        project.full_exam_intake_report = None
        project.full_exam_translation_report = None
        if uploaded_file is None:
            project.extracted_text = None
        project.current_step = StepKey.upload
        return self.touch(project_id)

    def set_school_logo(self, project_id: str, school_logo: ProjectLogoInfo | None) -> ProjectSession | None:
        project = self.get(project_id)
        if project is None:
            return None
        project.school_logo = school_logo
        self._invalidate_full_exam_export_report(project)
        project.current_step = StepKey.setup
        return self.touch(project_id)

    def set_extracted_text(
        self,
        project_id: str,
        uploaded_file: UploadedFileInfo,
        extracted_text: ExtractedTextInfo,
        full_exam_intake_report: FullExamIntakeReport | None = None,
    ) -> ProjectSession | None:
        project = self.get(project_id)
        if project is None:
            return None
        project.uploaded_file = uploaded_file
        project.extracted_text = extracted_text
        project.translation_batch_summary = None
        self._invalidate_full_exam_export_report(project)
        project.full_exam_intake_report = full_exam_intake_report
        project.full_exam_translation_report = None
        project.current_step = StepKey.extract
        return self.touch(project_id)

    def load_demo_content(self, project_id: str) -> ProjectSession | None:
        project = self.get(project_id)
        if project is None:
            return None
        project.questions = get_demo_questions()
        project.glossary = get_demo_glossary()
        project.translation_batch_summary = None
        project.full_exam_intake_report = None
        self._refresh_full_exam_translation_report(project)
        project.current_step = StepKey.extract
        return self.touch(project_id)


    def set_parsed_questions(
        self,
        project_id: str,
        questions: list[QuestionItem],
        full_exam_intake_report: FullExamIntakeReport | None = None,
    ) -> ProjectSession | None:
        project = self.get(project_id)
        if project is None:
            return None
        project.questions = questions
        project.translation_batch_summary = None
        project.full_exam_intake_report = full_exam_intake_report
        self._refresh_full_exam_translation_report(project)
        project.current_step = StepKey.review
        return self.touch(project_id)


    def set_glossary(self, project_id: str, glossary: list[GlossaryTerm]) -> ProjectSession | None:
        project = self.get(project_id)
        if project is None:
            return None
        project.glossary = glossary
        project.translation_batch_summary = None
        self._refresh_full_exam_translation_report(project)
        project.current_step = StepKey.glossary
        return self.touch(project_id)

    def set_layout_assets(self, project_id: str, layout_assets: list[PdfLayoutAssetInfo]) -> ProjectSession | None:
        project = self.get(project_id)
        if project is None:
            return None

        valid_asset_ids = {asset.id for asset in layout_assets}
        project.layout_assets = layout_assets
        project.questions = [
            question.model_copy(
                update={
                    "linked_layout_asset_ids": [
                        asset_id
                        for asset_id in question.linked_layout_asset_ids
                        if asset_id in valid_asset_ids
                    ]
                }
            )
            for question in project.questions
        ]
        project.questions = link_layout_assets_to_page_aware_questions(
            project.questions,
            layout_assets,
        )
        if project.extracted_text and project.extracted_text.pages:
            project.full_exam_intake_report = build_full_exam_intake_report(
                project.extracted_text.pages,
                questions=project.questions,
            )
        self._refresh_full_exam_translation_report(
            project,
            project.translation_batch_summary,
        )
        project.current_step = StepKey.extract
        return self.touch(project_id)

    def remove_layout_asset(self, project_id: str, asset_id: str) -> ProjectSession | None:
        project = self.get(project_id)
        if project is None:
            return None

        remaining_assets = [
            asset for asset in project.layout_assets
            if asset.id != asset_id
        ]
        if len(remaining_assets) == len(project.layout_assets):
            return None

        project.layout_assets = remaining_assets
        project.questions = [
            question.model_copy(
                update={
                    "linked_layout_asset_ids": [
                        linked_id
                        for linked_id in question.linked_layout_asset_ids
                        if linked_id != asset_id
                    ]
                }
            )
            for question in project.questions
        ]
        if project.extracted_text and project.extracted_text.pages:
            project.full_exam_intake_report = build_full_exam_intake_report(
                project.extracted_text.pages,
                questions=project.questions,
            )
        self._refresh_full_exam_translation_report(
            project,
            project.translation_batch_summary,
        )
        project.current_step = StepKey.extract
        return self.touch(project_id)

    def link_layout_asset_to_question(
        self,
        project_id: str,
        question_id: str,
        asset_id: str,
    ) -> ProjectSession | None:
        project = self.get(project_id)
        if project is None:
            return None

        if asset_id not in {asset.id for asset in project.layout_assets}:
            return None

        for index, question in enumerate(project.questions):
            if question.id != question_id:
                continue

            if asset_id in question.linked_layout_asset_ids:
                return project

            project.questions[index] = question.model_copy(
                update={
                    "linked_layout_asset_ids": [
                        *question.linked_layout_asset_ids,
                        asset_id,
                    ]
                }
            )
            if project.extracted_text and project.extracted_text.pages:
                project.full_exam_intake_report = build_full_exam_intake_report(
                    project.extracted_text.pages,
                    questions=project.questions,
                )
            self._refresh_full_exam_translation_report(
                project,
                project.translation_batch_summary,
            )
            project.current_step = StepKey.review
            return self.touch(project_id)

        return None

    def unlink_layout_asset_from_question(
        self,
        project_id: str,
        question_id: str,
        asset_id: str,
    ) -> ProjectSession | None:
        project = self.get(project_id)
        if project is None:
            return None

        for index, question in enumerate(project.questions):
            if question.id != question_id:
                continue

            if asset_id not in question.linked_layout_asset_ids:
                return None

            project.questions[index] = question.model_copy(
                update={
                    "linked_layout_asset_ids": [
                        linked_id
                        for linked_id in question.linked_layout_asset_ids
                        if linked_id != asset_id
                    ]
                }
            )
            if project.extracted_text and project.extracted_text.pages:
                project.full_exam_intake_report = build_full_exam_intake_report(
                    project.extracted_text.pages,
                    questions=project.questions,
                )
            self._refresh_full_exam_translation_report(
                project,
                project.translation_batch_summary,
            )
            project.current_step = StepKey.review
            return self.touch(project_id)

        return None

    def set_translated_questions(
        self,
        project_id: str,
        questions: list[QuestionItem],
        summary: TranslationBatchSummary | None = None,
        full_exam_translation_report: FullExamTranslationReport | None = None,
    ) -> ProjectSession | None:
        project = self.get(project_id)
        if project is None:
            return None
        project.questions = questions
        project.translation_batch_summary = summary
        self._invalidate_full_exam_export_report(project)
        project.full_exam_translation_report = (
            full_exam_translation_report
        )
        if project.full_exam_translation_report is None:
            self._refresh_full_exam_translation_report(project, summary)
        project.current_step = StepKey.review
        return self.touch(project_id)

    def update_question(self, project_id: str, question_id: str, patch: QuestionPatch) -> ProjectSession | None:
        project = self.get(project_id)
        if project is None:
            return None

        for index, question in enumerate(project.questions):
            if question.id == question_id:
                update_data = patch.model_dump(exclude_unset=True)
                if "parts" in patch.model_fields_set:
                    update_data["parts"] = patch.parts or []
                project.questions[index] = question.model_copy(update=update_data)
                project.translation_batch_summary = None
                self._refresh_full_exam_translation_report(project)
                project.current_step = StepKey.review
                return self.touch(project_id)
        return None


    def bulk_update_question_status(
        self,
        project_id: str,
        status: QuestionStatus,
        include_deleted: bool = False,
    ) -> ProjectSession | None:
        project = self.get(project_id)
        if project is None:
            return None

        updated_questions: list[QuestionItem] = []
        for question in project.questions:
            if question.status == QuestionStatus.deleted and not include_deleted:
                updated_questions.append(question)
                continue
            updated_questions.append(question.model_copy(update={"status": status}))

        project.questions = updated_questions
        project.translation_batch_summary = None
        self._refresh_full_exam_translation_report(project)
        project.current_step = StepKey.review
        return self.touch(project_id)

    def reorder_questions(self, project_id: str, ordered_question_ids: list[str]) -> ProjectSession | None:
        project = self.get(project_id)
        if project is None:
            return None

        existing_ids = {question.id for question in project.questions}
        if set(ordered_question_ids) != existing_ids:
            return None

        order_lookup = {question_id: position + 1 for position, question_id in enumerate(ordered_question_ids)}
        project.questions = [
            question.model_copy(update={"order_index": order_lookup[question.id]}) for question in project.questions
        ]
        self._refresh_full_exam_translation_report(
            project,
            project.translation_batch_summary,
        )
        project.current_step = StepKey.review
        return self.touch(project_id)

    def add_question_asset(self, project_id: str, question_id: str, asset: QuestionAssetInfo) -> ProjectSession | None:
        project = self.get(project_id)
        if project is None:
            return None

        for index, question in enumerate(project.questions):
            if question.id == question_id:
                note = question.attachment_note or "تم ربط صورة/جدول بهذا السؤال للمراجعة والتصدير."
                project.questions[index] = question.model_copy(
                    update={
                        "attachments": [*question.attachments, asset],
                        "attachment_note": note,
                    }
                )
                self._invalidate_full_exam_export_report(project)
                project.current_step = StepKey.review
                return self.touch(project_id)
        return None

    def remove_question_asset(self, project_id: str, question_id: str, asset_id: str) -> ProjectSession | None:
        project = self.get(project_id)
        if project is None:
            return None

        for index, question in enumerate(project.questions):
            if question.id == question_id:
                remaining_assets = [asset for asset in question.attachments if asset.id != asset_id]
                if len(remaining_assets) == len(question.attachments):
                    return None
                note = question.attachment_note
                if not remaining_assets and note == "تم ربط صورة/جدول بهذا السؤال للمراجعة والتصدير.":
                    note = None
                project.questions[index] = question.model_copy(
                    update={
                        "attachments": remaining_assets,
                        "attachment_note": note,
                    }
                )
                self._invalidate_full_exam_export_report(project)
                project.current_step = StepKey.review
                return self.touch(project_id)
        return None

    def update_glossary_term(self, project_id: str, term_id: str, patch: GlossaryTermPatch) -> ProjectSession | None:
        project = self.get(project_id)
        if project is None:
            return None

        for index, term in enumerate(project.glossary):
            if term.id == term_id:
                update_data = patch.model_dump(exclude_unset=True)
                project.glossary[index] = term.model_copy(update=update_data)
                project.translation_batch_summary = None
                self._refresh_full_exam_translation_report(project)
                project.current_step = StepKey.glossary
                return self.touch(project_id)
        return None

    def set_full_exam_export_report(
        self,
        project_id: str,
        report: FullExamExportReport,
    ) -> ProjectSession | None:
        project = self.get(project_id)
        if project is None:
            return None
        self._invalidate_full_exam_end_to_end_report(project)
        project.full_exam_export_report = report
        project.current_step = StepKey.export
        return self.touch(project_id)

    def set_full_exam_end_to_end_result(
        self,
        project_id: str,
        *,
        intake_report: FullExamIntakeReport | None,
        translation_report: FullExamTranslationReport | None,
        export_report: FullExamExportReport | None,
        end_to_end_report: FullExamEndToEndReport,
    ) -> ProjectSession | None:
        """Persist one internally consistent Phase 4-A6d gate result."""

        project = self.get(project_id)
        if project is None:
            return None
        project.full_exam_intake_report = intake_report
        project.full_exam_translation_report = translation_report
        project.full_exam_export_report = export_report
        project.full_exam_end_to_end_report = end_to_end_report
        project.current_step = StepKey.export
        return self.touch(project_id)


    def set_answer_key(self, project_id: str, answer_key: list[AnswerKeyItem]) -> ProjectSession | None:
        project = self.get(project_id)
        if project is None:
            return None
        project.answer_key = answer_key
        project.current_step = StepKey.export
        return self.touch(project_id)

    def clear_answer_key(self, project_id: str) -> ProjectSession | None:
        project = self.get(project_id)
        if project is None:
            return None
        project.answer_key = []
        project.current_step = StepKey.export
        return self.touch(project_id)

    def set_educational_analysis(self, project_id: str, analysis: EducationalAnalysisReport) -> ProjectSession | None:
        project = self.get(project_id)
        if project is None:
            return None
        project.educational_analysis = analysis
        project.current_step = StepKey.export
        return self.touch(project_id)

    def clear_educational_analysis(self, project_id: str) -> ProjectSession | None:
        project = self.get(project_id)
        if project is None:
            return None
        project.educational_analysis = None
        project.current_step = StepKey.export
        return self.touch(project_id)

    def set_quality_tools(self, project_id: str, quality_tools: EducationalQualityToolsReport) -> ProjectSession | None:
        project = self.get(project_id)
        if project is None:
            return None
        project.quality_tools = quality_tools
        project.current_step = StepKey.export
        return self.touch(project_id)

    def clear_quality_tools(self, project_id: str) -> ProjectSession | None:
        project = self.get(project_id)
        if project is None:
            return None
        project.quality_tools = None
        project.current_step = StepKey.export
        return self.touch(project_id)

    def list_recent(self, limit: int = 50, account_id: str | None = None, include_all: bool = True) -> list[ProjectSession]:
        projects = self._repository.list_recent(limit, account_id=account_id, include_all=include_all)
        for project in projects:
            self._projects[project.id] = project
        return projects


project_store = InMemoryProjectStore()
