from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum

from app.models.cloud_source import CloudSourceFile
from app.models.project import (
    CurriculumSourceAttachment,
    ProjectSession,
)
from app.services.google_drive import (
    GoogleDriveSourceError,
    list_google_drive_files,
)


class SourceRefreshState(str, Enum):
    current = "current"
    changed = "changed"
    missing = "missing"
    unverifiable = "unverifiable"


def compare_source_version(
    attachment: CurriculumSourceAttachment,
    current: CloudSourceFile | None,
) -> tuple[SourceRefreshState, str]:
    if current is None:
        return (
            SourceRefreshState.missing,
            "لم يعد الملف موجودًا داخل المجلد المسموح.",
        )

    if attachment.checksum and current.checksum:
        if attachment.checksum != current.checksum:
            return (
                SourceRefreshState.changed,
                "تغيّر محتوى الملف منذ آخر استيراد.",
            )
        return (
            SourceRefreshState.current,
            "المصدر مطابق لآخر نسخة مرتبطة.",
        )

    if (
        attachment.source_modified_at
        and current.modified_at
        and current.modified_at
        > attachment.source_modified_at
    ):
        return (
            SourceRefreshState.changed,
            "تاريخ تعديل المصدر أحدث من النسخة المرتبطة.",
        )

    if (
        attachment.source_modified_at
        and current.modified_at
        and current.modified_at
        == attachment.source_modified_at
    ):
        return (
            SourceRefreshState.current,
            "تاريخ تعديل المصدر لم يتغير.",
        )

    return (
        SourceRefreshState.unverifiable,
        "لا تتوفر بيانات كافية للتحقق من تغير المصدر.",
    )


def check_project_curriculum_sources(
    project: ProjectSession,
) -> list[CurriculumSourceAttachment]:
    try:
        listing = list_google_drive_files()
        ready = listing.status.ready
        current_by_id = {
            source.id: source
            for source in listing.files
        }
    except GoogleDriveSourceError:
        ready = False
        current_by_id = {}

    checked_at = datetime.now(timezone.utc)

    for attachment in project.curriculum_sources:
        attachment.last_checked_at = checked_at

        if attachment.provider != "google_drive":
            attachment.source_refresh_status = (
                SourceRefreshState.unverifiable.value
            )
            attachment.refresh_message = (
                "مزود المصدر غير مدعوم في هذا الفحص."
            )
            continue

        if not ready:
            attachment.source_refresh_status = (
                SourceRefreshState.unverifiable.value
            )
            attachment.refresh_message = (
                "تعذر الاتصال بالمصدر للتحقق من النسخة."
            )
            continue

        state, message = compare_source_version(
            attachment,
            current_by_id.get(
                attachment.source_file_id
            ),
        )
        attachment.source_refresh_status = state.value
        attachment.refresh_message = message

    return project.curriculum_sources
