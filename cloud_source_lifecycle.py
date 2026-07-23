from __future__ import annotations

from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path

from app.models.cloud_source import (
    CloudSource,
    CloudSourceProvider,
    CloudSourceSyncStatus,
)
from app.models.cloud_source_version import (
    CloudSourceAcceptVersionResponse,
    CloudSourceProjectIntakeResponse,
    CloudSourceRefreshResponse,
    CloudSourceVersion,
    CloudSourceVersionState,
)
from app.models.project import (
    ExtractedPdfPageInfo,
    ExtractedTextInfo,
    ProjectMetadata,
    ProjectSession,
    UploadedFileInfo,
)
from app.services.cloud_source_repository import (
    CloudSourceRepository,
)
from app.services.cloud_source_version_repository import (
    CloudSourceVersionRepository,
)
from app.services.full_exam_intake import (
    build_full_exam_intake_report,
)
from app.services.onedrive_graph_adapter import (
    synchronize_onedrive_source,
)
from app.services.session_store import InMemoryProjectStore
from app.services.text_extraction import (
    TextExtractionError,
    extract_text_from_pdf_bytes,
)


class CloudSourceLifecycleError(ValueError):
    pass


def _file_details(
    path_text: str | None,
) -> tuple[str | None, int | None]:
    if not path_text:
        return None, None
    path = Path(path_text)
    if not path.is_file():
        return None, None
    content = path.read_bytes()
    return sha256(content).hexdigest(), len(content)


def _fingerprint(
    source: CloudSource,
    checksum: str | None,
    size_bytes: int | None,
) -> str:
    payload = {
        "source_id": source.id,
        "external_id": source.external_id,
        "etag": source.etag,
        "checksum": checksum,
        "size_bytes": size_bytes,
        "modified_at": (
            source.modified_at_external.isoformat()
            if source.modified_at_external
            else None
        ),
    }
    return sha256(
        json.dumps(
            payload,
            ensure_ascii=False,
            sort_keys=True,
        ).encode("utf-8")
    ).hexdigest()


def refresh_cloud_source(
    source: CloudSource,
    source_repository: CloudSourceRepository,
    version_repository: CloudSourceVersionRepository,
    *,
    download: bool = True,
    client=None,
) -> CloudSourceRefreshResponse:
    if source.provider is not CloudSourceProvider.onedrive:
        raise CloudSourceLifecycleError(
            "Version refresh is implemented for OneDrive sources only."
        )

    sync_result = synchronize_onedrive_source(
        source,
        source_repository,
        download=download,
        client=client,
    )
    source = sync_result.source
    checksum, size_bytes = _file_details(
        sync_result.local_path
    )
    fingerprint = _fingerprint(
        source,
        checksum,
        size_bytes,
    )

    accepted_version_id = source.metadata.get(
        "accepted_version_id"
    )
    state = (
        CloudSourceVersionState.accepted
        if not accepted_version_id
        else CloudSourceVersionState.detected
    )
    now = datetime.now(timezone.utc)
    candidate = CloudSourceVersion(
        source_id=source.id,
        fingerprint=fingerprint,
        state=state,
        display_name=source.display_name,
        external_id=source.external_id,
        web_url=source.web_url,
        mime_type=source.mime_type,
        etag=source.etag,
        checksum_sha256=checksum,
        size_bytes=size_bytes,
        local_path=sync_result.local_path,
        modified_at_external=source.modified_at_external,
        accepted_at=(
            now
            if state is CloudSourceVersionState.accepted
            else None
        ),
        metadata={
            key: value
            for key, value in source.metadata.items()
            if key not in {
                "local_path",
                "accepted_version_id",
                "pending_version_id",
                "latest_version_id",
            }
        },
    )
    version, created = version_repository.create_or_update(
        candidate
    )

    if not accepted_version_id:
        version = version_repository.accept(
            source.id,
            version.id,
        )
        if version.accepted_at is None:
            version.accepted_at = now
            version_repository.save(version)
        source.metadata["accepted_version_id"] = version.id
        source.metadata.pop("pending_version_id", None)
        source.sync_status = CloudSourceSyncStatus.ready
        changed = False
        message = (
            "تم حفظ النسخة الأولى واعتمادها كأساس للمصدر."
        )
    elif accepted_version_id == version.id:
        source.metadata.pop("pending_version_id", None)
        source.sync_status = CloudSourceSyncStatus.ready
        changed = False
        message = "المصدر مطابق للنسخة المعتمدة."
    else:
        source.metadata["pending_version_id"] = version.id
        source.sync_status = CloudSourceSyncStatus.changed
        changed = True
        message = (
            "تم اكتشاف نسخة جديدة وحفظها بانتظار الاعتماد."
        )

    source.metadata["latest_version_id"] = version.id
    source.metadata["version_count"] = str(
        len(version_repository.list(source.id))
    )
    source_repository.save(source)

    return CloudSourceRefreshResponse(
        source=source,
        version=version,
        changed=changed,
        duplicate=not created,
        downloaded=sync_result.downloaded,
        message=message,
    )


