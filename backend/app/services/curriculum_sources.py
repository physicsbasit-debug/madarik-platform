from __future__ import annotations

from app.models.cloud_source import CloudSourceFile
from app.models.project import (
    CurriculumSourceAttachment,
    ProjectSession,
)


class CurriculumSourceError(ValueError):
    pass


def attach_curriculum_source(
    project: ProjectSession,
    source: CloudSourceFile,
    *,
    grade: int,
    science_domain: str,
    semester_id: str,
    subject_id: str,
    unit_id: str | None = None,
    source_document_type: str = "other",
) -> CurriculumSourceAttachment:
    if not 1 <= grade <= 12:
        raise CurriculumSourceError(
            "الصف يجب أن يكون بين 1 و12."
        )

    duplicate = next(
        (
            item
            for item in project.curriculum_sources
            if item.provider == source.provider.value
            and item.source_file_id == source.id
            and item.checksum == source.checksum
        ),
        None,
    )
    if duplicate is not None:
        return duplicate

    attachment = CurriculumSourceAttachment(
        provider=source.provider.value,
        source_file_id=source.id,
        file_name=source.file_name,
        mime_type=source.mime_type,
        size_bytes=source.size_bytes,
        checksum=source.checksum,
        grade=grade,
        science_domain=science_domain,
        semester_id=semester_id,
        subject_id=subject_id,
        unit_id=unit_id,
        source_document_type=source_document_type,
        source_modified_at=source.modified_at,
    )
    project.curriculum_sources.append(attachment)
    return attachment


def remove_curriculum_source(
    project: ProjectSession,
    attachment_id: str,
) -> CurriculumSourceAttachment:
    attachment = next(
        (
            item
            for item in project.curriculum_sources
            if item.id == attachment_id
        ),
        None,
    )
    if attachment is None:
        raise CurriculumSourceError(
            "المصدر المرتبط غير موجود."
        )

    project.curriculum_sources = [
        item
        for item in project.curriculum_sources
        if item.id != attachment_id
    ]
    return attachment
