from datetime import datetime, timezone

from app.models.project import (
    GlossaryTermPatch,
    StepKey,
    ProjectMetadata,
    ProjectSession,
    QuestionPatch,
    ExtractedTextInfo,
    UploadedFileInfo,
    QuestionItem,
)
from app.services.demo_content import get_demo_glossary, get_demo_questions


class InMemoryProjectStore:
    """Tiny in-memory store for early project sessions.

    This is deliberately temporary. Persistent drafts are deferred to later phases.
    """

    def __init__(self) -> None:
        self._projects: dict[str, ProjectSession] = {}

    def create(self, metadata: ProjectMetadata | None = None) -> ProjectSession:
        project = ProjectSession(metadata=metadata or ProjectMetadata())
        self._projects[project.id] = project
        return project

    def get(self, project_id: str) -> ProjectSession | None:
        return self._projects.get(project_id)

    def delete(self, project_id: str) -> bool:
        return self._projects.pop(project_id, None) is not None

    def touch(self, project_id: str) -> ProjectSession | None:
        project = self.get(project_id)
        if project is None:
            return None
        project.updated_at = datetime.now(timezone.utc)
        return project

    def update_metadata(self, project_id: str, metadata: ProjectMetadata) -> ProjectSession | None:
        project = self.get(project_id)
        if project is None:
            return None
        project.metadata = metadata
        project.current_step = StepKey.setup
        return self.touch(project_id)

    def set_uploaded_file(self, project_id: str, uploaded_file: UploadedFileInfo | None) -> ProjectSession | None:
        project = self.get(project_id)
        if project is None:
            return None
        project.uploaded_file = uploaded_file
        if uploaded_file is None:
            project.extracted_text = None
        project.current_step = StepKey.upload
        return self.touch(project_id)

    def set_extracted_text(
        self,
        project_id: str,
        uploaded_file: UploadedFileInfo,
        extracted_text: ExtractedTextInfo,
    ) -> ProjectSession | None:
        project = self.get(project_id)
        if project is None:
            return None
        project.uploaded_file = uploaded_file
        project.extracted_text = extracted_text
        project.current_step = StepKey.extract
        return self.touch(project_id)

    def load_demo_content(self, project_id: str) -> ProjectSession | None:
        project = self.get(project_id)
        if project is None:
            return None
        project.questions = get_demo_questions()
        project.glossary = get_demo_glossary()
        project.current_step = StepKey.extract
        return self.touch(project_id)


    def set_parsed_questions(self, project_id: str, questions: list[QuestionItem]) -> ProjectSession | None:
        project = self.get(project_id)
        if project is None:
            return None
        project.questions = questions
        project.current_step = StepKey.review
        return self.touch(project_id)

    def update_question(self, project_id: str, question_id: str, patch: QuestionPatch) -> ProjectSession | None:
        project = self.get(project_id)
        if project is None:
            return None

        for index, question in enumerate(project.questions):
            if question.id == question_id:
                update_data = patch.model_dump(exclude_unset=True)
                project.questions[index] = question.model_copy(update=update_data)
                project.current_step = StepKey.review
                return self.touch(project_id)
        return None

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
        project.current_step = StepKey.review
        return self.touch(project_id)

    def update_glossary_term(self, project_id: str, term_id: str, patch: GlossaryTermPatch) -> ProjectSession | None:
        project = self.get(project_id)
        if project is None:
            return None

        for index, term in enumerate(project.glossary):
            if term.id == term_id:
                update_data = patch.model_dump(exclude_unset=True)
                project.glossary[index] = term.model_copy(update=update_data)
                project.current_step = StepKey.glossary
                return self.touch(project_id)
        return None


project_store = InMemoryProjectStore()