def accept_cloud_source_version(
    source: CloudSource,
    version: CloudSourceVersion,
    source_repository: CloudSourceRepository,
    version_repository: CloudSourceVersionRepository,
) -> CloudSourceAcceptVersionResponse:
    if version.source_id != source.id:
        raise CloudSourceLifecycleError(
            "Cloud source version does not belong to this source."
        )

    accepted = version_repository.accept(
        source.id,
        version.id,
    )
    if accepted.accepted_at is None:
        accepted.accepted_at = datetime.now(timezone.utc)
        version_repository.save(accepted)

    source.metadata["accepted_version_id"] = accepted.id
    source.metadata["latest_version_id"] = accepted.id
    source.metadata.pop("pending_version_id", None)
    if accepted.etag:
        source.metadata["accepted_etag"] = accepted.etag
    source.sync_status = CloudSourceSyncStatus.ready
    source.last_error = None
    source_repository.save(source)

    return CloudSourceAcceptVersionResponse(
        source=source,
        version=accepted,
        message="تم اعتماد النسخة الجديدة وحفظ السابقة في السجل.",
    )


def intake_cloud_source_version(
    source: CloudSource,
    version: CloudSourceVersion,
    source_repository: CloudSourceRepository,
    version_repository: CloudSourceVersionRepository,
    project_store: InMemoryProjectStore,
    *,
    target_project: ProjectSession | None = None,
    owner_account_id: str | None = None,
) -> CloudSourceProjectIntakeResponse:
    if version.source_id != source.id:
        raise CloudSourceLifecycleError(
            "Cloud source version does not belong to this source."
        )
    if version.state is not CloudSourceVersionState.accepted:
        raise CloudSourceLifecycleError(
            "Only an accepted cloud-source version can enter a project."
        )
    if not version.local_path:
        raise CloudSourceLifecycleError(
            "The accepted version must be downloaded before project intake."
        )

    local_path = Path(version.local_path)
    if not local_path.is_file():
        raise CloudSourceLifecycleError(
            "The downloaded cloud-source file is missing."
        )

    is_pdf = (
        version.mime_type == "application/pdf"
        or local_path.suffix.lower() == ".pdf"
        or version.display_name.lower().endswith(".pdf")
    )
    if not is_pdf:
        raise CloudSourceLifecycleError(
            "Project intake currently supports PDF sources only."
        )

    file_bytes = local_path.read_bytes()
    try:
        result = extract_text_from_pdf_bytes(file_bytes)
    except TextExtractionError as exc:
        raise CloudSourceLifecycleError(str(exc)) from exc

    created_project = target_project is None
    project = target_project or project_store.create(
        ProjectMetadata(
            paper_title=version.display_name,
            subject="علوم",
        ),
        owner_account_id=owner_account_id,
    )

    uploaded_file = UploadedFileInfo(
        name=version.display_name,
        size=len(file_bytes),
        type=version.mime_type or "application/pdf",
    )
    pages = [
        ExtractedPdfPageInfo(
            page_number=page.page_number,
            text=page.text,
            character_count=page.character_count,
            is_text_empty=page.is_text_empty,
        )
        for page in result.pages
    ]
    intake_report = build_full_exam_intake_report(pages)
    extracted_text = ExtractedTextInfo(
        text=result.text if result.is_text_based else "",
        preview=result.preview if result.is_text_based else "",
        page_count=result.page_count,
        character_count=(
            result.character_count
            if result.is_text_based
            else 0
        ),
        is_text_based=result.is_text_based,
        message=(
            "تم إدخال نسخة سحابية معتمدة واستخراج النص منها."
            if result.is_text_based
            else (
                "تم إدخال النسخة السحابية، لكن PDF لا يحتوي "
                "نصًا قابلًا للاستخراج وسيحتاج OCR."
            )
        ),
        pages=pages,
    )

    updated_project = project_store.set_extracted_text(
        project.id,
        uploaded_file,
        extracted_text,
        full_exam_intake_report=intake_report,
    )
    if updated_project is None:
        raise CloudSourceLifecycleError(
            "Failed to update the target project."
        )

    now = datetime.now(timezone.utc)
    version.intake_project_id = updated_project.id
    version.intake_at = now
    version_repository.save(version)

    source.source_project_id = updated_project.id
    source.metadata["intake_version_id"] = version.id
    source.metadata["intake_project_id"] = updated_project.id
    source_repository.save(source)

    return CloudSourceProjectIntakeResponse(
        source=source,
        version=version,
        project=updated_project,
        created_project=created_project,
        message=(
            "تم إنشاء مشروع جديد من النسخة السحابية."
            if created_project
            else "تم إدخال النسخة السحابية إلى المشروع الحالي."
        ),
    )
