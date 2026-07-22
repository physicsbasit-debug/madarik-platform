from fastapi import APIRouter, HTTPException

from app.models.cloud_source import (
    CloudSourceImportRequest,
    CloudSourceImportResult,
    CloudSourceListResponse,
    CloudSourceStatus,
)
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
