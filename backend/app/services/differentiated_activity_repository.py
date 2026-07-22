from __future__ import annotations

import sqlite3
from datetime import datetime, timezone
from pathlib import Path

from app.core.config import settings
from app.models.differentiated_activity import (
    DifferentiatedActivity,
    DifferentiatedActivityCreateRequest,
)


class DifferentiatedActivityRepository:
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
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS differentiated_activities (
                    id TEXT PRIMARY KEY,
                    owner_account_id TEXT,
                    source_project_id TEXT,
                    updated_at TEXT NOT NULL,
                    payload TEXT NOT NULL
                )
                """
            )

    def create(
        self,
        payload: DifferentiatedActivityCreateRequest,
        owner_account_id: str | None = None,
    ) -> DifferentiatedActivity:
        return self.save(
            DifferentiatedActivity(
                owner_account_id=owner_account_id,
                **payload.model_dump(),
            )
        )

    def save(self, activity: DifferentiatedActivity) -> DifferentiatedActivity:
        activity.updated_at = datetime.now(timezone.utc)
        with self._connect() as connection:
            connection.execute(
                """
                INSERT INTO differentiated_activities (
                    id, owner_account_id, source_project_id,
                    updated_at, payload
                ) VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                    owner_account_id = excluded.owner_account_id,
                    source_project_id = excluded.source_project_id,
                    updated_at = excluded.updated_at,
                    payload = excluded.payload
                """,
                (
                    activity.id,
                    activity.owner_account_id,
                    activity.source_project_id,
                    activity.updated_at.isoformat(),
                    activity.model_dump_json(),
                ),
            )
        return activity

    def list(
        self,
        *,
        owner_account_id: str | None = None,
        grade: int | None = None,
        level: str | None = None,
    ) -> list[DifferentiatedActivity]:
        with self._connect() as connection:
            rows = connection.execute(
                "SELECT payload FROM differentiated_activities ORDER BY updated_at DESC"
            ).fetchall()
        items = [
            DifferentiatedActivity.model_validate_json(row["payload"])
            for row in rows
        ]
        if owner_account_id:
            items = [item for item in items if item.owner_account_id == owner_account_id]
        if grade is not None:
            items = [item for item in items if item.grade == grade]
        if level:
            items = [item for item in items if item.level.value == level]
        return items


def get(self, activity_id: str) -> DifferentiatedActivity | None:
    with self._connect() as connection:
        row = connection.execute(
            "SELECT payload FROM differentiated_activities WHERE id = ?",
            (activity_id,),
        ).fetchone()
    if row is None:
        return None
    return DifferentiatedActivity.model_validate_json(row["payload"])

    def delete(self, activity_id: str) -> DifferentiatedActivity | None:
        with self._connect() as connection:
            row = connection.execute(
                "SELECT payload FROM differentiated_activities WHERE id = ?",
                (activity_id,),
            ).fetchone()
            if row is None:
                return None
            connection.execute(
                "DELETE FROM differentiated_activities WHERE id = ?",
                (activity_id,),
            )
        return DifferentiatedActivity.model_validate_json(row["payload"])


differentiated_activity_repository = DifferentiatedActivityRepository()
