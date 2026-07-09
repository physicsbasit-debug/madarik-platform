from fastapi import APIRouter, HTTPException, status

from app.models.project import ProjectMetadata, ProjectSession
from app.services.session_store import project_store

router = APIRouter(prefix="/projects", tags=["projects"])


@router.post("", status_code=status.HTTP_201_CREATED)
def create_project(metadata: ProjectMetadata | None = None) -> ProjectSession:
    """Create a temporary project session for Phase 0."""

    return project_store.create(metadata)


@router.get("/{project_id}")
def get_project(project_id: str) -> ProjectSession:
    """Return a temporary project session."""

    project = project_store.get(project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


@router.delete("/{project_id}")
def delete_project(project_id: str) -> dict[str, bool]:
    """Delete the temporary project session."""

    deleted = project_store.delete(project_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Project not found")
    return {"deleted": True}
