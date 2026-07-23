from __future__ import annotations

import sqlite3
from pathlib import Path

from app.core.config import settings
from app.models.cloud_source_version import (
    CloudSourceVersion,
    CloudSourceVersionState,
)


class CloudSourceVersionRepository:
    def __init__(
        self,
        db_path: str | Path | None = None,
    ) -> None:
        self.db_path = Path(db_path or settings.db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._ensure_schema()

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.db_path)
        connection.row_factory = sqlite3.Row
        return connection

    def _ensure_schema(self) -> None:
        with self._connect() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS cloud_source_versions (
                    id TEXT PRIMARY KEY,
                    source_id TEXT NOT NULL,
                    fingerprint TEXT NOT NULL,
                    state TEXT NOT NULL,
                    detected_at TEXT NOT NULL,
                    payload TEXT NOT NULL,
                    UNIQUE(source_id, fingerprint)
                )
                """
            )
            connection.execute(
                """
                CREATE INDEX IF NOT EXISTS
                idx_cloud_source_versions_source
                ON cloud_source_versions(source_id, detected_at DESC)
                """
            )

    def save(
        self,
        version: CloudSourceVersion,
    ) -> CloudSourceVersion:
        with self._connect() as connection:
            connection.execute(
                """
                INSERT INTO cloud_source_versions (
                    id,
                    source_id,
                    fingerprint,
                    state,
                    detected_at,
                    payload
                ) VALUES (?, ?, ?, ?, ?, ?)
                ON CONFLICT(id)
                DO UPDATE SET
                    source_id = excluded.source_id,
                    fingerprint = excluded.fingerprint,
                    state = excluded.state,
                    detected_at = excluded.detected_at,
                    payload = excluded.payload
                """,
                (
                    version.id,
                    version.source_id,
                    version.fingerprint,
                    version.state.value,
                    version.detected_at.isoformat(),
                    version.model_dump_json(),
                ),
            )
        return version

    def get(
        self,
        version_id: str,
    ) -> CloudSourceVersion | None:
        with self._connect() as connection:
            row = connection.execute(
                """
                SELECT payload
                FROM cloud_source_versions
                WHERE id = ?
                """,
                (version_id,),
            ).fetchone()
        if row is None:
            return None
        return CloudSourceVersion.model_validate_json(
            row["payload"]
        )

    def get_by_fingerprint(
        self,
        source_id: str,
        fingerprint: str,
    ) -> CloudSourceVersion | None:
        with self._connect() as connection:
            row = connection.execute(
                """
                SELECT payload
                FROM cloud_source_versions
                WHERE source_id = ? AND fingerprint = ?
                """,
                (source_id, fingerprint),
            ).fetchone()
        if row is None:
            return None
        return CloudSourceVersion.model_validate_json(
            row["payload"]
        )

    def list(
        self,
        source_id: str,
    ) -> list[CloudSourceVersion]:
        with self._connect() as connection:
            rows = connection.execute(
                """
                SELECT payload
                FROM cloud_source_versions
                WHERE source_id = ?
                ORDER BY detected_at DESC
                """,
                (source_id,),
            ).fetchall()
        return [
            CloudSourceVersion.model_validate_json(row["payload"])
            for row in rows
        ]

    def create_or_update(
        self,
        version: CloudSourceVersion,
    ) -> tuple[CloudSourceVersion, bool]:
        existing = self.get_by_fingerprint(
            version.source_id,
            version.fingerprint,
        )
        if existing is None:
            return self.save(version), True

        changed = False
        if version.local_path and version.local_path != existing.local_path:
            existing.local_path = version.local_path
            changed = True
        if (
            version.checksum_sha256
            and version.checksum_sha256 != existing.checksum_sha256
        ):
            existing.checksum_sha256 = version.checksum_sha256
            changed = True
        if version.size_bytes is not None and version.size_bytes != existing.size_bytes:
            existing.size_bytes = version.size_bytes
            changed = True
        if changed:
            self.save(existing)
        return existing, False

    def accept(
        self,
        source_id: str,
        version_id: str,
    ) -> CloudSourceVersion:
        target = self.get(version_id)
        if target is None or target.source_id != source_id:
            raise ValueError("Cloud source version not found")

        for version in self.list(source_id):
            if version.id == target.id:
                version.state = CloudSourceVersionState.accepted
            elif version.state is CloudSourceVersionState.accepted:
                version.state = CloudSourceVersionState.superseded
            self.save(version)

        refreshed = self.get(target.id)
        if refreshed is None:
            raise ValueError("Cloud source version not found")
        return refreshed

    def delete_for_source(self, source_id: str) -> int:
        with self._connect() as connection:
            cursor = connection.execute(
                """
                DELETE FROM cloud_source_versions
                WHERE source_id = ?
                """,
                (source_id,),
            )
            return cursor.rowcount


cloud_source_version_repository = CloudSourceVersionRepository()
