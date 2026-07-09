from datetime import datetime, timezone

from app.models.project import ProjectMetadata, ProjectSession


class InMemoryProjectStore:
    """Tiny in-memory store for Phase 0 smoke testing.

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


project_store = InMemoryProjectStore()
