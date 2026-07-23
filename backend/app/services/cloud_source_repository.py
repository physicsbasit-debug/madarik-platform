from __future__ import annotations
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from app.core.config import settings
from app.models.cloud_source import CloudSource, CloudSourceCreateRequest

class CloudSourceRepository:
    def __init__(self, db_path: str | Path | None = None) -> None:
        self.db_path = Path(db_path or settings.db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._ensure_schema()

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.db_path)
        connection.row_factory = sqlite3.Row
        return connection

    def _ensure_schema(self) -> None:
        with self._connect() as connection:
            connection.execute("""
                CREATE TABLE IF NOT EXISTS cloud_sources (
                    id TEXT PRIMARY KEY,
                    owner_account_id TEXT,
                    source_project_id TEXT,
                    provider TEXT NOT NULL,
                    external_id TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    payload TEXT NOT NULL,
                    UNIQUE(provider, external_id)
                )
            """)

    def create(self, payload: CloudSourceCreateRequest, owner_account_id: str | None = None) -> CloudSource:
        return self.save(CloudSource(owner_account_id=owner_account_id, **payload.model_dump()))

    def save(self, source: CloudSource) -> CloudSource:
        source.updated_at = datetime.now(timezone.utc)
        with self._connect() as connection:
            connection.execute("""
                INSERT INTO cloud_sources (
                    id, owner_account_id, source_project_id,
                    provider, external_id, updated_at, payload
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(provider, external_id)
                DO UPDATE SET
                    id = excluded.id,
                    owner_account_id = excluded.owner_account_id,
                    source_project_id = excluded.source_project_id,
                    updated_at = excluded.updated_at,
                    payload = excluded.payload
            """, (
                source.id, source.owner_account_id, source.source_project_id,
                source.provider.value, source.external_id,
                source.updated_at.isoformat(), source.model_dump_json(),
            ))
        return source

    def list(self, *, owner_account_id: str | None = None, provider: str | None = None, source_project_id: str | None = None) -> list[CloudSource]:
        with self._connect() as connection:
            rows = connection.execute("SELECT payload FROM cloud_sources ORDER BY updated_at DESC").fetchall()
        items = [CloudSource.model_validate_json(row['payload']) for row in rows]
        if owner_account_id:
            items = [item for item in items if item.owner_account_id == owner_account_id]
        if provider:
            items = [item for item in items if item.provider.value == provider]
        if source_project_id:
            items = [item for item in items if item.source_project_id == source_project_id]
        return items

    def get(self, source_id: str) -> CloudSource | None:
        with self._connect() as connection:
            row = connection.execute("SELECT payload FROM cloud_sources WHERE id = ?", (source_id,)).fetchone()
        return None if row is None else CloudSource.model_validate_json(row['payload'])

    def delete(self, source_id: str) -> CloudSource | None:
        source = self.get(source_id)
        if source is None:
            return None
        with self._connect() as connection:
            connection.execute("DELETE FROM cloud_sources WHERE id = ?", (source_id,))
        return source

cloud_source_repository = CloudSourceRepository()
