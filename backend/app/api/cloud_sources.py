from fastapi import APIRouter, HTTPException

from app.models.cloud_source import (
    CloudSourceImportRequest,
    CloudSourceImportResult,
    CloudSourceListResponse,
    CloudSourceStatus,
)
from app.models.curriculum_source import (
    AttachCurriculumSourceRequest,
    CurriculumSourceListResponse,
    RefreshCurriculumSourcesResponse,
)
from app.services.curriculum_source_refresh import (
    check_project_curriculum_sources,
    accept_project_source_update,
)
from app.services.curriculum_sources import (
    CurriculumSourceError,
    attach_curriculum_source,
    remove_curriculum_source,
)
from app.services.session_store import project_store
from app.services.google_drive import (
    GoogleDriveSourceError,
    get_google_drive_status,
    import_google_drive_file,
    list_google_drive_files,
)


router = APIRouter(prefix="/cloud-sources", tags=["cloud-sources"])


@router.get("/google-drive/status")
def google_drive_status() -> CloudSourceStatus:
    return get_google_drive_status()


@router.get("/google-drive/files")
def google_drive_files() -> CloudSourceListResponse:
    try:
        return list_google_drive_files()
    except GoogleDriveSourceError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc


@router.post("/google-drive/import")
def google_drive_import(
    request: CloudSourceImportRequest,
) -> CloudSourceImportResult:
    try:
        return import_google_drive_file(request.file_id)
    except GoogleDriveSourceError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get(
    "/projects/{project_id}/curriculum-sources",
    response_model=CurriculumSourceListResponse,
)
def list_project_curriculum_sources(
    project_id: str,
) -> CurriculumSourceListResponse:
    project = project_store.get(project_id)
    if project is None:
        raise HTTPException(
            status_code=404,
            detail="Project not found",
        )
    return CurriculumSourceListResponse(
        items=project.curriculum_sources,
    )


@router.post(
    "/projects/{project_id}/curriculum-sources/google-drive",
)
def attach_google_drive_source_to_project(
    project_id: str,
    request: AttachCurriculumSourceRequest,
):
    project = project_store.get(project_id)
    if project is None:
        raise HTTPException(
            status_code=404,
            detail="Project not found",
        )

    try:
        imported = import_google_drive_file(
            request.source_file_id
        )
        attachment = attach_curriculum_source(
            project,
            imported.source,
            grade=request.grade,
            science_domain=request.science_domain,
            semester_id=request.semester_id,
            subject_id=request.subject_id,
            unit_id=request.unit_id,
            source_document_type=request.source_document_type,
        )
        project_store.touch(project_id)
        return attachment
    except (
        GoogleDriveSourceError,
        CurriculumSourceError,
    ) as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc


@router.delete(
    "/projects/{project_id}/curriculum-sources/{attachment_id}",
)
def delete_project_curriculum_source(
    project_id: str,
    attachment_id: str,
):
    project = project_store.get(project_id)
    if project is None:
        raise HTTPException(
            status_code=404,
            detail="Project not found",
        )

    try:
        removed = remove_curriculum_source(
            project,
            attachment_id,
        )
        project_store.touch(project_id)
        return removed
    except CurriculumSourceError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        ) from exc


@router.post(
    "/projects/{project_id}/curriculum-sources/check-refresh",
    response_model=RefreshCurriculumSourcesResponse,
)
def check_curriculum_source_updates(
    project_id: str,
) -> RefreshCurriculumSourcesResponse:
    project = project_store.get(project_id)
    if project is None:
        raise HTTPException(
            status_code=404,
            detail="Project not found",
        )

    items = check_project_curriculum_sources(project)
    project_store.touch(project_id)

    return RefreshCurriculumSourcesResponse(
        items=items,
        checked_count=len(items),
        changed_count=sum(
            item.source_refresh_status == "changed"
            for item in items
        ),
        missing_count=sum(
            item.source_refresh_status == "missing"
            for item in items
        ),
        unverifiable_count=sum(
            item.source_refresh_status == "unverifiable"
            for item in items
        ),
    )


@router.post(
    "/projects/{project_id}/curriculum-sources/{attachment_id}/accept-update",
)
def accept_curriculum_source_update(
    project_id: str,
    attachment_id: str,
):
    project = project_store.get(project_id)
    if project is None:
        raise HTTPException(
            status_code=404,
            detail="Project not found",
        )

    try:
        updated = accept_project_source_update(
            project,
            attachment_id,
        )
        project_store.touch(project_id)
        return updated
    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc
